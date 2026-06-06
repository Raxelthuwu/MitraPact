import logging
import os
from dotenv import load_dotenv
from .base import *

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s'
)
logging.info("Cargando configuraciones específicas para el entorno local (Development)...")

# Variables de entorno
env_loaded = load_dotenv()
if env_loaded:
    logging.info("Archivo '.env' detectado y cargado correctamente en las variables de entorno.")
else:
    logging.warning("No se encontró un archivo '.env' o no se pudo cargar. Se utilizarán las variables del sistema actual.")

# Debug
DEBUG = True
logging.info(f"Modo DEBUG establecido en: {DEBUG}")

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['*']
logging.info("ALLOWED_HOSTS configurado para aceptar todos los hosts (LAN local).")

# Base de datos
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER', 'No definido')
db_host = os.environ.get('PGHOST', 'No definido')
db_port = os.environ.get('PGPORT', '5432')
logging.info(f"Intentando estructurar conexión a PostgreSQL -> Servidor: {db_host}:{db_port} | Base de Datos: {db_name} | Usuario: {db_user}")

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
            'options': '-c search_path=gestion_eventos,estadistico_territorial,busqueda_semantica,public'       
        },
    }
}
logging.info("Diccionario DATABASES para PostgreSQL mapeado con éxito.")