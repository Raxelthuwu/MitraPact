import logging
from sentence_transformers import SentenceTransformer

# Configuración inicial para visualizar los logs en la consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EmbeddingService:
    def __init__(self, modelName: str):
        logging.info(f"Inicializando EmbeddingService con el modelo: '{modelName}'...")
        self.model = SentenceTransformer(modelName)
        logging.info("Modelo cargado correctamente.")

    def embed(self, text: str) -> list[float]:
        logging.info(f"Generando embedding para un texto individual (Longitud: {len(text)} caracteres)...")
        embedding = self.model.encode(text).tolist()
        logging.info("Embedding individual generado con éxito.")
        return embedding

    def embedBatch(self, texts: list[str]) -> list[list[float]]:
        logging.info(f"Recibida solicitud de lote (batch) con {len(texts)} textos.")
        if not texts:
            logging.warning("El lote de textos está vacío. Retornando lista vacía.")
            return []
        
        logging.info("Procesando el lote de embeddings...")
        embeddings = self.model.encode(texts).tolist()
        logging.info(f"Lote procesado con éxito. Se generaron {len(embeddings)} embeddings.")
        return embeddings