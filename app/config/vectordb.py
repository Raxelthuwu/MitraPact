import logging
from semanticManager import SemanticManager

# Configuración inicial para visualizar los logs en la consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setupVectorCollections():

    # Crea o verifica las 3 colecciones vectoriales del modelo.
    # Ejecutar una vez al iniciar la aplicación.

    logging.info("[Setup] Iniciando el proceso de verificación y creación de colecciones vectoriales...")

    chroma = SemanticManager.getChromaService()

    # FRAGMENTOS_VEC fragmentos de documentos PDF indexados
    logging.info("[Setup] Configurando colección: 'fragmentos_vec'...")
    chroma.getOrCreateCollection(
        name="fragmentos_vec",
        metadata={"description": "Embeddings de fragmentos documentales"}
    )

    # OPINIONES_VEC  opiniones políticas de encuestas
    logging.info("[Setup] Configurando colección: 'opiniones_vec'...")
    chroma.getOrCreateCollection(
        name="opiniones_vec",
        metadata={"description": "Embeddings de opiniones clasificadas"}
    )

    # ARGUMENTOS_VEC argumentos identificados por problemática
    logging.info("[Setup] Configurando colección: 'argumentos_vec'...")
    chroma.getOrCreateCollection(
        name="argumentos_vec",
        metadata={"description": "Embeddings de argumentos recurrentes"}
    )

    logging.info("[Setup] Todas las colecciones han sido procesadas por el ChromaService.")
    print("Colecciones vectoriales listas.")