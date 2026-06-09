# Backend/moduloBusquedaSemantica/services/ClasificacionService.py

import json
import logging
import asyncio
import asyncpg
from django.conf import settings
from app.config.semanticManager import SemanticManager
from Backend.moduloBusquedaSemantica.models import (
    Argumento,
    ArgumentoDocumento,
    OpinionClasificada,
)
from Backend.moduloBusquedaSemantica.interfaces import IClasificacionService

logger = logging.getLogger(__name__)


class ClasificacionService(IClasificacionService):
    """
    Servicio worker de clasificación semántica de encuestas.
    Escucha el canal 'encuesta_insertada' de PostgreSQL via asyncpg
    y orquesta el procesamiento semántico automático de cada encuesta
    nueva sin intervención del usuario.
    """

    def __init__(self):
        self._conexion: asyncpg.Connection | None = None
        self._activo:   bool                      = False

    # -------------------------------------------------------------------------
    # PÚBLICOS
    # -------------------------------------------------------------------------

    async def iniciar(self) -> None:
        """
        Inicia el worker abriendo una conexión asyncpg y registrando
        el LISTEN sobre el canal 'encuesta_insertada' de PostgreSQL.
        Queda en loop indefinido procesando notificaciones hasta que
        se llame a detener().
        """
        logger.info("[ClasificacionService] Iniciando worker — conectando a PostgreSQL via asyncpg...")

        self._conexion = await asyncpg.connect(
            host     = settings.DATABASES['default']['HOST'],
            port     = settings.DATABASES['default']['PORT'],
            database = settings.DATABASES['default']['NAME'],
            user     = settings.DATABASES['default']['USER'],
            password = settings.DATABASES['default']['PASSWORD'],
        )

        await self._conexion.add_listener('encuesta_insertada', self._onNotify)
        self._activo = True

        logger.info("[ClasificacionService] LISTEN activo en canal 'encuesta_insertada'. Worker en espera...")

        # Loop que mantiene la conexión viva mientras el worker esté activo
        while self._activo:
            await asyncio.sleep(1)

    async def detener(self) -> None:
        """
        Detiene el worker cerrando la conexión asyncpg limpiamente.
        Garantiza que no queden conexiones abiertas ni procesos huérfanos.
        """
        logger.info("[ClasificacionService] Deteniendo worker...")
        self._activo = False

        if self._conexion:
            await self._conexion.remove_listener('encuesta_insertada', self._onNotify)
            await self._conexion.close()
            self._conexion = None

        logger.info("[ClasificacionService] Worker detenido y conexión cerrada.")

    # -------------------------------------------------------------------------
    # PRIVADOS
    # -------------------------------------------------------------------------

    async def _onNotify(
        self,
        conexion: asyncpg.Connection,
        pid: int,
        canal: str,
        payload: str
    ) -> None:
        """
        Callback registrado en asyncpg que se dispara con cada pg_notify.
        Deserializa el payload y delega a _procesarEncuesta.

        Args:
            conexion: Conexión asyncpg activa.
            pid:      PID del proceso PostgreSQL que emitió el notify.
            canal:    Nombre del canal — siempre 'encuesta_insertada'.
            payload:  JSON string con los datos de la encuesta.
        """
        logger.info(f"[ClasificacionService] Notify recibido en canal '{canal}' | pid: {pid}")
        try:
            datos = json.loads(payload)
            await self._procesarEncuesta(datos)
        except Exception as e:
            logger.error(f"[ClasificacionService] Error procesando notify: {e}")

    async def _procesarEncuesta(self, payload: dict) -> None:
        """
        Orquesta el flujo completo de procesamiento de una encuesta.
        Recibe el payload del pg_notify y coordina en orden:
        clasificación de opinión, extracción de argumentos y vinculación
        de documentos.

        Args:
            payload: dict con id, barrio_id, opinion_politica,
                     prob_1_cod, prob_2_cod, prob_otra.
        """
        encuestaId   = payload.get('id')
        barrioId     = payload.get('barrio_id')
        textoOpinion = payload.get('opinion_politica', '').strip()
        prob1Cod     = payload.get('prob_1_cod')
        prob2Cod     = payload.get('prob_2_cod')
        probOtra     = payload.get('prob_otra')

        logger.info(f"[ClasificacionService] Procesando encuesta_id: '{encuestaId}'")

        if not textoOpinion:
            logger.warning(f"[ClasificacionService] Encuesta '{encuestaId}' sin opinion_politica — omitiendo.")
            return

        # 1. Clasificar opinión y persistir OpinionClasificada
        opinion = await self._clasificarOpinion(encuestaId, barrioId, textoOpinion)
        opinionId = opinion['id']

        # 2. Extraer argumentos y gestionar frecuencias
        argumentos = await self._extraerArgumentos(
            opinionId,
            textoOpinion,
            prob1Cod,
            prob2Cod,
            probOtra
        )

        # 3. Vincular documentos por cada argumento procesado
        for argumento in argumentos:
            await self._vincularDocumentos(argumento['id'], argumento['texto'])

        logger.info(
            f"[ClasificacionService] Encuesta '{encuestaId}' procesada | "
            f"argumentos: {len(argumentos)}"
        )

    async def _clasificarOpinion(
            self,
            encuestaId: str,
            barrioId: str,
            textoOpinion: str
        ) -> dict:
            logger.info(f"[ClasificacionService] Clasificando opinión de encuesta_id: '{encuestaId}'")

            embedding  = SemanticManager.getEmbeddingService()
            chroma     = SemanticManager.getChromaService()
            coleccion  = chroma.getOrCreateCollection('opiniones_vec')

            # Generar vector del texto entrante
            vector = await embedding.embed(textoOpinion)

            # 1. Intentar buscar un vecino cercano en ChromaDB
            resultados = await asyncio.to_thread(
                coleccion.query,
                query_embeddings = [vector],
                n_results        = 1
            )

            tema = 'sin_clasificar'
            if resultados and resultados.get('metadatas') and resultados['metadatas'][0]:
                distancia = resultados['distances'][0][0]
                logger.info(f"[ClasificacionService] Distancia al vecino más cercano: {distancia}")
                
                # Si el vector está lo suficientemente cerca, heredamos el tema directamente
                if distancia <= settings.SEMANTIC_MATCH_THRESHOLD:
                    tema = resultados['metadatas'][0].get('tema', 'sin_clasificar')
                    logger.info(f"[ClasificacionService] Match semántico encontrado. Heredando tema: '{tema}'")

            # 2. FALLBACK HEURÍSTICO AVANZADO (DICCIONARIO ENRIQUECIDO DE ALTA COBERTURA)
            if tema == 'sin_clasificar' or tema is None:
                logger.info("[ClasificacionService] Sin coincidencia en vector DB. Aplicando diccionario semántico robusto...")
                texto_minuscula = textoOpinion.lower()
                
                # Diccionario expandido con terminología urbana, sinónimos y variaciones de quejas comunes
                diccionario_temas = {
                    'Seguridad': [
                        'robo', 'hurto', 'asalto', 'policía', 'patrulla', 'inseguridad', 'delincuencia', 'atrac', 
                        'miedo', 'alarma', 'droga', 'microtráfico', 'banda', 'vandalismo', 'violencia', 'cámaras', 
                        'caí', 'seguro', 'extorsión', 'sicariato', 'amenaza', 'pelea', 'pandilla', 'sospechoso'
                    ],
                    'Infraestructura': [
                        'calle', 'bache', 'hueco', 'pavimento', 'vía', 'carretera', 'andén', 'construcción', 
                        'puente', 'asfalto', 'obra', 'andenes', 'grieta', 'hundimiento', 'alcantarilla sin tapa', 
                        'semáforo', 'señalización', 'alumbrado', 'luminaria', 'oscuridad', 'poste', 'parque', 'plaza'
                    ],
                    'Servicios Públicos': [
                        'agua', 'luz', 'energía', 'acueducto', 'alcantarillado', 'corte', 'cotes', 'apagón', 
                        'presión', 'tubería', 'potable', 'gas', 'conectividad', 'internet', 'fibra', 'recibo', 
                        'factura', 'tarifa', 'sobrenivel', 'drenaje', 'inundación'
                    ],
                    'Salud': [
                        'hospital', 'clínica', 'médico', 'cita', 'eps', 'salud', 'medicina', 'ambulancia', 
                        'atención', 'enfermo', 'urgencias', 'puesto de salud', 'doctor', 'enfermera', 'farmacia', 
                        'medicamento', 'tratamiento', 'vacuna', 'pediatra', 'camilla'
                    ],
                    'Educación': [
                        'colegio', 'escuela', 'universidad', 'clase', 'estudio', 'profesor', 'beca', 'educación', 
                        'jardín', 'niños', 'estudiante', 'docente', 'aula', 'pupitre', 'matrícula', 'útiles', 
                        'refrigerio', 'pae', 'deserción', 'institución educativa', 'academia'
                    ],
                    'Medio Ambiente': [
                        'basura', 'limpieza', 'recolección', 'escombro', 'contaminación', 'humo', 'ruido', 'plaga', 
                        'rata', 'roedor', 'mosquito', 'dengue', 'río', 'quebrada', 'reciclaje', 'árbol', 'tala', 
                        'poda', 'mal olor', 'vertedero', 'botadero', 'canino', 'callejero'
                    ],
                    'Movilidad y Transporte': [
                        'tráfico', 'trancón', 'bus', 'transporte', 'colectivo', 'ruta', 'paradero', 'ciclovía', 
                        'ciclorruta', 'taxis', 'terminal', 'congestión', 'pasaje', 'frecuencia', 'vía colapsada', 
                        'accidente', 'choque', 'moto', 'conductor'
                    ]
                }
                
                # Evaluar cuál categoría acumula el mayor número de impactos semánticos
                conteos = {k: sum(texto_minuscula.count(palabra) for palabra in v) for k, v in diccionario_temas.items()}
                ganador = max(conteos, key=conteos.get)
                
                if conteos[ganador] > 0:
                    tema = ganador
                    logger.info(f"[ClasificacionService] Tema inferido por diccionario: '{tema}' (Impactos: {conteos[ganador]})")
                else:
                    tema = 'Otros'  # Categoría neutral para textos que no tengan ninguna palabra clave
                    logger.info("[ClasificacionService] No se detectaron palabras clave en el diccionario. Asignando categoría: 'Otros'")

            # 3. Persistir en la base de datos PostgreSQL
            opinion = await OpinionClasificada.insertar(encuestaId, barrioId, tema)

            # 4. Registrar en ChromaDB para alimentar la memoria del sistema
            # De esta forma, las próximas encuestas con redacción similar harán Match en el Bloque 1
            vectorId = f"opinion_{opinion['id']}"
            await asyncio.to_thread(
                coleccion.upsert,
                ids        = [vectorId],
                embeddings = [vector],
                documents  = [textoOpinion],
                metadatas  = [{'tema': tema, 'barrio_id': barrioId}]
            )

            logger.info(f"[ClasificacionService] Opinión indexada exitosamente con tema definitivo: '{tema}'")
            return opinion

    async def _extraerArgumentos(
        self,
        opinionId: str,
        textoOpinion: str,
        prob1Cod: int,
        prob2Cod: int,
        probOtra: str
    ) -> list[dict]:
        """
        Extrae los argumentos presentes en el texto de la opinión.
        Por cada problemática consulta 'argumentos_vec' para decidir
        si es el mismo argumento existente (incrementa frecuencia)
        o uno nuevo (inserta y hace upsert en 'argumentos_vec').

        Args:
            opinionId:    UUID de la OpinionClasificada padre.
            textoOpinion: Texto de la opinión a procesar.
            prob1Cod:     Código de la primera problemática.
            prob2Cod:     Código de la segunda problemática.
            probOtra:     Texto libre de problemática no catalogada.

        Returns:
            list[dict] con los argumentos procesados.
        """
        logger.info(f"[ClasificacionService] Extrayendo argumentos para opinion_id: '{opinionId}'")

        embedding  = SemanticManager.getEmbeddingService()
        chroma     = SemanticManager.getChromaService()
        coleccion  = chroma.getOrCreateCollection('argumentos_vec')

        # Construir lista de problemáticas a procesar
        problematicas = [c for c in [prob1Cod, prob2Cod] if c is not None]

        # Resolver prob_otra si existe
        if probOtra and probOtra.strip():
            codInferido = await self._resolverProblematica(probOtra.strip())
            if codInferido:
                problematicas.append(codInferido)

        argumentosProcesados = []

        for problematicaCod in problematicas:
            vector = await embedding.embed(textoOpinion)

            # Buscar argumentos similares filtrados por problematica_cod
            resultados = await asyncio.to_thread(
                coleccion.query,
                query_embeddings = [vector],
                n_results        = 1,
                where            = {'problematica_cod': problematicaCod}
            )

            # Siempre insertar argumento nuevo — frecuencia se gestiona manualmente desde auditoría
            argumento = await Argumento.insertar(
                opinionId       = opinionId,
                texto           = textoOpinion,
                tema            = 'sin_clasificar',
                problematicaCod = problematicaCod,
                frecuencia      = 1
            )

            # Upsert en argumentos_vec
            vectorId = f"argumento_{argumento['id']}"
            await asyncio.to_thread(
                coleccion.upsert,
                ids        = [vectorId],
                embeddings = [vector],
                documents  = [textoOpinion],
                metadatas  = [{
                    'argumento_id':    argumento['id'],
                    'problematica_cod': problematicaCod
                }]
            )
            logger.info(f"[ClasificacionService] Nuevo argumento insertado id: '{argumento['id']}'")

            argumentosProcesados.append(argumento)

        return argumentosProcesados

    async def _resolverProblematica(self, probOtra: str) -> int | None:
        """
        Resuelve el código de problemática para un texto libre no catalogado.
        Embeddea probOtra y hace query general en 'argumentos_vec' sin filtro
        para encontrar el código más cercano semánticamente.

        Args:
            probOtra: Texto libre de problemática no catalogada.

        Returns:
            int con el problematica_cod inferido, o None si no hay similitud suficiente.
        """
        logger.info(f"[ClasificacionService] Resolviendo problematica para prob_otra: '{probOtra}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        vector     = await embedding.embed(probOtra)
        resultados = await asyncio.to_thread(
            coleccion.query,
            query_embeddings = [vector],
            n_results        = 1
        )

        if resultados and resultados.get('metadatas') and resultados['metadatas'][0]:
            distancia = resultados['distances'][0][0]
            if distancia <= settings.SEMANTIC_RELATED_THRESHOLD:
                codInferido = resultados['metadatas'][0].get('problematica_cod')
                logger.info(f"[ClasificacionService] Problemática inferida: {codInferido}")
                return codInferido

        logger.warning(f"[ClasificacionService] No se pudo inferir problemática para: '{probOtra}'")
        return None

    async def _vincularDocumentos(
        self,
        argumentoId: str,
        textoArgumento: str
    ) -> list[str]:
        """
        Busca fragmentos documentales similares al argumento en 'fragmentos_vec'.
        Extrae los documento_id únicos que superen SEMANTIC_FRAGMENT_MATCH_THRESHOLD
        y los vincula via ArgumentoDocumento.insertarBatch.

        Args:
            argumentoId:    UUID del argumento a vincular.
            textoArgumento: Texto del argumento para el query semántico.

        Returns:
            list[str] con los documento_id vinculados.
        """
        logger.info(f"[ClasificacionService] Vinculando documentos para argumento_id: '{argumentoId}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        vector     = await embedding.embed(textoArgumento)
        resultados = await asyncio.to_thread(
            coleccion.query,
            query_embeddings = [vector],
            n_results        = 5
        )

        documentoIds = []

        if resultados and resultados.get('metadatas') and resultados['metadatas'][0]:
            for metadata, distancia in zip(
                resultados['metadatas'][0],
                resultados['distances'][0]
            ):
                if distancia <= settings.SEMANTIC_FRAGMENT_MATCH_THRESHOLD:
                    documentoId = metadata.get('documento_id')
                    if documentoId and documentoId not in documentoIds:
                        documentoIds.append(documentoId)

        if documentoIds:
            await ArgumentoDocumento.insertarBatch(argumentoId, documentoIds)
            logger.info(
                f"[ClasificacionService] {len(documentoIds)} documentos vinculados "
                f"al argumento_id: '{argumentoId}'"
            )
        else:
            logger.warning(
                f"[ClasificacionService] Sin documentos vinculables para "
                f"argumento_id: '{argumentoId}'"
            )

        return documentoIds