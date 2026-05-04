import os
import dj_database_url
from .base import *

DEBUG = False

ALLOWED_HOSTS = [os.environ['RENDER_EXTERNAL_HOSTNAME']]

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# WhiteNoise serves compressed, fingerprinted static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
