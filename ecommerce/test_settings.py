from ecommerce.settings import *
import tempfile
import os

# Configuration spécifique pour les tests
MEDIA_ROOT = Path(__file__).resolve().parent / 'media'
MEDIA_URL = '/media/'