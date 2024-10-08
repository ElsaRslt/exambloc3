from pathlib import Path
import os
import django_heroku
import dj_database_url
import tempfile
import cloudinary
import cloudinary.uploader
import cloudinary.api




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIRS = os.path.join(BASE_DIR, 'templates')

IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!mw_y!iohn!-dkl=8-+lr25q2dk%uj-^cly6j(gy%-j28zq97u'

if IS_HEROKU_APP:
    DEBUG = False
else:
    DEBUG = True

ALLOWED_HOSTS = ['jo2024shop-e5f38238c523.herokuapp.com', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ecommerce',
    'corsheaders',
    'whitenoise.runserver_nostatic',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
        'APP_DIRS': True,
        'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            
            ],
        }
    },
]


WSGI_APPLICATION = 'ecommerce.wsgi.application'

# Database configuration

if IS_HEROKU_APP:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'oby44j31kxv7y3jq',
            'USER': 'ohxywep85xgkg8ka',
            'PASSWORD': 'hj7cpoz0jygaxihp',
            'HOST': 'b8rg15mwxwynuk9q.chr7pe7iynqr.eu-west-1.rds.amazonaws.com',
            'PORT': 3306,
            'OPTIONS': {
                'sql_mode': 'STRICT_TRANS_TABLES',
            }
        }
    }

else:

    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jo2024',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
        }
    },

}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configure static files for Heroku
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Activate Django-Heroku
django_heroku.settings(locals())

AUTH_USER_MODEL = 'ecommerce.Utilisateur'

# gestion des mails de recupérations MDP oubliés
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'joparis2024studi@gmail.com'  
EMAIL_HOST_PASSWORD = 's o v i x j x i x x d s j p d l'  
DEFAULT_FROM_EMAIL = 'joparis2024studi@gmail.com' 

LOGIN_URL = '/connexion/'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# CSRF_TRUSTED_ORIGINS = [
#     'https://jo2024shop-e5f38238c523.herokuapp.com/',
# ]


if IS_HEROKU_APP:
    SECURE_SSL_REDIRECT = True
else:
    SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True



