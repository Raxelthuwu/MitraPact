import logging
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from .base import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s'
)
logging.info("Cargando configuración de PRODUCCIÓN (servidor local)...")

# =============================================================================
# VARIABLES DE ENTORNO
# Carga explícitamente .env.production desde la raíz del proyecto.
# =============================================================================
env_path = BASE_DIR / '.env.production'
if not env_path.exists():
    raise ImproperlyConfigured(
        f"No se encontró el archivo de entorno de producción en: '{env_path}'. "
        "Asegúrate de crear .env.production antes de arrancar en producción."
    )
load_dotenv(dotenv_path=env_path)
logging.info(f"Variables de entorno cargadas desde: '{env_path}'")

# =============================================================================
# DEBUG — siempre False en producción
# =============================================================================
DEBUG = False
logging.warning(f"DEBUG={DEBUG}. Trazas de error no expuestas al cliente.")

# =============================================================================
# SECRET KEY — obligatoria, no tiene fallback
# =============================================================================
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logging.critical("FALTA CRÍTICA: 'SECRET_KEY' no definida en .env.production.")
    raise ImproperlyConfigured("'SECRET_KEY' es obligatoria en producción.")
logging.info("SECRET_KEY cargada correctamente.")

# =============================================================================
# ALLOWED HOSTS
# En producción local se limita a la IP/hostname real del servidor.
# Ajusta según tu red LAN o dominio interno.
# =============================================================================
_allowed = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',')]
logging.info(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")

# =============================================================================
# BASE DE DATOS — PostgreSQL local
# sslmode=disable porque PostgreSQL local no tiene SSL por defecto.
# Si configuras SSL en tu PG local, cambia PGSSLMODE=require en .env.production.
# =============================================================================
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER',     'No definido')
db_host = os.environ.get('PGHOST',     'No definido')
db_port = os.environ.get('PGPORT',     '5432')
logging.info(f"PostgreSQL local -> {db_host}:{db_port} | BD: {db_name} | Usuario: {db_user}")

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         os.environ.get('PGDATABASE'),
        'USER':         os.environ.get('PGUSER'),
        'PASSWORD':     os.environ.get('PGPASSWORD'),
        'HOST':         os.environ.get('PGHOST', 'localhost'),
        'PORT':         os.environ.get('PGPORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            # PostgreSQL local no requiere SSL.
            # Cambia a 'require' si habilitas SSL en tu instancia local.
            'sslmode': os.environ.get('PGSSLMODE', 'disable'),
            'options': '-c search_path=gestion_eventos,estadistico_territorial,busqueda_semantica,public',
        },
    }
}
logging.info("DATABASES configurado para PostgreSQL local.")

# =============================================================================
# CHROMADB — ruta absoluta en el servidor local
# En .env.production define CHROMA_PERSIST_DIR con la ruta real del servidor.
# Si no está definida, cae al default de base.py (BASE_DIR/chroma_db).
# =============================================================================
_chroma = os.environ.get('CHROMA_PERSIST_DIR')
if _chroma:
    CHROMA_PERSIST_DIR = _chroma
    logging.info(f"ChromaDB producción: '{CHROMA_PERSIST_DIR}'")
else:
    logging.warning(
        f"CHROMA_PERSIST_DIR no definida en .env.production. "
        f"Usando directorio base: '{CHROMA_PERSIST_DIR}'"
    )

# =============================================================================
# SEGURIDAD ADICIONAL EN PRODUCCIÓN
# =============================================================================
SECURE_BROWSER_XSS_FILTER   = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS             = 'DENY'

logging.info("Configuración de PRODUCCIÓN lista.")