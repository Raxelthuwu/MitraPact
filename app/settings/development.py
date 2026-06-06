import logging
import os
from dotenv import load_dotenv
from .base import *

# Configuración del formateador de logs para el entorno local/dev
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [Django Settings Local] %(message)s')

logging.info("Cargando configuraciones específicas para el entorno local (Development)...")

# Intentar cargar variables de entorno desde el archivo .env
env_loaded = load_dotenv()
if env_loaded:
    logging.info("Archivo '.env' detectado y cargado correctamente en las variables de entorno.")
else:
    logging.warning("No se encontró un archivo '.env' o no se pudo cargar. Se utilizarán las variables del sistema actual.")

DEBUG = True
logging.info(f"Modo DEBUG establecido en: {DEBUG}")

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
logging.info(f"Hosts permitidos (ALLOWED_HOSTS): {ALLOWED_HOSTS}")

# Extracción de variables para el log de conexiones
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER', 'No definido')
db_host = os.environ.get('PGHOST', 'No definido')
db_port = os.environ.get('PGPORT', '5432')

logging.info(f"Intentando estructurar conexión a PostgreSQL -> Servidor: {db_host}:{db_port} | Base de Datos: {db_name} | Usuario: {db_user}")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.environ['PGDATABASE'],
        'USER':     os.environ['PGUSER'],
        'PASSWORD': os.environ['PGPASSWORD'],
        'HOST':     os.environ['PGHOST'],
        'PORT':     os.environ.get('PGPORT', '5432'),
        'CONN_MAX_AGE': 600, 
        'OPTIONS': {
            'sslmode': 'require',       
        },
    }
}

logging.info("Diccionario DATABASES para PostgreSQL mapeado con éxito.")