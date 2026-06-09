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

    def __init__(self):
        self._conexion: asyncpg.Connection | None = None
        self._activo:   bool                      = False

    async def iniciar(self) -> None:
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

    async def _onNotify(
        self,
        conexion: asyncpg.Connection,
        pid: int,
        canal: str,
        payload: str
    ) -> None:
        logger.info(f"[ClasificacionService] Notify recibido en canal '{canal}' | pid: {pid}")
        try:
            datos = json.loads(payload)
            # Guardia: el trigger siempre envía un dict; si por alguna razón
            # llegara otra estructura, lo descartamos con un log claro.
            if not isinstance(datos, dict):
                logger.error(
                    f"[ClasificacionService] Payload inesperado (no es dict): {type(datos)} — {datos}"
                )
                return
            await self._procesarEncuesta(datos)
        except json.JSONDecodeError as e:
            logger.error(f"[ClasificacionService] Payload no es JSON válido: {e} — raw: {payload!r}")
        except Exception as e:
            logger.error(f"[ClasificacionService] Error procesando notify: {e}", exc_info=True)

    async def _procesarEncuesta(self, payload: dict) -> None:
        encuestaId   = payload.get('id')
        barrioId     = payload.get('barrio_id')
        textoOpinion = (payload.get('opinion_politica') or '').strip()
        prob1Cod     = payload.get('prob_1_cod')
        prob2Cod     = payload.get('prob_2_cod')
        probOtra     = payload.get('prob_otra')

        logger.info(f"[ClasificacionService] Procesando encuesta_id: '{encuestaId}'")

        if not textoOpinion:
            logger.warning(f"[ClasificacionService] Encuesta '{encuestaId}' sin opinion_politica — omitiendo.")
            return

        opinion   = await self._clasificarOpinion(encuestaId, barrioId, textoOpinion)
        opinionId = opinion['id']

        argumentos = await self._extraerArgumentos(
            opinionId, textoOpinion, prob1Cod, prob2Cod, probOtra
        )

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

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('opiniones_vec')

        vector = await embedding.embed(textoOpinion)

        # 1. Buscar vecino cercano en ChromaDB
        # FIX: coleccion.query devuelve [] cuando la colección está vacía,
        # no un dict — se protege con isinstance + try/except.
        tema = 'sin_clasificar'
        try:
            resultados = await asyncio.to_thread(
                coleccion.query,
                query_embeddings=[vector],
                n_results=1,
            )
            if (
                isinstance(resultados, dict)
                and resultados.get('metadatas')
                and resultados['metadatas'][0]
            ):
                distancia = resultados['distances'][0][0]
                logger.info(f"[ClasificacionService] Distancia al vecino más cercano: {distancia}")
                if distancia <= settings.SEMANTIC_MATCH_THRESHOLD:
                    tema = resultados['metadatas'][0][0].get('tema', 'sin_clasificar')
                    logger.info(f"[ClasificacionService] Match semántico encontrado. Heredando tema: '{tema}'")
        except Exception as e:
            logger.warning(f"[ClasificacionService] Query ChromaDB falló (colección vacía o error): {e}")

        # 2. FALLBACK — Zero-Shot
        if not tema or tema == 'sin_clasificar':
            logger.info("[ClasificacionService] Sin match vectorial. Clasificando con Zero-Shot...")
            labels = [
                'Seguridad', 'Infraestructura', 'Servicios Públicos',
                'Salud', 'Educación', 'Medio Ambiente', 'Movilidad y Transporte',
                'Empleo y Economía', 'Vivienda', 'Otros'
            ]
            try:
                tema = await embedding.clasificarTextoInteligente(textoOpinion, labels)
                logger.info(f"[ClasificacionService] Tema inferido por Zero-Shot: '{tema}'")
            except Exception as e:
                logger.error(f"[ClasificacionService] Zero-Shot falló: {e}")
                tema = 'sin_clasificar'

        # 3. Persistir en PostgreSQL
        opinion = await OpinionClasificada.insertar(encuestaId, barrioId, tema)

        # 4. Indexar en ChromaDB
        vectorId = f"opinion_{opinion['id']}"
        try:
            await asyncio.to_thread(
                coleccion.upsert,
                ids=[vectorId],
                embeddings=[vector],
                documents=[textoOpinion],
                metadatas=[{'tema': tema, 'barrio_id': str(barrioId)}],
            )
        except Exception as e:
            logger.error(f"[ClasificacionService] Error indexando en ChromaDB: {e}")

        logger.info(f"[ClasificacionService] Opinión indexada con tema: '{tema}'")
        return opinion

    async def _extraerArgumentos(
        self,
        opinionId: str,
        textoOpinion: str,
        prob1Cod: int,
        prob2Cod: int,
        probOtra: str
    ) -> list[dict]:
        logger.info(f"[ClasificacionService] Extrayendo argumentos para opinion_id: '{opinionId}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        problematicas = [c for c in [prob1Cod, prob2Cod] if c is not None]

        if probOtra and probOtra.strip():
            codInferido = await self._resolverProblematica(probOtra.strip())
            if codInferido:
                problematicas.append(codInferido)

        argumentosProcesados = []

        for problematicaCod in problematicas:
            vector = await embedding.embed(textoOpinion)

            # FIX: mismo patrón — proteger query cuando la colección está vacía
            try:
                await asyncio.to_thread(
                    coleccion.query,
                    query_embeddings=[vector],
                    n_results=1,
                    where={'problematica_cod': problematicaCod},
                )
            except Exception as e:
                logger.warning(
                    f"[ClasificacionService] Query argumentos_vec falló "
                    f"(prob={problematicaCod}): {e}"
                )

            argumento = await Argumento.insertar(
                opinionId       = opinionId,
                texto           = textoOpinion,
                tema            = 'sin_clasificar',
                problematicaCod = problematicaCod,
                frecuencia      = 1,
            )

            vectorId = f"argumento_{argumento['id']}"
            try:
                await asyncio.to_thread(
                    coleccion.upsert,
                    ids=[vectorId],
                    embeddings=[vector],
                    documents=[textoOpinion],
                    metadatas=[{
                        'argumento_id':     str(argumento['id']),
                        'problematica_cod': problematicaCod,
                    }],
                )
            except Exception as e:
                logger.error(f"[ClasificacionService] Error indexando argumento en ChromaDB: {e}")

            logger.info(f"[ClasificacionService] Nuevo argumento insertado id: '{argumento['id']}'")
            argumentosProcesados.append(argumento)

        return argumentosProcesados

    async def _resolverProblematica(self, probOtra: str) -> int | None:
        logger.info(f"[ClasificacionService] Resolviendo problematica para prob_otra: '{probOtra}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        vector = await embedding.embed(probOtra)

        # FIX: proteger query cuando la colección está vacía
        try:
            resultados = await asyncio.to_thread(
                coleccion.query,
                query_embeddings=[vector],
                n_results=1,
            )
            if (
                isinstance(resultados, dict)
                and resultados.get('metadatas')
                and resultados['metadatas'][0]
            ):
                distancia = resultados['distances'][0][0]
                if distancia <= settings.SEMANTIC_RELATED_THRESHOLD:
                    codInferido = resultados['metadatas'][0][0].get('problematica_cod')
                    logger.info(f"[ClasificacionService] Problemática inferida: {codInferido}")
                    return codInferido
        except Exception as e:
            logger.warning(f"[ClasificacionService] Query _resolverProblematica falló: {e}")

        logger.warning(f"[ClasificacionService] No se pudo inferir problemática para: '{probOtra}'")
        return None

    async def _vincularDocumentos(
        self,
        argumentoId: str,
        textoArgumento: str
    ) -> list[str]:
        logger.info(f"[ClasificacionService] Vinculando documentos para argumento_id: '{argumentoId}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        vector = await embedding.embed(textoArgumento)

        documentoIds = []

        # FIX: proteger query cuando la colección está vacía
        try:
            resultados = await asyncio.to_thread(
                coleccion.query,
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
                    if distancia <= settings.SEMANTIC_FRAGMENT_MATCH_THRESHOLD:
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