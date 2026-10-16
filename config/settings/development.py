"""
Development settings and overrides for local development.
"""
from .base import *  # noqa: F403

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "support-system-dev-cache",
    }
}

# Run Celery tasks eagerly in dev if CELERY_ALWAYS_EAGER env var is True or Redis is absent
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=True)
CELERY_TASK_EAGER_PROPAGATES = True