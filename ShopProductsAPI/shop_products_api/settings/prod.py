"""
Django production settings for shop-products-api project.

Security-focused configuration without BasicAuthentication/SessionAuthentication.
Uses token-based authentication only.
"""

import os
from .base import *  # noqa: F401, F403

DEBUG = False

# Add JWT authentication app
INSTALLED_APPS += ['rest_framework_simplejwt', 'rest_framework_simplejwt.token_blacklist']  # noqa: F405

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Production authentication - JWT only (no Basic/Session auth)
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [  # noqa: F405
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]

# JSON only in production (no browsable API)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS settings
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Refresh cookie must be secure in production
JWT_AUTH_REFRESH_COOKIE_SECURE = True

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'  # noqa: F405

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
    },
}
