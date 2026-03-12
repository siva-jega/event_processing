import os

SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'TEST_SECRET_KEY')

# PostgreSQL database used to store Superset metadata
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@postgres:5432/superset'

# Redis cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
}

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Disable examples
LOAD_EXAMPLES = False

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = os.getenv('MAPBOX_API_KEY', '')