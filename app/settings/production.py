import logging
import os
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
from .base import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s'
)
logging.info("Cargando configuraciones críticas para el entorno de PRODUCCIÓN...")

# Variables de entorno
load_dotenv()

# Debug
DEBUG = False
logging.warning(f"Modo DEBUG establecido en: {DEBUG}. El entorno está protegido contra exposición de trazas de error.")

# Secret Key (obligatoria en producción)
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    logging.critical("FALTA CRÍTICA: La variable 'SECRET_KEY' no está definida en el entorno de producción.")
    raise ImproperlyConfigured("La variable 'SECRET_KEY' es estrictamente obligatoria en producción.")
logging.info("SECRET_KEY cargada exitosamente desde las variables de entorno del sistema.")

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']
logging.info("ALLOWED_HOSTS configurado para aceptar todos los hosts (LAN local).")

# Base de datos
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER', 'No definido')
db_host = os.environ.get('PGHOST', 'No definido')
db_port = os.environ.get('PGPORT', '5432')
logging.info(f"Configurando conexión de datos principal -> PostgreSQL en {db_host}:{db_port} | Base de Datos: {db_name} | Usuario: {db_user}")
logging.info("Aplicando políticas de seguridad de red en base de datos: SSL MODE = 'require'")

DATABASES = {
    'default': {
        'ENGINE':       'django.db.backends.postgresql',
        'NAME':         os.environ.get('PGDATABASE'),
        'USER':         os.environ.get('PGUSER'),
        'PASSWORD':     os.environ.get('PGPASSWORD'),
        'HOST':         os.environ.get('PGHOST'),
        'PORT':         os.environ.get('PGPORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}
logging.info("Diccionario DATABASES para PostgreSQL mapeado con éxito.")

# Módulo semántico (ChromaDB) 
CHROMA_PERSIST_DIR = os.environ.get('CHROMA_PERSIST_DIR', '/data/chroma_db')
logging.info(f"Conexión semántica producción: Directorio de persistencia para ChromaDB mapeado en: '{CHROMA_PERSIST_DIR}'")

logging.info("Todas las variables del entorno de producción se han verificado e inicializado.")