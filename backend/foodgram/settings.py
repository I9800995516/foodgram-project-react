import os

from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR.parent.parent, 'infra/.env'), verbose=True)


SECRET_KEY = os.getenv(
    "SECRET_KEY", default="p&l%385148kslhtyn^##a1)ilz@4zqj=rq&agdol^##zgl9(vs",
)


DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',

    'django_filters',
    'colorfield',
    'api',
    'recipes',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'foodgram.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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

WSGI_APPLICATION = 'foodgram.wsgi.application'


# Database

# DATABASES = {
#     'default': {
#         'ENGINE': os.getenv('DB_ENGINE', default='django.db.backends.postgresql'),
#         'NAME': os.getenv('DB_NAME', default='postgres'),
#         'USER': os.getenv('POSTGRES_USER', default='postgres'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', default='postgres'),
#         'HOST': os.getenv('DB_HOST', default='localhost'),
#         'PORT': os.getenv('DB_PORT', default=5432),
#     },
# }

DATABASES = {
   'default': {
       'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
       'NAME': str(os.environ.get('POSTGRES_DB', BASE_DIR / 'db.sqlite3')),
       'USER': os.environ.get('POSTGRES_USER'),
       'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
       'HOST': os.environ.get('DB_HOST'),
       'PORT': os.environ.get('DB_PORT'),
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

AUTHENTICATION_BACKENDS = (
   "django.contrib.auth.backends.ModelBackend",
)

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = False


AUTH_USER_MODEL = 'users.User'
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'sent_emails')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ],

}


DJOSER = {
    
    'SERIALIZERS': {
        'user_create': 'users.serializers.CustomUserCreateSerializer',
        'user': 'users.serializers.CustomUserCreateSerializer',
        'current_user': 'users.serializers.CustomUserCreateSerializer',
        'set_password': 'djoser.serializers.SetPasswordSerializer',
        'username_reset': 'djoser.email.UsernameResetEmail',
    },

    'PERMISSIONS': {
        'user': ['rest_framework.permissions.IsAuthenticatedOrReadOnly'],
        'user_list': ['rest_framework.permissions.AllowAny'],
        'token_create': ['rest_framework.permissions.AllowAny'],
        'token_destroy': ['rest_framework.permissions.IsAuthenticated'],
    },
    'HIDE_USERS': False,
    'LOGIN_FIELD': 'email',
}


TEXT_LENGTH = 15
PER_PAGE = 10
EMAIL = "I9800995516@yandex.ru"
EMAIL_LENGTH = 254
NAME_LENGTH = 150
TAG_MAX_LENGTH = 200
RECIPE_NAME_MAX_LENGTH = 200
INGREDIENT_MAX_LENGTH = 200
TAG_MAX_LENGTH = 7

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
