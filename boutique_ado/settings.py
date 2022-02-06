"""
Django settings for boutique_ado project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', '')

# SECURITY WARNING: don't run with debug turned on in production!
# Debug will only be true if there's a variable called development
# in the environment
# DEBUG = 'DEVELOPMENT' in os.environ
DEBUG = True

ALLOWED_HOSTS = ['the-boutique-ado-ms4-project.herokuapp.com', 'localhost']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # required by allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # our own apps
    'home',
    'products',
    'bag',
    'checkout',
    'profiles',

    # crispy forms - allows us to format our forms using
    # bootstrap styling
    "crispy_forms",

    # django storages
    'storages',
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

ROOT_URLCONF = 'boutique_ado.urls'

CRISPY_TEMPLATE_PACK = "bootstrap4"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # adding the route template directories
            os.path.join(BASE_DIR, "templates"),

            # adding our custom allauth directory to template dirs setting
            os.path.join(BASE_DIR, "templates", "allauth")
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',

                # Allows django & allauth to access HTTP request
                'django.template.context_processors.request', # required by allauth

                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.media',

                # Making the bag_contents function available throughout app
                'bag.contexts.bag_contents',
            ],
            "builtins": [
                # Contains all the tags we want available in
                # all of our templates by default
                "crispy_forms.templatetags.crispy_forms_tags",
                "crispy_forms.templatetags.crispy_forms_field",
            ]
        },
    },
]

# Tell django to store messages within the session
# This is often not required as it's the default but due to the use
# Of gitpod, it's required
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

AUTHENTICATION_BACKENDS = [

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',

]

SITE_ID = 1

# tells allauth that we want to allow authentication
# using either usernames or emails
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# these three make it so an email is required
# to register for the site, email verification is
# mandatory so we know users are using a real email and
# they're gonna be required to enter their email twice
# on the registration page, reducing the likeliness of typos
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True

# a minimum username length
ACCOUNT_USERNAME_MIN_LENGTH = 4

# url when logging in
LOGIN_URL = '/accounts/login/'

# url to be redirected to when logged in
LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

WSGI_APPLICATION = 'boutique_ado.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if 'DATABASES_URL' in os.environ:
    DATABASES = {
        dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# tells django where all of our static files are located
# meant to be tuple, hence being in brackets
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

MEDIA_URL = "/media/"
# tells django where all of our media files are located
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

if 'USE_AWS' in os.environ:

    # Cache control
    # This will tell the browser it's okay to cache static files
    # As they won't change very often and this will improve
    # Performance for our users
    AWS_S3_OBJECT_PARAMETERS = {
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'CacheControl': 'max-age=94608000',
    }

    # Bucket Configuration
    AWS_STORAGE_BUCKET_NAME = 'the-boutique-ado-ms4-project'
    AWS_S3_REGION_NAME = 'eu-west-1'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # Static & media files
    # For static file storage we want to use our
    # StaticStorage class
    STATICFILES_STORAGE = 'custom_storage.StaticStorage'

    # The location django should save to is a folder
    # named static
    STATICFILES_LOCATION = 'static'

    # For media file storage we want to use our
    # MediaStorage class
    DEFAULT_FILE_STORAGE = 'custom_storage.MediaStorage'

    # The location django should save to is a folder
    # named media
    MEDIAFILES_LOCATION = 'media'

    # Override static and media URLS in production
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/'

# Stripe
FREE_DELIVERY_THRESHOLD = 50
STANDARD_DELIVERY_PERCENTAGE = 10
STRIPE_CURRENCY = 'usd'
STRIPE_WH_SECRET = os.environ.get("STRIPE_WH_SECRET")

# Default email
DEFAULT_FROM_EMAIL = "boutiqueado@example.com"

# The following are env variables
# The public key is here purely for consistency
# The secret key is important to be secret as it's used to do
# everything within stripe. This includes:
# creating charges, making payments, issuing refunds & updating account info
# use set PUBLIC_SECRET_KEY <key> to set these variables in gitpod
# doing it this way is not permanent and you'd need to do it every time you
# start your workspace - this can be permanent by using the env vars
# in gitpod settings
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
