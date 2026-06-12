import logging
import asyncio
import re
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

    # -------------------------------------------------------------------------
    # PÚBLICOS
    # -------------------------------------------------------------------------

    async def buscarPorPalabras(
        self,
        texto: str,
        nResultados: int = 20,
        documento: str = None,
    ) -> dict:
        logger.info(f"[ConsultaSemanticaService] Búsqueda por palabras: '{texto}' | documento: '{documento}'")

        fragmentos = await Fragmento.buscarPorTextoGlobal(texto, nResultados, documento)

        logger.info(f"[ConsultaSemanticaService] {len(fragmentos)} fragmentos encontrados.")
        return {'fragmentos': fragmentos, 'total': len(fragmentos)}

    async def buscarPorLenguajeNatural(
        self,
        consulta: str,
        nResultados: int = 5
    ) -> dict:
        logger.info(f"[ConsultaSemanticaService] Búsqueda natural: '{consulta}'")

        embedding = SemanticManager.getEmbeddingService()
        chroma    = SemanticManager.getChromaService()
        coleccion = chroma.getOrCreateCollection('fragmentos_vec')

        vector    = await embedding.embed(consulta)
        nBusqueda = max(nResultados * 3, 20)

        resultados = await asyncio.to_thread(
            coleccion.query,
            query_embeddings = [vector],
            n_results        = nBusqueda,
            include          = ['distances', 'metadatas']
        )

        if not resultados or not resultados.get('ids') or not resultados['ids'][0]:
            logger.warning("[ConsultaSemanticaService] Sin resultados en ChromaDB.")
            return {'fragmentos': [], 'documentos': []}

        # Ordenar por distancia ascendente (más similar primero)
        parejas = sorted(
            zip(resultados['ids'][0], resultados['distances'][0]),
            key=lambda x: x[1]
        )

        # Recolectar párrafos de los fragmentos más cercanos
        parrafosFinales = []
        consultaTokens  = set(re.sub(r'[^\w\s]', '', consulta.lower()).split())
        _cacheDoc       = {}

        for vectorId, distancia in parejas:
            if len(parrafosFinales) >= nResultados:
                break
            if distancia > settings.SEMANTIC_RELATED_THRESHOLD:
                continue

            fragmento = await Fragmento.obtenerPorVectorIdConNombre(vectorId)
            if not fragmento:
                continue

            docId = fragmento.get('documento_id')
            if docId not in _cacheDoc:
                _cacheDoc[docId] = await Documento.obtenerPorId(docId)

            scoreVectorial = round(max(0.0, 1 - (distancia / 2)), 3)
            parrafos = self._partirEnParrafos(
                fragmento.get('contenido', ''),
                consultaTokens
            )

            if parrafos:
                mejorParrafo = parrafos[0]
                parrafosFinales.append({
                    **fragmento,
                    'contenido':      mejorParrafo['texto'],
                    'contenido_full': fragmento.get('contenido'),
                    'score':          scoreVectorial,
                    'score_lexico':   mejorParrafo['scoreLexico'],
                })
            else:
                parrafosFinales.append({
                    **fragmento,
                    'score': scoreVectorial,
                })

        # Fallback: si threshold fue muy estricto, retornar top sin filtro
        if not parrafosFinales:
            logger.warning("[ConsultaSemanticaService] Threshold estricto — fallback sin filtro.")
            for vectorId, distancia in parejas[:nResultados]:
                fragmento = await Fragmento.obtenerPorVectorIdConNombre(vectorId)
                if fragmento:
                    docId = fragmento.get('documento_id')
                    if docId not in _cacheDoc:
                        _cacheDoc[docId] = await Documento.obtenerPorId(docId)
                    score = round(max(0.0, 1 / (1 + distancia)), 3)
                    parrafos = self._partirEnParrafos(
                        fragmento.get('contenido', ''), consultaTokens
                    )
                    mejor = parrafos[0] if parrafos else None
                    parrafosFinales.append({
                        **fragmento,
                        'contenido':      mejor['texto'] if mejor else fragmento.get('contenido'),
                        'contenido_full': fragmento.get('contenido'),
                        'score':          score,
                        'documento_nombre': fragmento.get('documento_nombre', ''),
                    })

        documentos = list({
            f['documento_id']: _cacheDoc.get(f['documento_id'])
            for f in parrafosFinales
            if f.get('documento_id') and _cacheDoc.get(f['documento_id'])
        }.values())

        logger.info(
            f"[ConsultaSemanticaService] {len(parrafosFinales)} párrafos | "
            f"{len(documentos)} documentos"
        )

        return {'fragmentos': parrafosFinales, 'documentos': documentos}

    async def buscarArgumentosPorProblematica(
        self,
        problematicaCod: int,
        nResultados: int = 5
    ) -> list[dict]:
        """
        Va directo a PostgreSQL con JOIN a catalogo_problematica.
        No depende de ChromaDB para este flujo.
        """
        logger.info(
            f"[ConsultaSemanticaService] Argumentos para problematica_cod: {problematicaCod}"
        )

        argumentos = await Argumento.buscarPorProblematicaConDescripcion(problematicaCod)

        if not argumentos:
            logger.warning(
                f"[ConsultaSemanticaService] Sin argumentos para "
                f"problematica_cod: {problematicaCod}"
            )
            return []

        resultado = []
        for argumento in argumentos[:nResultados]:
            argumentoId = argumento.get('id')
            documentos  = await ArgumentoDocumento.listarDocumentosDeArgumento(argumentoId)
            resultado.append({
                **argumento,
                'documentos': documentos,
            })

        logger.info(
            f"[ConsultaSemanticaService] {len(resultado)} argumentos retornados."
        )
        return resultado

    async def actualizar_argumento(
        self,
        argumento_id: str,
        tema: str,
        problematica_cod: int
    ) -> dict:
        logger.info(
            f"[ConsultaSemanticaService] Actualizando argumento_id: {argumento_id}"
        )

        resultado = await Argumento.actualizar(
            argumentoId     = argumento_id,
            tema            = tema,
            problematicaCod = problematica_cod
        )

        if not resultado:
            raise ValueError(
                "No se encontró el argumento o no sufrió variaciones."
            )

        # Sincronizar ChromaDB
        try:
            chroma    = SemanticManager.getChromaService()
            coleccion = chroma.getOrCreateCollection('argumentos_vec')

            registro = await asyncio.to_thread(
                coleccion.get,
                where   = {'argumento_id': str(argumento_id)},
                include = ['embeddings', 'metadatas']
            )

            if registro and registro.get('ids'):
                vector_id        = registro['ids'][0]
                embedding_base   = registro['embeddings'][0]
                metadata_antigua = registro['metadatas'][0] if registro.get('metadatas') else {}

                nueva_metadata = {
                    'argumento_id':    str(argumento_id),
                    'tema':            str(tema),
                    'problematica_cod': int(problematica_cod) if problematica_cod is not None else 0,
                    'barrio_id':       str(metadata_antigua.get('barrio_id', ''))
                }

                await asyncio.to_thread(
                    coleccion.upsert,
                    ids        = [vector_id],
                    embeddings = [embedding_base],
                    metadatas  = [nueva_metadata]
                )
                logger.info(f"[ConsultaSemanticaService] ChromaDB sincronizado: {vector_id}")
            else:
                logger.warning(
                    f"[ConsultaSemanticaService] Argumento {argumento_id} "
                    "sin vector en argumentos_vec."
                )

        except Exception as e:
            logger.error(
                f"[ConsultaSemanticaService] Error ChromaDB: {e}", exc_info=True
            )

        return {
            'status':    'success',
            'mensaje':   'Argumento actualizado correctamente.',
            'argumento': resultado
        }

    # -------------------------------------------------------------------------
    # PRIVADOS
    # -------------------------------------------------------------------------

    def _partirEnParrafos(
        self,
        contenido: str,
        consultaTokens: set
    ) -> list[dict]:
        """
        Divide el contenido en párrafos y los ordena por relevancia léxica
        respecto a la consulta. Retorna lista ordenada de mayor a menor score.
        """
        if not contenido:
            return []

        parrafos_raw = re.split(
            r'\n{2,}|(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])',
            contenido.strip()
        )

        parrafos = []
        for p in parrafos_raw:
            p = p.strip()
            if len(p) < 30:
                continue

            pTokens      = set(re.sub(r'[^\w\s]', '', p.lower()).split())
            coincidencias = len(consultaTokens & pTokens)
            scoreLexico   = round(coincidencias / max(len(consultaTokens), 1), 3)

            parrafos.append({
                'texto':      p,
                'scoreLexico': scoreLexico,
            })

        return sorted(parrafos, key=lambda x: x['scoreLexico'], reverse=True)

    async def _recuperarFragmentos(self, vectorIds: list[str]) -> list[dict]:
        """Implementación requerida por la interfaz."""
        fragmentos = []
        for vectorId in vectorIds:
            fragmento = await Fragmento.obtenerPorVectorIdConNombre(vectorId)
            if fragmento:
                fragmentos.append(fragmento)
        return fragmentos

    async def _recuperarDocumentosDeFragmentos(self, fragmentos: list[dict]) -> list[dict]:
        """Implementación requerida por la interfaz."""
        documentoIds = []
        for fragmento in fragmentos:
            docId = fragmento.get('documento_id')
            if docId and docId not in documentoIds:
                documentoIds.append(docId)

        documentos = []
        for docId in documentoIds:
            doc = await Documento.obtenerPorId(docId)
            if doc:
                documentos.append(doc)
        return documentos