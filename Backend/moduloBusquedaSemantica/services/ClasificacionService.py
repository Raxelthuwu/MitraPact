# Backend/moduloBusquedaSemantica/services/ClasificacionService.py

import json
import logging
import asyncio
import asyncpg
from django.conf import settings
from django.db import connection
from asgiref.sync import sync_to_async
from app import db
from app.config.semanticManager import SemanticManager
from Backend.moduloBusquedaSemantica.models import (
    Argumento,
    ArgumentoDocumento,
    OpinionClasificada,
)
from Backend.moduloBusquedaSemantica.interfaces import IClasificacionService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Threshold por defecto si no está en settings
# ---------------------------------------------------------------------------
_MATCH_THRESHOLD    = getattr(settings, 'SEMANTIC_MATCH_THRESHOLD',    0.35)
_RELATED_THRESHOLD  = getattr(settings, 'SEMANTIC_RELATED_THRESHOLD',  0.40)
_FRAGMENT_THRESHOLD = getattr(settings, 'SEMANTIC_FRAGMENT_MATCH_THRESHOLD', 0.40)

# Labels Zero-Shot para clasificación de opiniones
_LABELS_OPINION = [
    'Seguridad', 'Infraestructura', 'Servicios Públicos',
    'Salud', 'Educación', 'Medio Ambiente', 'Movilidad y Transporte',
    'Empleo y Economía', 'Vivienda', 'Otros',
]


def _leer_catalogo_problematica():
    """Lee el catálogo de problemáticas de forma síncrona (para bootstrapping)."""
    with connection.cursor() as cur:
        cur.execute(f"SELECT codigo, descripcion FROM {db.catalogo_problematica} ORDER BY codigo")
        rows = cur.fetchall()
    return [{"codigo": r[0], "descripcion": r[1]} for r in rows]


_leer_catalogo_async = sync_to_async(_leer_catalogo_problematica, thread_sensitive=True)


def _query_chroma(coleccion, **kwargs):
    """Wrapper síncrono para coleccion.query — se usa con asyncio.to_thread."""
    return coleccion.query(**kwargs)


def _upsert_chroma(coleccion, **kwargs):
    """Wrapper síncrono para coleccion.upsert — se usa con asyncio.to_thread."""
    return coleccion.upsert(**kwargs)


class ClasificacionService(IClasificacionService):

    def __init__(self):
        self._conexion: asyncpg.Connection | None = None
        self._activo:   bool                      = False

    # -----------------------------------------------------------------------
    # Ciclo de vida del worker
    # -----------------------------------------------------------------------

    async def iniciar(self) -> None:
        logger.info("[ClasificacionService] Iniciando worker — conectando a PostgreSQL via asyncpg...")

        self._conexion = await asyncpg.connect(
            host     = settings.DATABASES['default']['HOST'],
            port     = int(settings.DATABASES['default']['PORT']),
            database = settings.DATABASES['default']['NAME'],
            user     = settings.DATABASES['default']['USER'],
            password = settings.DATABASES['default']['PASSWORD'],
            ssl      = False,
        )

        await self._conexion.add_listener('encuesta_insertada', self._onNotify)
        self._activo = True

        # Bootstrapping: indexar catálogo de problemáticas si argumentos_vec está vacío
        await self._bootstrapCatalogo()

        logger.info("[ClasificacionService] LISTEN activo en canal 'encuesta_insertada'. Worker en espera...")

        while self._activo:
            await asyncio.sleep(1)

    async def detener(self) -> None:
        logger.info("[ClasificacionService] Deteniendo worker...")
        self._activo = False

        if self._conexion:
            await self._conexion.remove_listener('encuesta_insertada', self._onNotify)
            await self._conexion.close()
            self._conexion = None

        logger.info("[ClasificacionService] Worker detenido y conexión cerrada.")

    # -----------------------------------------------------------------------
    # Bootstrapping del catálogo de problemáticas
    # -----------------------------------------------------------------------

    async def _bootstrapCatalogo(self) -> None:
        """
        Al arrancar, indexa cada problemática del catálogo en argumentos_vec
        como 'semilla' si la colección está vacía o le faltan entradas.
        Así desde la primera encuesta ya hay vecinos con qué comparar.
        Cada vez que se agregue una problemática al catálogo y se reinicie
        el worker, se indexará automáticamente.
        """
        logger.info("[ClasificacionService] Verificando bootstrapping del catálogo...")

        try:
            embedding = SemanticManager.getEmbeddingService()
            chroma    = SemanticManager.getChromaService()
            coleccion = chroma.getOrCreateCollection('argumentos_vec')

            catalogo = await _leer_catalogo_async()
            if not catalogo:
                logger.warning("[ClasificacionService] Catálogo de problemáticas vacío — sin bootstrapping.")
                return

            # Verificar cuáles semillas ya están indexadas
            ids_semilla = [f"semilla_{p['codigo']}" for p in catalogo]
            try:
                existentes = await asyncio.to_thread(
                    coleccion.get,
                    ids=ids_semilla,
                )
                ids_existentes = set(existentes.get('ids', []))
            except Exception:
                ids_existentes = set()

            pendientes = [p for p in catalogo if f"semilla_{p['codigo']}" not in ids_existentes]

            if not pendientes:
                logger.info(
                    f"[ClasificacionService] Catálogo ya indexado ({len(catalogo)} semillas). "
                    "Sin bootstrapping necesario."
                )
                return

            logger.info(
                f"[ClasificacionService] Indexando {len(pendientes)} semilla(s) nuevas del catálogo..."
            )

            for prob in pendientes:
                codigo      = prob['codigo']
                descripcion = prob['descripcion']
                vector      = await embedding.embed(descripcion)
                vectorId    = f"semilla_{codigo}"

                try:
                    await asyncio.to_thread(
                        _upsert_chroma,
                        coleccion,
                        ids=[vectorId],
                        embeddings=[vector],
                        documents=[descripcion],
                        metadatas=[{
                            'problematica_cod': codigo,
                            'es_semilla':       True,
                            'argumento_id':     '',   # semillas no tienen argumento en BD
                        }],
                    )
                    logger.info(
                        f"[ClasificacionService] Semilla indexada: cod={codigo} — '{descripcion}'"
                    )
                except Exception as e:
                    logger.error(f"[ClasificacionService] Error indexando semilla cod={codigo}: {e}")

            logger.info("[ClasificacionService] Bootstrapping completado.")

        except Exception as e:
            logger.error(f"[ClasificacionService] Error en bootstrapping: {e}", exc_info=True)

    # -----------------------------------------------------------------------
    # Listener NOTIFY
    # -----------------------------------------------------------------------

    async def _onNotify(
        self,
        conexion: asyncpg.Connection,
        pid: int,
        canal: str,
        payload: str,
    ) -> None:
        logger.info(f"[ClasificacionService] Notify recibido en canal '{canal}' | pid: {pid}")
        try:
            datos = json.loads(payload)
            if not isinstance(datos, dict):
                logger.error(
                    f"[ClasificacionService] Payload inesperado (no es dict): "
                    f"{type(datos)} — {datos}"
                )
                return
            await self._procesarEncuesta(datos)
        except json.JSONDecodeError as e:
            logger.error(
                f"[ClasificacionService] Payload no es JSON válido: {e} — raw: {payload!r}"
            )
        except Exception as e:
            logger.error(
                f"[ClasificacionService] Error procesando notify: {e}", exc_info=True
            )

    # -----------------------------------------------------------------------
    # Procesamiento de encuesta
    # -----------------------------------------------------------------------

    async def _procesarEncuesta(self, payload: dict) -> None:
        encuestaId   = payload.get('id')
        barrioId     = payload.get('barrio_id')
        textoOpinion = (payload.get('opinion_politica') or '').strip()
        prob1Cod     = payload.get('prob_1_cod')
        prob2Cod     = payload.get('prob_2_cod')
        probOtra     = payload.get('prob_otra')

        logger.info(f"[ClasificacionService] Procesando encuesta_id: '{encuestaId}'")

        if not textoOpinion:
            logger.warning(
                f"[ClasificacionService] Encuesta '{encuestaId}' sin opinion_politica — omitiendo."
            )
            return

        opinion   = await self._clasificarOpinion(encuestaId, barrioId, textoOpinion)
        opinionId = opinion['id']
        tema      = opinion['tema']          # ← tomar el tema clasificado

        argumentos = await self._extraerArgumentos(
            opinionId, textoOpinion, prob1Cod, prob2Cod, probOtra, tema
        )

        for argumento in argumentos:
            await self._vincularDocumentos(argumento['id'], argumento['texto'])

        logger.info(
            f"[ClasificacionService] Encuesta '{encuestaId}' procesada | "
            f"argumentos: {len(argumentos)}"
        )

    # -----------------------------------------------------------------------
    # Clasificar opinión
    # -----------------------------------------------------------------------

    async def _clasificarOpinion(
        self,
        encuestaId: str,
        barrioId: str,
        textoOpinion: str,
    ) -> dict:
        logger.info(
            f"[ClasificacionService] Clasificando opinión de encuesta_id: '{encuestaId}'"
        )

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('opiniones_vec')

        vector = await embedding.embed(textoOpinion)

        # 1. Buscar vecino cercano en opiniones_vec
        tema = 'sin_clasificar'
        try:
            resultados = await asyncio.to_thread(
                _query_chroma,
                coleccion,
                query_embeddings=[vector],
                n_results=1,
            )
            if (
                isinstance(resultados, dict)
                and resultados.get('metadatas')
                and resultados['metadatas'][0]
            ):
                distancia = resultados['distances'][0][0]
                logger.info(
                    f"[ClasificacionService] Distancia vecino opiniones: {distancia:.4f}"
                )
                if distancia <= _MATCH_THRESHOLD:
                    tema = resultados['metadatas'][0][0].get('tema', 'sin_clasificar')
                    logger.info(
                        f"[ClasificacionService] Match semántico — heredando tema: '{tema}'"
                    )
        except Exception as e:
            logger.warning(
                f"[ClasificacionService] Query opiniones_vec falló: {e}"
            )

        # 2. Fallback Zero-Shot
        if not tema or tema == 'sin_clasificar':
            logger.info("[ClasificacionService] Sin match vectorial — clasificando con Zero-Shot...")
            try:
                tema = await embedding.clasificarTextoInteligente(textoOpinion, _LABELS_OPINION)
                logger.info(f"[ClasificacionService] Tema Zero-Shot: '{tema}'")
            except Exception as e:
                logger.error(f"[ClasificacionService] Zero-Shot falló: {e}")
                tema = 'sin_clasificar'

        # 3. Persistir en PostgreSQL
        opinion = await OpinionClasificada.insertar(encuestaId, barrioId, tema)

        # 4. Indexar en ChromaDB
        try:
            await asyncio.to_thread(
                _upsert_chroma,
                coleccion,
                ids=[f"opinion_{opinion['id']}"],
                embeddings=[vector],
                documents=[textoOpinion],
                metadatas=[{'tema': tema, 'barrio_id': str(barrioId)}],
            )
        except Exception as e:
            logger.error(f"[ClasificacionService] Error indexando opinión en ChromaDB: {e}")

        logger.info(f"[ClasificacionService] Opinión clasificada con tema: '{tema}'")
        return opinion

    # -----------------------------------------------------------------------
    # Extraer y acumular argumentos con frecuencia semántica
    # -----------------------------------------------------------------------

    async def _extraerArgumentos(
        self,
        opinionId: str,
        textoOpinion: str,
        prob1Cod,
        prob2Cod,
        probOtra: str,
        tema: str = 'sin_clasificar',
    ) -> list[dict]:
        """
        Por cada problemática de la encuesta:
          1. Embeds el texto de la opinión.
          2. Busca en argumentos_vec el argumento más cercano que comparta
             la misma problematica_cod (puede ser una semilla o un argumento real).
          3. Si el resultado tiene argumento_id real en BD → incrementa su frecuencia.
          4. Si es una semilla o no hay match → inserta nuevo argumento con frecuencia=1
             y lo indexa en ChromaDB.
        Siempre hay un ganador (el más cercano), sin importar la distancia.
        """
        logger.info(
            f"[ClasificacionService] Extrayendo argumentos para opinion_id: '{opinionId}'"
        )

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        # Construir lista de problemáticas a procesar
        problematicas = [c for c in [prob1Cod, prob2Cod] if c is not None]
        if probOtra and probOtra.strip():
            codInferido = await self._resolverProblematica(probOtra.strip())
            if codInferido:
                problematicas.append(codInferido)

        argumentosProcesados = []

        for problematicaCod in problematicas:
            vector = await embedding.embed(textoOpinion)

            argumentoExistente = None

            # Buscar el argumento más cercano para esta problemática
            try:
                resultados = await asyncio.to_thread(
                    _query_chroma,
                    coleccion,
                    query_embeddings=[vector],
                    n_results=1,
                    where={'problematica_cod': problematicaCod},
                )

                if (
                    isinstance(resultados, dict)
                    and resultados.get('metadatas')
                    and resultados['metadatas'][0]
                ):
                    meta         = resultados['metadatas'][0][0]
                    distancia    = resultados['distances'][0][0]
                    argumentoId  = meta.get('argumento_id', '')
                    esSemilla    = meta.get('es_semilla', False)

                    logger.info(
                        f"[ClasificacionService] Vecino más cercano para prob={problematicaCod}: "
                        f"distancia={distancia:.4f} | es_semilla={esSemilla} | id='{argumentoId}'"
                    )

                    # Si no es semilla y tiene argumento_id válido → incrementar frecuencia
                    if not esSemilla and argumentoId:
                        argumentoExistente = await Argumento.incrementarFrecuencia(argumentoId)
                        if argumentoExistente:
                            logger.info(
                                f"[ClasificacionService] Frecuencia incrementada — "
                                f"argumento_id='{argumentoId}' → {argumentoExistente['frecuencia']}"
                            )
                            argumentosProcesados.append(argumentoExistente)
                            continue  # No insertar nuevo

            except Exception as e:
                logger.warning(
                    f"[ClasificacionService] Query argumentos_vec falló "
                    f"(prob={problematicaCod}): {e}"
                )

            # Insertar nuevo argumento (primera vez o era semilla)
            argumento = await Argumento.insertar(
                opinionId       = opinionId,
                texto           = textoOpinion,
                tema            = tema,
                problematicaCod = problematicaCod,
                frecuencia      = 1,
            )

            # Indexar en ChromaDB (reemplaza la semilla si era el vecino más cercano)
            try:
                await asyncio.to_thread(
                    _upsert_chroma,
                    coleccion,
                    ids=[f"argumento_{argumento['id']}"],
                    embeddings=[vector],
                    documents=[textoOpinion],
                    metadatas=[{
                        'argumento_id':     str(argumento['id']),
                        'problematica_cod': problematicaCod,
                        'es_semilla':       False,
                        'tema':             tema,
                    }],
                )
            except Exception as e:
                logger.error(
                    f"[ClasificacionService] Error indexando argumento en ChromaDB: {e}"
                )

            logger.info(
                f"[ClasificacionService] Nuevo argumento insertado id: '{argumento['id']}'"
            )
            argumentosProcesados.append(argumento)

        return argumentosProcesados

    # -----------------------------------------------------------------------
    # Resolver prob_otra con similitud semántica
    # -----------------------------------------------------------------------

    async def _resolverProblematica(self, probOtra: str) -> int | None:
        logger.info(
            f"[ClasificacionService] Resolviendo prob_otra: '{probOtra}'"
        )

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        vector = await embedding.embed(probOtra)

        try:
            resultados = await asyncio.to_thread(
                _query_chroma,
                coleccion,
                query_embeddings=[vector],
                n_results=1,
            )
            if (
                isinstance(resultados, dict)
                and resultados.get('metadatas')
                and resultados['metadatas'][0]
            ):
                distancia   = resultados['distances'][0][0]
                codInferido = resultados['metadatas'][0][0].get('problematica_cod')
                logger.info(
                    f"[ClasificacionService] prob_otra match: cod={codInferido} "
                    f"distancia={distancia:.4f}"
                )
                # Para prob_otra siempre tomamos el más cercano (sin threshold duro)
                if codInferido:
                    return codInferido
        except Exception as e:
            logger.warning(f"[ClasificacionService] Query _resolverProblematica falló: {e}")

        logger.warning(
            f"[ClasificacionService] No se pudo inferir problemática para: '{probOtra}'"
        )
        return None

    # -----------------------------------------------------------------------
    # Vincular documentos al argumento
    # -----------------------------------------------------------------------

    async def _vincularDocumentos(
        self,
        argumentoId: str,
        textoArgumento: str,
    ) -> list[str]:
        logger.info(
            f"[ClasificacionService] Vinculando documentos para argumento_id: '{argumentoId}'"
        )

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        vector       = await embedding.embed(textoArgumento)
        documentoIds = []

        try:
            resultados = await asyncio.to_thread(
                _query_chroma,
                coleccion,
                query_embeddings=[vector],
                n_results=5,
            )
            if (
                isinstance(resultados, dict)
                and resultados.get('metadatas')
                and resultados['metadatas'][0]
            ):
                for metadata, distancia in zip(
                    resultados['metadatas'][0],
                    resultados['distances'][0],
                ):
                    if distancia <= _FRAGMENT_THRESHOLD:
                        documentoId = metadata.get('documento_id')
                        if documentoId and documentoId not in documentoIds:
                            documentoIds.append(documentoId)
        except Exception as e:
            logger.warning(f"[ClasificacionService] Query fragmentos_vec falló: {e}")

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