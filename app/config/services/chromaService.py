import asyncio
import logging
import chromadb


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromaService:
    def __init__(self, persistDir: str):
        logging.info(f"[ChromaService] Inicializando cliente asíncrono en: '{persistDir}'")
        self.client = chromadb.PersistentClient(path=persistDir)
        logging.info("[ChromaService] Cliente de ChromaDB conectado.")

    def getOrCreateCollection(self, name: str, metadata: dict = None):
        logging.info(f"[Colección] Obteniendo o creando colección: '{name}'")
        kwargs = {"name": name}
        if metadata:
            kwargs["metadata"] = metadata
        collection = self.client.get_or_create_collection(**kwargs)
        return collection


    # FRAGMENTOS_VEC


    async def upsertFragmento(self, fragmentoId: str, embedding: list, documentoId: str, pagina: int):
        logging.info(f"[Fragmentos] Insertando/Actualizando fragmento_id: '{fragmentoId}' para documento_id: '{documentoId}' (Pág. {pagina}) de forma asíncrona.")
        col = self.getOrCreateCollection("fragmentos_vec")
        
        # Pasamos el método síncrono .upsert a un hilo secundario
        await asyncio.to_thread(
            col.upsert,
            ids=[fragmentoId],
            embeddings=[embedding],
            documents=[""],

            metadatas=[{
                "fragmento_id": str(fragmentoId),
                "documento_id": str(documentoId),
                "pagina":       pagina
            }]
        )
        logging.info(f"[Fragmentos] Upsert asíncrono completado con éxito para fragmento_id: '{fragmentoId}'")

    async def queryFragmentos(self, queryEmbedding: list, nResults: int = 5):
        logging.info(f"[Fragmentos] Ejecutando consulta general asíncrona por similitud. n_results: {nResults}")
        col = self.getOrCreateCollection("fragmentos_vec")
        
        # Pasamos la lectura en disco a un hilo secundario
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults
        )
        logging.info(f"[Fragmentos] Consulta general asíncrona finalizada.")
        return resultados

    async def queryFragmentosPorDocumento(self, documentoId: str, queryEmbedding: list, nResults: int = 5):
        logging.info(f"[Fragmentos] Ejecutando consulta asíncrona filtrada por documento_id: '{documentoId}'. n_results: {nResults}")
        col = self.getOrCreateCollection("fragmentos_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"documento_id": documentoId}
        )
        logging.info(f"[Fragmentos] Consulta por documento finalizada.")
        return resultados

    async def deleteFragmentosByDocumento(self, documentoId: str):
        logging.info(f"[Fragmentos] Solicitud asíncrona de eliminación para todos los fragmentos del documento_id: '{documentoId}'")
        col = self.getOrCreateCollection("fragmentos_vec")
        
        # .get() accede a disco -> hilo secundario
        resultados = await asyncio.to_thread(col.get, where={"documento_id": documentoId})
        
        if resultados and resultados["ids"]:
            cantidad = len(resultados["ids"])
            logging.info(f"[Fragmentos] Se encontraron {cantidad} fragmentos asociados. Eliminando de forma asíncrona en disco...")
            # .delete() escribe en disco -> hilo secundario
            await asyncio.to_thread(col.delete, ids=resultados["ids"])
            logging.info(f"[Fragmentos] Eliminación asíncrona completada con éxito.")
        else:
            logging.warning(f"[Fragmentos] No se encontraron fragmentos para el documento_id: '{documentoId}'")




    # OPINIONES_VEC

    async def upsertOpinion(self, encuestaId: str, embedding: list, barrioId: str, inclinacionVoto: int):
        logging.info(f"[Opiniones] Insertando/Actualizando encuesta_id: '{encuestaId}' en barrio_id: '{barrioId}' de forma asíncrona.")
        col = self.getOrCreateCollection("opiniones_vec")
        
        await asyncio.to_thread(
            col.upsert,
            ids=[encuestaId],
            embeddings=[embedding],
            documents=[""],
            metadatas=[{
                "encuesta_id":      str(encuestaId),
                "barrio_id":        str(barrioId),
                "inclinacion_voto": inclinacionVoto
            }]
        )
        logging.info(f"[Opiniones] Upsert asíncrono completado con éxito para encuesta_id: '{encuestaId}'")

    async def queryOpinionesPorTema(self, queryEmbedding: list, nResults: int = 10):
        logging.info(f"[Opiniones] Buscando opiniones asíncronamente por tema (similitud). n_results: {nResults}")
        col = self.getOrCreateCollection("opiniones_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults
        )
        logging.info(f"[Opiniones] Búsqueda asíncrona por tema finalizada.")
        return resultados

    async def queryOpinionesPorBarrio(self, queryEmbedding: list, barrioId: str, nResults: int = 10):
        logging.info(f"[Opiniones] Buscando opiniones asíncronamente filtradas por barrio_id: '{barrioId}'. n_results: {nResults}")
        col = self.getOrCreateCollection("opiniones_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"barrio_id": barrioId}
        )
        logging.info(f"[Opiniones] Búsqueda por barrio finalizada.")
        return resultados


    # ARGUMENTOS_VEC


    async def upsertArgumento(self, argumentoId: str, embedding: list, tema: str, problematicaCod: int, barrioId: str):
        logging.info(f"[Argumentos] Insertando/Actualizando argumento_id: '{argumentoId}' (Tema: '{tema}', Problemática: {problematicaCod}) de forma asíncrona.")
        col = self.getOrCreateCollection("argumentos_vec")
        
        await asyncio.to_thread(
            col.upsert,
            ids=[argumentoId],
            embeddings=[embedding],
            documents=[""],
            metadatas=[{
                "argumento_id":     str(argumentoId),
                "tema":             tema,
                "problematica_cod": problematicaCod,
                "barrio_id":        str(barrioId)
            }]
        )
        logging.info(f"[Argumentos] Upsert asíncrono completado con éxito para argumento_id: '{argumentoId}'")

    async def queryArgumentosFrecuentes(self, queryEmbedding: list, tema: str, nResults: int = 10):
        logging.info(f"[Argumentos] Buscando argumentos frecuentes asíncronamente para el tema: '{tema}'. n_results: {nResults}")
        col = self.getOrCreateCollection("argumentos_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"tema": tema}
        )
        logging.info(f"[Argumentos] Búsqueda de argumentos frecuentes finalizada.")
        return resultados

    async def queryArgumentosPorProblematica(self, queryEmbedding: list, problematicaCod: int, nResults: int = 10):
        logging.info(f"[Argumentos] Buscando argumentos asíncronamente por problematica_cod: {problematicaCod}. n_results: {nResults}")
        col = self.getOrCreateCollection("argumentos_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"problematica_cod": problematicaCod}
        )
        logging.info(f"[Argumentos] Búsqueda por problemática finalizada.")
        return resultados

    async def queryArgumentosPorBarrioYProblematica(self, queryEmbedding: list, barrioId: str, problematicaCod: int, nResults: int = 5):
        logging.info(f"[Argumentos] Buscando argumentos asíncronamente con filtro compuesto ($and) -> barrio_id: '{barrioId}' AND problematica_cod: {problematicaCod}")
        col = self.getOrCreateCollection("argumentos_vec")
        
        resultados = await asyncio.to_thread(
            col.query,
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={
                "$and": [
                    {"barrio_id":        barrioId},
                    {"problematica_cod": problematicaCod}
                ]
            }
        )
        logging.info(f"[Argumentos] Búsqueda compuesta por Barrio y Problemática finalizada.")
        return resultados


    # QUERY GENÉRICO

    async def query(self, collectionName: str, queryEmbedding: list, nResults: int = 5, where: dict = None):
        logging.info(f"[Query Genérico] Solicitud asíncrona en colección: '{collectionName}' | n_results: {nResults} | Filtros: {where}")
        col = self.getOrCreateCollection(collectionName)
        params = {
            "query_embeddings": [queryEmbedding],
            "n_results":        nResults
        }
        if where:
            params["where"] = where
        
        resultados = await asyncio.to_thread(col.query, **params)
        logging.info(f"[Query Genérico] Ejecución asíncrona completada para colección: '{collectionName}'")
        return resultados