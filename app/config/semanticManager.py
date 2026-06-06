import logging
from django.conf import settings

# Configuración inicial para visualizar los logs en la consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SemanticManager:

    # Manager global para el módulo de Análisis Semántico y Consulta Documental.
    # Patrón Singleton — centraliza embeddings y ChromaDB.

    embeddingInstance = None
    chromaInstance    = None

    @classmethod
    def getEmbeddingService(cls):
        logging.info("[SemanticManager] Solicitando servicio de Embeddings...")
        if cls.embeddingInstance is None:
            logging.info(f"[SemanticManager] Instancia de EmbeddingService no encontrada. Creando nueva por primera vez con el modelo: '{settings.SENTENCE_TRANSFORMER_MODEL}'...")
            from app.config.services.embeddingService import EmbeddingService
            cls.embeddingInstance = EmbeddingService(
                modelName=settings.SENTENCE_TRANSFORMER_MODEL
            )
            logging.info("[SemanticManager] Instancia de EmbeddingService inicializada y guardada en el Singleton.")
        else:
            logging.info("[SemanticManager] Retornando instancia existente de EmbeddingService (Cached).")
        return cls.embeddingInstance

    @classmethod
    def getChromaService(cls):
        logging.info("[SemanticManager] Solicitando servicio de ChromaDB...")
        if cls.chromaInstance is None:
            logging.info(f"[SemanticManager] Instancia de ChromaService no encontrada. Creando nueva por primera vez en el directorio: '{settings.CHROMA_PERSIST_DIR}'...")
            from app.config.services.chromaService import ChromaService
            cls.chromaInstance = ChromaService(
                persistDir=str(settings.CHROMA_PERSIST_DIR)
            )
            logging.info("[SemanticManager] Instancia de ChromaService inicializada y guardada en el Singleton.")
        else:
            logging.info("[SemanticManager] Retornando instancia existente de ChromaService (Cached).")
        return cls.chromaInstance