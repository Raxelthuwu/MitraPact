import logging
import os
from dotenv import load_dotenv
from .base import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s'
)
logging.info("Cargando configuración de DESARROLLO (Railway)...")

# =============================================================================
# VARIABLES DE ENTORNO
# En Railway las variables se inyectan directamente en el entorno del contenedor,
# por lo que load_dotenv() simplemente no encuentra archivo y no falla.
# Localmente puedes tener un .env.development para simular Railway.
# =============================================================================
env_path = BASE_DIR / '.env.development'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    logging.info(f"Archivo '.env.development' cargado desde: '{env_path}'")
else:
    logging.info("Sin .env.development local — usando variables inyectadas por Railway.")

# =============================================================================
# DEBUG
# =============================================================================
DEBUG = True
logging.info(f"DEBUG={DEBUG}")

# =============================================================================
# SECRET KEY
# En desarrollo se permite un fallback inseguro para no bloquear el arranque.
# En Railway define SECRET_KEY como variable de entorno igualmente.
# =============================================================================
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-dev-leat#y$cce&6tir1_1qjuno&(i8y1rs9ntkw#t8%z@a3!fdq9('
)
logging.info("SECRET_KEY cargada (fallback inseguro activo si no está en el entorno).")

# =============================================================================
# ALLOWED HOSTS
# Railway expone un dominio público; '*' simplifica el desarrollo.
# =============================================================================
ALLOWED_HOSTS = ['*']
logging.info("ALLOWED_HOSTS: '*' (desarrollo)")

# =============================================================================
# BASE DE DATOS — PostgreSQL en Railway
# Railway inyecta automáticamente las variables PGDATABASE, PGUSER, etc.
# cuando enlazas un plugin de PostgreSQL al servicio.
# sslmode=require porque Railway sí requiere SSL.
# =============================================================================
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER',     'No definido')
db_host = os.environ.get('PGHOST',     'No definido')
db_port = os.environ.get('PGPORT',     '5432')
logging.info(f"PostgreSQL Railway -> {db_host}:{db_port} | BD: {db_name} | Usuario: {db_user}")

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         os.environ.get('PGDATABASE'),
        'USER':         os.environ.get('PGUSER'),
        'PASSWORD':     os.environ.get('PGPASSWORD'),
        'HOST':         os.environ.get('PGHOST'),
        'PORT':         os.environ.get('PGPORT', '5432'),
        'CONN_MAX_AGE': 60,  # Más bajo que producción; Railway puede reciclar conexiones
        'OPTIONS': {
            'sslmode': 'require',
            'options': '-c search_path=gestion_eventos,estadistico_territorial,busqueda_semantica,public',
        },
    }
}
logging.info("DATABASES configurado para PostgreSQL en Railway.")

# =============================================================================
# CHROMADB — en Railway usa directorio temporal o volumen montado.
# Define CHROMA_PERSIST_DIR en las variables de Railway si necesitas persistencia.
# =============================================================================
_chroma = os.environ.get('CHROMA_PERSIST_DIR')
if _chroma:
    CHROMA_PERSIST_DIR = _chroma
    logging.info(f"ChromaDB desarrollo: '{CHROMA_PERSIST_DIR}'")
else:
    logging.warning(
        f"CHROMA_PERSIST_DIR no definida. "
        f"Usando directorio base: '{CHROMA_PERSIST_DIR}' (no persiste entre deploys en Railway)."
    )

logging.info("Configuración de DESARROLLO lista.")