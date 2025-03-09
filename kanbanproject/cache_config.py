from datetime import timedelta

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'RETRY_ON_TIMEOUT': True,
        },
        'KEY_PREFIX': 'kanbany',
        'TIMEOUT': 300,  # 5 minutes default timeout
    }
}

# Cache time for specific views
CACHE_MIDDLEWARE_SECONDS = 300

# Cache time for static files
STATICFILES_CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 30 days

# Session cache configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Cache version
CACHE_VERSION = 1

# Key patterns for different types of cached data
CACHE_KEYS = {
    'task_list': 'task_list_{group_id}',
    'user_profile': 'user_profile_{user_id}',
    'worker_group': 'worker_group_{group_id}',
}

# Cache timeouts for different types of data
CACHE_TIMEOUTS = {
    'task_list': timedelta(minutes=5),
    'user_profile': timedelta(hours=1),
    'worker_group': timedelta(minutes=15),
}