"""Local development settings for weatherplatform."""
from .base import *  # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE, env  # noqa: F401

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# django-debug-toolbar
# ---------------------------------------------------------------------------
INSTALLED_APPS += ["debug_toolbar", "django_extensions", "core.apps.CoreConfig"]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1", "::1"]

# ---------------------------------------------------------------------------
# Logging (verbose during development)
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# Celery & Cache local fallbacks
# ---------------------------------------------------------------------------
# Execute Celery tasks synchronously in local dev when Redis is not active
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Fall back to in-memory cache if local Redis is unreachable
try:
    import socket
    _s = socket.create_connection(("localhost", 6379), timeout=0.2)
    _s.close()
except Exception:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-weatherplatform-local",
        }
    }
