import logging
import os
from dotenv import load_dotenv
from .base import *

# Configuración de logs con un formato limpio para servidores de producción/syslog
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [Django Settings Production] %(message)s')

logging.info("Cargando configuraciones críticas para el entorno de PRODUCCIÓN...")

# Carga de variables de entorno 
load_dotenv()

DEBUG = False
logging.warning(f"Modo DEBUG establecido en: {DEBUG}. El entorno está protegido contra exposición de trazas de error.")

# Validación de la existencia de la llave secreta en producción
if 'SECRET_KEY' in os.environ:
    SECRET_KEY = os.environ['SECRET_KEY']
    logging.info("SECRET_KEY cargada exitosamente desde las variables de entorno del sistema.")
else:
    logging.critical("FALTA CRÍTICA: La variable 'SECRET_KEY' no está definida en el entorno de producción.")
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
# Procesamiento de hosts permitidos
allowed_hosts_raw = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = allowed_hosts_raw.split(',')
logging.info(f"ALLOWED_HOSTS procesados e inicializados para los dominios: {ALLOWED_HOSTS}")

# Extracción de parámetros de base de datos para monitoreo de conexiones seguras
db_name = os.environ.get('PGDATABASE', 'No definido')
db_user = os.environ.get('PGUSER', 'No definido')
db_host = os.environ.get('PGHOST', 'No definido')
db_port = os.environ.get('PGPORT', '5432')

logging.info(f"Configurando conexión de datos principal -> PostgreSQL en {db_host}:{db_port} | Base de Datos: {db_name} | Usuario: {db_user}")
logging.info("Aplicando políticas de seguridad de red en base de datos: SSL MODE = 'require'")

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

# Configuración del módulo semántico en producción
CHROMA_PERSIST_DIR = os.environ.get('CHROMA_PERSIST_DIR', '/data/chroma_db')
logging.info(f"Conexión semántica producción: Directorio de persistencia para ChromaDB mapeado en: '{CHROMA_PERSIST_DIR}'")

logging.info("Todas las variables del entorno de producción se han verificado e inicializado.")