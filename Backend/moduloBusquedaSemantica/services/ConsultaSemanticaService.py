# Backend/moduloBusquedaSemantica/services/consultaSemanticaService.py

import logging
import asyncio
from django.conf import settings
from app.config.semanticManager import SemanticManager
from Backend.moduloBusquedaSemantica.models import (
    Fragmento,
    Documento,
    Argumento,
    ArgumentoDocumento,
)
from Backend.moduloBusquedaSemantica.interfaces import IConsultaSemanticaService

logger = logging.getLogger(__name__)


class ConsultaSemanticaService(IConsultaSemanticaService):
    """
    Servicio de consulta semántica sobre documentos y argumentos.
    Orquesta el flujo de embedding, query en ChromaDB y recuperación
    de resultados completos desde PostgreSQL para presentar al usuario.
    """

    # -------------------------------------------------------------------------
    # PÚBLICOS
    # -------------------------------------------------------------------------

    async def buscarPorLenguajeNatural(
        self,
        consulta: str,
        nResultados: int = 5
    ) -> dict:
        """
        Recibe una consulta en lenguaje natural, la embeddea y busca
        los fragmentos documentales más similares en 'fragmentos_vec'.
        Recupera los fragmentos completos y sus documentos desde PG.

        Args:
            consulta:    Texto libre de la consulta del usuario.
            nResultados: Cantidad máxima de fragmentos a retornar. Default 5.

        Returns:
            dict con 'fragmentos' y 'documentos' relacionados.
        """
        logger.info(f"[ConsultaSemanticaService] Búsqueda por lenguaje natural: '{consulta}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        vector     = await embedding.embed(consulta)
        resultados = await asyncio.to_thread(
            coleccion.query,
            query_embeddings = [vector],
            n_results        = nResultados
        )

        # Extraer vector_ids de los resultados
        vectorIds = []
        if resultados and resultados.get('ids') and resultados['ids'][0]:
            for vectorId, distancia in zip(
                resultados['ids'][0],
                resultados['distances'][0]
            ):
                if distancia >= settings.SEMANTIC_RELATED_THRESHOLD:
                    vectorIds.append(vectorId)

        if not vectorIds:
            logger.warning("[ConsultaSemanticaService] Sin resultados para la consulta.")
            return {'fragmentos': [], 'documentos': []}

        # Recuperar fragmentos completos desde PG
        fragmentos = await self._recuperarFragmentos(vectorIds)

        # Recuperar documentos únicos desde PG
        documentos = await self._recuperarDocumentosDeFragmentos(fragmentos)

        logger.info(
            f"[ConsultaSemanticaService] Resultados: "
            f"{len(fragmentos)} fragmentos | {len(documentos)} documentos"
        )

        return {
            'fragmentos': fragmentos,
            'documentos': documentos
        }

    async def buscarArgumentosPorProblematica(
        self,
        problematicaCod: int,
        nResultados: int = 5
    ) -> list[dict]:
        """
        Busca en 'argumentos_vec' los argumentos más relevantes
        para una problemática específica y recupera sus documentos
        vinculados via ArgumentoDocumento.

        Args:
            problematicaCod: Código de la problemática a consultar.
            nResultados:     Cantidad máxima de argumentos a retornar. Default 5.

        Returns:
            list[dict] con argumentos y sus documentos vinculados.
        """
        logger.info(
            f"[ConsultaSemanticaService] Buscando argumentos para "
            f"problematica_cod: {problematicaCod}"
        )

        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('argumentos_vec')

        # Obtener argumentos filtrando por problematica_cod en metadata
        resultados = await asyncio.to_thread(
            coleccion.get,
            where      = {'problematica_cod': problematicaCod},
            limit      = nResultados
        )

        argumentoIds = []
        if resultados and resultados.get('metadatas'):
            for metadata in resultados['metadatas']:
                argumentoId = metadata.get('argumento_id')
                if argumentoId and argumentoId not in argumentoIds:
                    argumentoIds.append(argumentoId)

        if not argumentoIds:
            logger.warning(
                f"[ConsultaSemanticaService] Sin argumentos para "
                f"problematica_cod: {problematicaCod}"
            )
            return []

        # Recuperar argumentos completos desde PG y vincular documentos
        resultado = []
        for argumentoId in argumentoIds:
            argumento  = await Argumento.obtenerPorId(argumentoId)
            if not argumento:
                continue

            documentos = await ArgumentoDocumento.listarDocumentosDeArgumento(argumentoId)
            resultado.append({
                **argumento,
                'documentos': documentos
            })

        logger.info(
            f"[ConsultaSemanticaService] {len(resultado)} argumentos "
            f"recuperados para problematica_cod: {problematicaCod}"
        )

        return resultado

    # -------------------------------------------------------------------------
    # PRIVADOS
    # -------------------------------------------------------------------------

    async def _recuperarFragmentos(self, vectorIds: list[str]) -> list[dict]:
        """
        Recupera los fragmentos completos desde PG dado una lista
        de vector_id retornados por ChromaDB.

        Args:
            vectorIds: Lista de vector_id de ChromaDB.

        Returns:
            list[dict] con los fragmentos completos desde PG.
        """
        logger.info(f"[ConsultaSemanticaService] Recuperando {len(vectorIds)} fragmentos desde PG.")

        fragmentos = []
        for vectorId in vectorIds:
            fragmento = await Fragmento.obtenerPorVectorId(vectorId)
            if fragmento:
                fragmentos.append(fragmento)

        return fragmentos

    async def _recuperarDocumentosDeFragmentos(
        self,
        fragmentos: list[dict]
    ) -> list[dict]:
        """
        Extrae los documento_id únicos de los fragmentos recuperados
        y obtiene los documentos completos desde PG.

        Args:
            fragmentos: Lista de fragmentos con su documento_id.

        Returns:
            list[dict] con los documentos únicos recuperados desde PG.
        """
        logger.info("[ConsultaSemanticaService] Recuperando documentos únicos desde PG.")

        documentoIds = []
        for fragmento in fragmentos:
            documentoId = fragmento.get('documento_id')
            if documentoId and documentoId not in documentoIds:
                documentoIds.append(documentoId)

        documentos = []
        for documentoId in documentoIds:
            documento = await Documento.obtenerPorId(documentoId)
            if documento:
                documentos.append(documento)

        return documentos