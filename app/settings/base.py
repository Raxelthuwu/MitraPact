import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Django Settings] %(message)s'
)
logging.info("Cargando configuración base compartida...")

# =============================================================================
# RUTAS
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent
logging.info(f"BASE_DIR: '{BASE_DIR}'")

# =============================================================================
# SEGURIDAD BASE
# Cada entorno sobreescribe SECRET_KEY y DEBUG en su propio archivo.
# Este valor solo existe para que Django no explote si se importa base.py solo.
# =============================================================================
SECRET_KEY = 'django-insecure-base-placeholder-sobreescribir-en-cada-entorno'
DEBUG = False

# =============================================================================
# APLICACIONES
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Backend.moduloEventos',
    'Backend.moduloLogin',
    'Backend.moduloBusquedaSemantica',
    'Backend.moduloEstadisticas',
]

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================================================
# SESIONES Y COOKIES
# Secure=True en ambos entornos; en desarrollo Railway también corre HTTPS.
# =============================================================================
SESSION_ENGINE       = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE    = True

# =============================================================================
# URLS Y WSGI/ASGI
# =============================================================================
ROOT_URLCONF     = 'app.urls'
WSGI_APPLICATION = 'app.wsgi.application'
ASGI_APPLICATION = 'app.asgi.application'

# =============================================================================
# TEMPLATES
# =============================================================================
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

# =============================================================================
# VALIDADORES DE CONTRASEÑA
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNACIONALIZACIÓN
# =============================================================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE     = 'America/Bogota'
USE_I18N      = True
USE_TZ        = True
logging.info(f"Regional: idioma={LANGUAGE_CODE} | zona={TIME_ZONE}")

# =============================================================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =============================================================================
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'Frontend' / 'Styles']
MEDIA_URL        = 'media/'
MEDIA_ROOT       = BASE_DIR / 'media'
logging.info("Rutas de estáticos y media enlazadas.")

# =============================================================================
# MODELO POR DEFECTO
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# MÓDULO SEMÁNTICO — ChromaDB
# Cada entorno sobreescribe CHROMA_PERSIST_DIR si necesita una ruta distinta.
# =============================================================================
CHROMA_PERSIST_DIR = BASE_DIR / 'chroma_db'
logging.info(f"ChromaDB base: '{CHROMA_PERSIST_DIR}'")

# =============================================================================
# MODELOS IA (compartidos entre entornos)
# =============================================================================
ZERO_SHOT_MODEL            = 'joeddav/xlm-roberta-large-xnli'
SENTENCE_TRANSFORMER_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'
logging.info(f"Modelos IA: zero-shot='{ZERO_SHOT_MODEL}' | embeddings='{SENTENCE_TRANSFORMER_MODEL}'")

# =============================================================================
# UMBRALES DE SIMILITUD SEMÁNTICA
# < 0.5 excelente coincidencia | < 0.8 aceptable
# =============================================================================
SEMANTIC_MATCH_THRESHOLD          = 0.25
SEMANTIC_RELATED_THRESHOLD        = 0.55
SEMANTIC_FRAGMENT_MATCH_THRESHOLD = 0.35
PARAGRAPH_MIN_LENGTH              = 40

# =============================================================================
# DIRECTORIOS DE INGESTA
# =============================================================================
DOCUMENTOS_PDF_DIR = MEDIA_ROOT / 'documentos'
CSV_IMPORT_DIR     = MEDIA_ROOT / 'csv_imports'
logging.info(f"PDFs: '{DOCUMENTOS_PDF_DIR}' | CSVs: '{CSV_IMPORT_DIR}'")

logging.info("Configuración base cargada correctamente.")