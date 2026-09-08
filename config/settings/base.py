"""Base Django settings for weatherplatform."""
import environ
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # project root

# ---------------------------------------------------------------------------
# django-environ
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# Read .env file if present (ignored in container where env vars are injected)
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# GDAL / GeoDjango Availability Detection & DLL Preloading
# ---------------------------------------------------------------------------
import ctypes
import os
import sys

HAS_GDAL = False
_DLL_DIRECTORIES = []
GDAL_LIBRARY_PATH = None
GEOS_LIBRARY_PATH = None
SPATIALITE_LIBRARY_PATH = None

if sys.platform == "win32":
    qgis_candidates = [
        r"C:\Users\yadia\AppData\Local\Programs\OSGeo4W\bin",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\OSGeo4W\bin"),
        r"C:\OSGeo4W\bin",
        r"C:\OSGeo4W64\bin",
        r"C:\Program Files\QGIS 3.2\bin",
    ]
    for q_bin in qgis_candidates:
        if os.path.exists(q_bin):
            if hasattr(os, "add_dll_directory"):
                try:
                    _DLL_DIRECTORIES.append(os.add_dll_directory(q_bin))
                except Exception:
                    pass
            os.environ["PATH"] = q_bin + ";" + os.environ.get("PATH", "")

            # Pre-load dependent DLLs into process memory on Windows before Python's
            # minimal built-in sqlite3.dll is loaded, avoiding procedure not found (WinError 127)
            for dll_name in ["sqlite3.dll", "geos_c.dll", "spatialite.dll", "mod_spatialite.dll"]:
                candidate_dll = os.path.join(q_bin, dll_name)
                if os.path.exists(candidate_dll):
                    try:
                        ctypes.CDLL(candidate_dll)
                    except Exception:
                        pass

            # Detect GDAL DLL
            for fname in os.listdir(q_bin):
                if fname.startswith("gdal") and fname.endswith(".dll"):
                    gdal_candidate = os.path.join(q_bin, fname)
                    try:
                        ctypes.CDLL(gdal_candidate)
                    except Exception:
                        pass
                    GDAL_LIBRARY_PATH = gdal_candidate
                    os.environ["GDAL_LIBRARY_PATH"] = gdal_candidate
                    break

            # Detect GEOS DLL
            geos_path = os.path.join(q_bin, "geos_c.dll")
            if os.path.exists(geos_path):
                GEOS_LIBRARY_PATH = geos_path
                os.environ["GEOS_LIBRARY_PATH"] = geos_path

            # SpatiaLite library name
            SPATIALITE_LIBRARY_PATH = "mod_spatialite"

            # GDAL and PROJ data directories
            osgeo_root = os.path.dirname(q_bin)
            gdal_data = os.path.join(osgeo_root, "apps", "gdal", "share", "gdal")
            if os.path.exists(gdal_data):
                os.environ["GDAL_DATA"] = gdal_data
            proj_lib = os.path.join(osgeo_root, "share", "proj")
            if os.path.exists(proj_lib):
                os.environ["PROJ_LIB"] = proj_lib
            break

# Verify GDAL library availability directly without circular settings import
if GDAL_LIBRARY_PATH and os.path.exists(GDAL_LIBRARY_PATH):
    try:
        ctypes.CDLL(GDAL_LIBRARY_PATH)
        HAS_GDAL = True
    except Exception:
        HAS_GDAL = False
else:
    try:
        import ctypes.util
        _lib = ctypes.util.find_library("gdal")
        if _lib:
            ctypes.CDLL(_lib)
            HAS_GDAL = True
    except Exception:
        HAS_GDAL = False

# ---------------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]
if HAS_GDAL:
    DJANGO_APPS.append("django.contrib.gis")

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "django_celery_beat",
    "django_celery_results",
]
if HAS_GDAL:
    THIRD_PARTY_APPS.append("rest_framework_gis")

LOCAL_APPS = [
    "apps.ingestion",
    "apps.weather",
    "apps.incidents",
    "apps.alerts",
    "apps.dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database (PostGIS with SpatiaLite fallback)
# ---------------------------------------------------------------------------
_db_raw = env("DATABASE_URL", default="sqlite:///db.sqlite3")

def _can_connect_postgis(url_str):
    try:
        import urllib.parse
        import socket
        parsed = urllib.parse.urlparse(url_str.replace("postgis://", "postgresql://"))
        host = parsed.hostname
        port = parsed.port or 5432
        if host == "db" and sys.platform == "win32":
            return False
        s = socket.create_connection((host, port), timeout=1)
        s.close()
        return True
    except Exception:
        return False

if HAS_GDAL and "postgis" in _db_raw and _can_connect_postgis(_db_raw):
    DATABASES = {
        "default": env.db("DATABASE_URL", engine="django.contrib.gis.db.backends.postgis")
    }
else:
    # Use GeoDjango SpatiaLite backend so PointField, PolygonField etc. work natively
    DATABASES = {
        "default": {
            "ENGINE": "django.contrib.gis.db.backends.spatialite" if HAS_GDAL else "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static and Media files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# CORS Settings
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# ---------------------------------------------------------------------------
# Cache (Redis)
# ---------------------------------------------------------------------------
REDIS_URL = env("REDIS_URL", default="redis://redis:6379/0")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "WeatherPlatform API",
    "DESCRIPTION": "REST API for the WeatherPlatform analytics and incident monitoring service.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit

# Use Django DB as result backend table
CELERY_RESULT_EXTENDED = True

# Celery beat uses Django DB scheduler (managed via django-celery-beat)
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
