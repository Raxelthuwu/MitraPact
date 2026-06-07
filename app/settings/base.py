import logging
from pathlib import Path


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s')

logging.info("Cargando archivo de configuración settings.py...")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
logging.info(f"BASE_DIR detectado en el sistema: '{BASE_DIR}'")

SECRET_KEY = 'django-insecure-leat#y$cce&6tir1_1qjuno&(i8y1rs9ntkw#t8%z@a3!fdq9('

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Backend.moduloEventos',
    'Backend.moduloLogin'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'Frontend' / 'Templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app.wsgi.application'
ASGI_APPLICATION = 'app.asgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True
logging.info(f"Configuración regional establecida: Idioma={LANGUAGE_CODE} | Zona Horaria={TIME_ZONE}")

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'Frontend' / 'Styles',
]


MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
logging.info(f"Rutas de archivos estáticos y multimedia enlazadas en BASE_DIR.")

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Chromadb (módulo semántico) 
CHROMA_PERSIST_DIR = BASE_DIR / 'chroma_db'
logging.info(f"Conexión semántica: Directorio de persistencia de ChromaDB asignado en: '{CHROMA_PERSIST_DIR}'")

# Sentence Transformers 
SENTENCE_TRANSFORMER_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
logging.info(f"Modelo IA: SentenceTransformer configurado con el modelo de lenguaje: '{SENTENCE_TRANSFORMER_MODEL}'")

# PDFs subidos para indexación documental 
DOCUMENTOS_PDF_DIR = MEDIA_ROOT / 'documentos'
logging.info(f"Almacenamiento: Directorio para indexación de PDFs definido en: '{DOCUMENTOS_PDF_DIR}'")

#  CSV imports 
CSV_IMPORT_DIR = MEDIA_ROOT / 'csv_imports'
logging.info(f"Almacenamiento: Directorio para importación de archivos CSV definido en: '{CSV_IMPORT_DIR}'")

logging.info("Estructura de variables de configuración cargada correctamente.")