import logging
import chromadb

# Configuración inicial para visualizar los logs en la consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChromaService:
    def __init__(self, persistDir: str):
        logging.info(f"[ChromaService] Inicializando cliente persistente en: '{persistDir}'")
        self.client = chromadb.PersistentClient(path=persistDir)
        logging.info("[ChromaService] Cliente de ChromaDB conectado.")

    def getOrCreateCollection(self, name: str, metadata: dict = None):
        logging.info(f"[Colección] Obteniendo o creando colección: '{name}'")
        collection = self.client.get_or_create_collection(
            name=name,
            metadata=metadata or {}
        )
        return collection


    # FRAGMENTOS_VEC


    def upsertFragmento(self, fragmentoId: str, embedding: list, documentoId: str, pagina: int):
        logging.info(f"[Fragmentos] Insertando/Actualizando fragmento_id: '{fragmentoId}' para documento_id: '{documentoId}' (Pág. {pagina})")
        col = self.getOrCreateCollection("fragmentos_vec")
        col.upsert(
            ids=[fragmentoId],
            embeddings=[embedding],
            documents=[""],
            metadatas=[{
                "fragmento_id": fragmentoId,
                "documento_id": documentoId,
                "pagina":       pagina
            }]
        )
        logging.info(f"[Fragmentos] Upsert completado con éxito para fragmento_id: '{fragmentoId}'")

    def queryFragmentos(self, queryEmbedding: list, nResults: int = 5):
        logging.info(f"[Fragmentos] Ejecutando consulta general por similitud. n_results: {nResults}")
        col = self.getOrCreateCollection("fragmentos_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults
        )
        logging.info(f"[Fragmentos] Consulta general finalizada.")
        return resultados

    def queryFragmentosPorDocumento(self, documentoId: str, queryEmbedding: list, nResults: int = 5):
        logging.info(f"[Fragmentos] Ejecutando consulta filtrada por documento_id: '{documentoId}'. n_results: {nResults}")
        col = self.getOrCreateCollection("fragmentos_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"documento_id": documentoId}
        )
        logging.info(f"[Fragmentos] Consulta por documento finalizada.")
        return resultados

    def deleteFragmentosByDocumento(self, documentoId: str):
        logging.info(f"[Fragmentos] Solicitud de eliminación para todos los fragmentos del documento_id: '{documentoId}'")
        col = self.getOrCreateCollection("fragmentos_vec")
        resultados = col.get(where={"documento_id": documentoId})
        
        if resultados and resultados["ids"]:
            cantidad = len(resultados["ids"])
            logging.info(f"[Fragmentos] Se encontraron {cantidad} fragmentos asociados. Procediendo a eliminar...")
            col.delete(ids=resultados["ids"])
            logging.info(f"[Fragmentos] Eliminación completada con éxito.")
        else:
            logging.warning(f"[Fragmentos] No se encontraron fragmentos para el documento_id: '{documentoId}'")




    # OPINIONES_VEC

    def upsertOpinion(self, encuestaId: str, embedding: list, barrioId: str, inclinacionVoto: int):
        logging.info(f"[Opiniones] Insertando/Actualizando encuesta_id: '{encuestaId}' en barrio_id: '{barrioId}'")
        col = self.getOrCreateCollection("opiniones_vec")
        col.upsert(
            ids=[encuestaId],
            embeddings=[embedding],
            documents=[""],
            metadatas=[{
                "encuesta_id":      encuestaId,
                "barrio_id":        barrioId,
                "inclinacion_voto": inclinacionVoto
            }]
        )
        logging.info(f"[Opiniones] Upsert completado con éxito para encuesta_id: '{encuestaId}'")

    def queryOpinionesPorTema(self, queryEmbedding: list, nResults: int = 10):
        logging.info(f"[Opiniones] Buscando opiniones por tema (similitud). n_results: {nResults}")
        col = self.getOrCreateCollection("opiniones_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults
        )
        logging.info(f"[Opiniones] Búsqueda por tema finalizada.")
        return resultados

    def queryOpinionesPorBarrio(self, queryEmbedding: list, barrioId: str, nResults: int = 10):
        logging.info(f"[Opiniones] Buscando opiniones filtradas por barrio_id: '{barrioId}'. n_results: {nResults}")
        col = self.getOrCreateCollection("opiniones_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"barrio_id": barrioId}
        )
        logging.info(f"[Opiniones] Búsqueda por barrio finalizada.")
        return resultados


    # ARGUMENTOS_VEC


    def upsertArgumento(self, argumentoId: str, embedding: list, tema: str, problematicaCod: int, barrioId: str):
        logging.info(f"[Argumentos] Insertando/Actualizando argumento_id: '{argumentoId}' (Tema: '{tema}', Problemática: {problematicaCod})")
        col = self.getOrCreateCollection("argumentos_vec")
        col.upsert(
            ids=[argumentoId],
            embeddings=[embedding],
            documents=[""],
            metadatas=[{
                "argumento_id":     argumentoId,
                "tema":             tema,
                "problematica_cod": problematicaCod,
                "barrio_id":        barrioId
            }]
        )
        logging.info(f"[Argumentos] Upsert completado con éxito para argumento_id: '{argumentoId}'")

    def queryArgumentosFrecuentes(self, queryEmbedding: list, tema: str, nResults: int = 10):
        logging.info(f"[Argumentos] Buscando argumentos frecuentes para el tema: '{tema}'. n_results: {nResults}")
        col = self.getOrCreateCollection("argumentos_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"tema": tema}
        )
        logging.info(f"[Argumentos] Búsqueda de argumentos frecuentes finalizada.")
        return resultados

    def queryArgumentosPorProblematica(self, queryEmbedding: list, problematicaCod: int, nResults: int = 10):
        logging.info(f"[Argumentos] Buscando argumentos por problematica_cod: {problematicaCod}. n_results: {nResults}")
        col = self.getOrCreateCollection("argumentos_vec")
        resultados = col.query(
            query_embeddings=[queryEmbedding],
            n_results=nResults,
            where={"problematica_cod": problematicaCod}
        )
        logging.info(f"[Argumentos] Búsqueda por problemática finalizada.")
        return resultados

    def queryArgumentosPorBarrioYProblematica(self, queryEmbedding: list, barrioId: str, problematicaCod: int, nResults: int = 5):
        logging.info(f"[Argumentos] Buscando argumentos con filtro compuesto ($and) -> barrio_id: '{barrioId}' AND problematica_cod: {problematicaCod}")
        col = self.getOrCreateCollection("argumentos_vec")
        resultados = col.query(
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

    def query(self, collectionName: str, queryEmbedding: list, nResults: int = 5, where: dict = None):
        logging.info(f"[Query Genérico] Solicitud en colección: '{collectionName}' | n_results: {nResults} | Filtros: {where}")
        col = self.getOrCreateCollection(collectionName)
        params = {
            "query_embeddings": [queryEmbedding],
            "n_results":        nResults
        }
        if where:
            params["where"] = where
        
        resultados = col.query(**params)
        logging.info(f"[Query Genérico] Ejecución completada para colección: '{collectionName}'")
        return resultados