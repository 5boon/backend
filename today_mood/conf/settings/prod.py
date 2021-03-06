import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

RELEASE_VERSION = '2020.8.9'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DJANGO_ROOT = BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5boon_secret_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*', 'localhost:8000', '127.0.0.1', 'localhost', '5boon.me']

OAUTH2_CLIENT_KEY = '5boon_oauth2_client_key'

AUTH_USER_MODEL = "users.user"

# Jet admin 테마
JET_SIDE_MENU_COMPACT = True
JET_THEMES = [
    {
        'theme': '#F08B68', # theme folder name
        'color': '#F08B68', # color of the theme's button in user menu
        'title': '#F08B68' # theme title
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]

###############################################################################
#     Logging
#     https://docs.python.org/3/howto/logging.html#configuring-logging
###############################################################################
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 다른 logger 들 활성
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] [%(asctime)s] %(message)s',
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'json': {
            'format': '%(levelname)s %(asctime)s %(message)s',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join('5boon_log_path', 'access.log'),
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 100,  # 100M
            'backupCount': 10,  # 최대 10개 유지
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('INFO'),
            'propagate': False,
        },
    },
}

#########################################
#     Application definition
#########################################
INSTALLED_APPS = [
    'jet',
    'jet.dashboard',  # dashboard 기능을 사용하려면 다음을 추가

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    'rest_framework',
    'oauth2_provider',
    'corsheaders',

    'apps.users',
    'apps.moods',
    'apps.mood_groups',
]

#########################################
#                미들웨어
#########################################
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]


#########################################
#           REST FRAMEWORK
#########################################
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework.authentication.SessionAuthentication', # To keep the Browsable API
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        # 'oauth2_provider.ext.rest_framework.TokenHasReadWriteScope'
    ),
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # To keep the Browsable API
    'oauth2_provider.backends.OAuth2Backend',
)


#########################################
#                CORS
#########################################

CORS_ORIGIN_ALLOW_ALL = True

#CORS_ALLOW_CREDENTIALS = False


#########################################
#               Oauth2
#########################################
# OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS'] = 24 * 60 * 60    # 24 Hours

# OAUTH2_PROVIDER = {
#     # other OAUTH2 settings
#     'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore'
# }

# OAUTH2_PROVIDER_APPLICATION_MODEL = 'users.User'

ROOT_URLCONF = 'urls.domain'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.normpath(os.path.join(DJANGO_ROOT, 'templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'today_mood.wsgi.application'

#########################################
#           데이터 베이스 세팅
#########################################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '5boondb',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/conf.d/5boon.cnf',
            'charset': 'utf8mb4',
        },
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#########################################
#           센트리 리포팅
#########################################
sentry_sdk.init(
    dsn="sentry_channel_key",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

#########################################
#           슬랙 채널
#########################################
SLACK_CHANNEL_JOINED_USER = 'slack_channel_joined_user_key'
SLACK_CHANNEL_CREATE_MOOD = 'slack_channel_create_mood_key'


#########################################
#           Gmail SMTP
#########################################
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = '5boon_email'
EMAIL_HOST_PASSWORD = '5boon_email_pw'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


#########################################
#           기타 등등
#########################################
SNS_AUTH_USER_KEY = 'sns_auth_user_key'


#########################################
#      Time Zone and language
#########################################
USE_TZ = False
USE_I18N = True
USE_L10N = True
TIME_ZONE = 'Asia/Seoul'
LANGUAGE_CODE = 'ko-kr'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/deploy/sites/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
