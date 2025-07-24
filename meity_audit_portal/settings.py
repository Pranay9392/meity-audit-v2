# Project: meity_audit_portal
# File: meity_audit_portal/settings.py
# Description: Configuration settings for the Django project, now including DRF and JWT.

import os
from pathlib import Path
from datetime import timedelta # Import timedelta for JWT settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See [https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-for-production' # Replace with a real secret key in production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',  # Register the users app
    'audit_management.apps.AuditManagementConfig', # Register the audit_management app
    'rest_framework', # Django REST Framework
    'corsheaders', # For handling Cross-Origin Resource Sharing
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS middleware must be very high, preferably before CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meity_audit_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Look for templates in a global 'templates' directory
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

WSGI_APPLICATION = 'meity_audit_portal.wsgi.application'

# Database
# Using SQLite for simplicity. For production, consider PostgreSQL, MySQL, etc.
# [https://docs.djangoproject.com/en/5.0/ref/settings/#databases](https://docs.djangoproject.com/en/5.0/howto/databases/)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# [https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators](https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators)

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
# [https://docs.djangoproject.com/en/5.0/topics/i18n/](https://docs.djangoproject.com/en/5.0/topics/i18n/)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata' # Set to India's timezone

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# [https://docs.djangoproject.com/en/5.0/howto/static-files/](https://docs.djangoproject.com/en/5.0/howto/static-files/)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Where Django will look for static files
]

# Media files (for user uploads like audit documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Where uploaded files will be stored

# Default primary key field type
# [https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field](https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser' # Point to our custom user model

# Login/Logout redirects (these are for the web app, not directly used by API)
LOGIN_URL = 'login' # Name of the URL pattern for login
LOGIN_REDIRECT_URL = 'dashboard' # Name of the URL pattern to redirect after login
LOGOUT_REDIRECT_URL = 'login' # Name of the URL pattern to redirect after logout


# -----------------------------------------------
# Django REST Framework Settings (for API)
# -----------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Default to requiring authentication
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10, # Optional: For pagination in API list views
}

# Simple JWT Settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60), # Access token valid for 60 minutes
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),    # Refresh token valid for 1 day
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY, # Use Django's SECRET_KEY for signing JWTs
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

# CORS Headers Settings (for allowing mobile app to connect)
CORS_ALLOWED_ORIGINS = [
    # Add the origins where your React Native app will run during development.
    # For Expo Go, this might be your local IP address (e.g., 'exp://192.168.1.100:19000')
    # Or for a web build of Expo, it might be 'http://localhost:19006'
    # For production, specify your actual mobile app's domain if it's a web build,
    # or consider a more secure approach for native apps.
    # For simplicity during initial development, you might use CORS_ALLOW_ALL_ORIGINS = True
    # but be aware of security implications in production.
    "http://localhost:8081", # React Native development server default
    "http://localhost:19000", # Expo Go default
    "exp://localhost:19000", # Expo Go default
    "http://127.0.0.1:8081",
    "http://127.0.0.1:19000",
    # Add your local IP address if you are testing on a physical device in your network
    # E.g., "http://192.168.1.X:8081",
    # E.g., "exp://192.168.1.X:19000",
]

# For development, you might temporarily allow all origins.
# IMPORTANT: Set this to False and configure CORS_ALLOWED_ORIGINS for production!
CORS_ALLOW_ALL_ORIGINS = True







'''
# Project: meity_audit_portal
# File: meity_audit_portal/settings.py
# Description: Configuration settings for the Django project.

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See [https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here-for-production' # Replace with a real secret key in production

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',  # Register the users app
    'audit_management.apps.AuditManagementConfig', # Register the audit_management app
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'your_app_name',  # if not already added
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'meity_audit_portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Look for templates in a global 'templates' directory
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

WSGI_APPLICATION = 'meity_audit_portal.wsgi.application'

# Database
# Using SQLite for simplicity. For production, consider PostgreSQL, MySQL, etc.
# [https://docs.djangoproject.com/en/5.0/ref/settings/#databases](https://docs.djangoproject.com/en/5.0/howto/databases/)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# [https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators](https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators)

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
# [https://docs.djangoproject.com/en/5.0/topics/i18n/](https://docs.djangoproject.com/en/5.0/topics/i18n/)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata' # Set to India's timezone

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# [https://docs.djangoproject.com/en/5.0/howto/static-files/](https://docs.djangoproject.com/en/5.0/howto/static-files/)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Where Django will look for static files
]

# Media files (for user uploads like audit documents)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Where uploaded files will be stored

# Default primary key field type
# [https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field](https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser' # Point to our custom user model

# Login/Logout redirects
LOGIN_URL = 'login' # Name of the URL pattern for login
LOGIN_REDIRECT_URL = 'dashboard' # Name of the URL pattern to redirect after login
LOGOUT_REDIRECT_URL = 'login' # Name of the URL pattern to redirect after logout


CSRF_TRUSTED_ORIGINS = [
    'https://meity-audit-v1.onrender.com',
]




REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

'''
