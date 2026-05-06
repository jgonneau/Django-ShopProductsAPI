"""
Django development settings for shop-products-api project.

Includes BasicAuthentication and SessionAuthentication for easy development/testing.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Add JWT apps
INSTALLED_APPS += ['rest_framework_simplejwt', 'rest_framework_simplejwt.token_blacklist']  # noqa: F405

# Development authentication classes (JWT + Basic + Session for browsable API)
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [  # noqa: F405
    'rest_framework_simplejwt.authentication.JWTAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework.authentication.SessionAuthentication',
]

# Enable browsable API in development
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
]

# CORS settings for local development (if needed)
# CORS_ALLOW_ALL_ORIGINS = True

# Cookie settings for local HTTP development
JWT_AUTH_REFRESH_COOKIE_SECURE = False

# Debug toolbar settings (optional)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']
