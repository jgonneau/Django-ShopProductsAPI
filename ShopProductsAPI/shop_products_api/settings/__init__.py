"""
Settings module that selects the appropriate configuration based on DJANGO_ENV.

Usage:
    - Set DJANGO_ENV=dev for development (default)
    - Set DJANGO_ENV=prod for production
"""

import os

env = os.getenv('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *  # noqa: F401, F403
else:
    from .dev import *  # noqa: F401, F403
