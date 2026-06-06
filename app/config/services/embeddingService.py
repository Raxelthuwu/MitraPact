import asyncio
import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EmbeddingService:
    def __init__(self, modelName: str):
        logging.info(f"Inicializando EmbeddingService con el modelo: '{modelName}'...")
        self.model = SentenceTransformer(modelName)
        logging.info("Modelo cargado correctamente.")

    async def embed(self, text: str) -> list[float]:
        logging.info(f"Generando embedding asíncrono (Longitud: {len(text)} caracteres)...")
        # Pasamos la ejecución síncrona y pesada a un hilo para liberar el bucle de Uvicorn
        embedding = await asyncio.to_thread(self._sync_embed, text)
        logging.info("Embedding individual generado con éxito.")
        return embedding

    def _sync_embed(self, text: str) -> list[float]:
        """Método interno síncrono para el cálculo del embedding."""
        return self.model.encode(text).tolist()

    async def embedBatch(self, texts: list[str]) -> list[list[float]]:
        logging.info(f"Recibida solicitud asíncrona de lote (batch) con {len(texts)} textos.")
        if not texts:
            logging.warning("El lote de textos está vacío. Retornando lista vacía.")
            return []
        
        logging.info("Procesando el lote de embeddings en hilo secundario...")
        # Pasamos el lote pesado al hilo secundario
        embeddings = await asyncio.to_thread(self._sync_embed_batch, texts)
        logging.info(f"Lote procesado con éxito. Se generaron {len(embeddings)} embeddings.")
        return embeddings

    def _sync_embed_batch(self, texts: list[str]) -> list[list[float]]:
        #Método interno síncrono para el cálculo del lote de embeddings.
        return self.model.encode(texts).tolist()