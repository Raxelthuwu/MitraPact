import asyncio
import logging
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from django.conf import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EmbeddingService:
    def __init__(self, modelName: str):
        logging.info(f"Inicializando EmbeddingService con el modelo: '{modelName}'...")
        self.model = SentenceTransformer(modelName)
        
        logging.info("Cargando clasificador Zero-Shot inteligente...")
        self.classifier = pipeline(
            "zero-shot-classification",
            model=settings.ZERO_SHOT_MODEL
        )
        logging.info("Modelo cargado correctamente.")

    async def embed(self, text: str) -> list[float]:
        logging.info(f"Generando embedding asíncrono (Longitud: {len(text)} caracteres)...")
        embedding = await asyncio.to_thread(self._sync_embed, text)
        logging.info("Embedding individual generado con éxito.")
        return embedding

    def _sync_embed(self, text: str) -> list[float]:
        return self.model.encode(text).tolist()

    async def embedBatch(self, texts: list[str]) -> list[list[float]]:
        logging.info(f"Recibida solicitud asíncrona de lote (batch) con {len(texts)} textos.")
        if not texts:
            logging.warning("El lote de textos está vacío. Retornando lista vacía.")
            return []
        logging.info("Procesando el lote de embeddings en hilo secundario...")
        embeddings = await asyncio.to_thread(self._sync_embed_batch, texts)
        logging.info(f"Lote procesado con éxito. Se generaron {len(embeddings)} embeddings.")
        return embeddings

    def _sync_embed_batch(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts).tolist()

    async def clasificarTextoInteligente(self, text: str, labels: list[str]) -> str:
        logging.info(f"Clasificando analíticamente: '{text[:30]}...'")
        res = await asyncio.to_thread(self._sync_classify, text, labels)
        return res['labels'][0]

    def _sync_classify(self, text: str, labels: list[str]) -> dict:
        return self.classifier(text, candidate_labels=labels)