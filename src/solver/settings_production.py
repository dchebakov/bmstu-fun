from .settings import *

DEBUG = False

SECRETS_PATH_PREFIX = '/run/secrets/'


def get_secret(name):
    secret_file = open(os.path.join(SECRETS_PATH_PREFIX, name), 'r')
    secret = secret_file.read().strip()
    secret_file.close()

    return secret


SECRET_KEY = get_secret('bmstu_fun_secret_key')
ALLOWED_HOSTS = get_secret('bmstu_fun_allowed_hosts').split(',')
DB_PASSWORD = get_secret('bmstu_fun_db_password')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'bmstu_fun',
        'USER': 'admin',
        'PASSWORD': DB_PASSWORD,
        'HOST': 'db',
        'PORT': '5432',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[django] %(levelname)s %(asctime)s %(module)s %(message)s\n'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
