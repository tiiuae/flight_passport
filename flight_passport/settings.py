"""
Django settings for flight_passport project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from urllib.parse import urlparse

import dj_database_url
from dotenv import find_dotenv, load_dotenv

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "_m7&5-z7-_+qw*^05k8lg1wrl8ip0or#&2-lxo-*=33d1(3ke9")
# SECURITY WARNING: don't run with debug turned on in production!
debug_mode = os.environ.get("ENABLE_DEBUG", 0)
if int(debug_mode):
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ["*"]

issuer_domain = os.environ.get("JWT_ISSUER_DOMAIN", None)
if issuer_domain:
    d = urlparse(issuer_domain).hostname
    ALLOWED_HOSTS = [d]
    CSRF_TRUSTED_ORIGINS = [issuer_domain]
    CORS_ORIGIN_WHITELIST = [issuer_domain]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oauth2_provider",
    "oauth2_provider_jwt",
    "corsheaders",
    "authprofiles",
    "rolepermissions",
    "allauth",
    "vault",
    "allauth.account",
    "allauth.socialaccount",
    "anymail",
]

ANYMAIL = {
    # (exact settings here depend on your ESP...)
    "MAILERSEND_API_TOKEN": os.environ.get("MAILERSEND_API_TOKEN", "000000"),  # Email service provider API Key
    "RESEND_API_KEY": os.environ.get("RESEND_API_KEY", "000000"),
}
SITE_ID = 1


MIDDLEWARE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "csp.middleware.CSPMiddleware",
)

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = [
     os.environ.get("JWT_ISSUER_DOMAIN", "https://local.test:9000"),
]

ROOT_URLCONF = "flight_passport.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (
            os.path.join(BASE_DIR, "allauth", "templates", "allauth"),
            os.path.join(BASE_DIR, "vault", "templates"),
        ),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "vault.context_processors.from_settings",
            ],
        },
    },
]

# Django Superuser

DJANGO_SUPERUSER_USERNAME = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
DJANGO_SUPERUSER_EMAIL = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@mysite.com")
DJANGO_SUPERUSER_INITIAL_PASSWORD = os.environ.get("DJANGO_SUPERUSER_INITIAL_PASSWORD", "admin")  # To be changed after first login by admin

WSGI_APPLICATION = "flight_passport.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

SOCIALACCOUNT_AUTO_SIGNUP = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_ADAPTER = "authprofiles.adapter.PassportAccountAdapter"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "Openskies Flight Passport Support <noreply@id.openskies.sh>")
LOGO_URL = "https://www.openskies.sh/images/logo.svg"
APPLICATION_NAME = "Openskies Flight Passport"

ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = os.environ.get("ESP_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

EMAIL_PORT = 587
EMAIL_USE_TLS = True

ACCOUNT_FORMS = {
    "signup": "authprofiles.forms.PassportSignUpForm",
    "login": "authprofiles.forms.PassportLoginForm",
    "reset_password": "authprofiles.forms.ResetPasswordForm",
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
    "oauth2_provider.backends.OAuth2Backend",
)

JWT_ISSUER = os.environ.get("JWT_ISSUER_NAME", "Openskies")
JWT_ISSUER_DOMAIN = os.environ.get("JWT_ISSUER_DOMAIN", "https://id.openskies.sh/")
JWT_ID_ATTRIBUTE = "email"
JWT_PRIVATE_KEY_OPENSKIES = os.environ.get("OIDC_RSA_PRIVATE_KEY")

JWT_PAYLOAD_ENRICHER = "vault.jwt_utils.payload_enricher"

SHOW_ADMIN = int(os.environ.get("SHOW_ADMIN", 0))

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# SCOPES_BACKEND_CLASS = 'authprofiles.scopes'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
OAUTH2_PROVIDER_APPLICATION_MODEL = "authprofiles.PassportApplication"
OAUTH2_PROVIDER = {
    # 'OAUTH2_BACKEND_CLASS': 'oauth2_provider.oauth2_backends.JSONOAuthLibCore',
    "OIDC_ENABLED": True,
    "PKCE_REQUIRED": os.environ.get("PKCE_ENABLED", False),
    "OIDC_RSA_PRIVATE_KEY": os.environ.get("OIDC_RSA_PRIVATE_KEY"),
    # 'APPLICATION_MODEL': 'authprofiles.PassportApplication',
    "SCOPES_BACKEND_CLASS": "authprofiles.scopes.PassportScopes",
    "OAUTH2_VALIDATOR_CLASS": "authprofiles.oauth_validators.PassportOAuth2Validator",
    "REQUEST_APPROVAL_PROMPT": "auto",
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,
    "REFRESH_TOKEN_EXPIRE_SECONDS": 3600,
    "ID_TOKEN_EXPIRE_SECONDS": 3600,
}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {}
USING_DOCKER_COMPOSE = int(os.environ.get("USING_DOCKER_COMPOSE", 0))
if USING_DOCKER_COMPOSE:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("DB_DATABASE", os.path.join(BASE_DIR, "flight_passport.sqlite3")),
        }
    }
else:
    DATABASES["default"] = dj_database_url.config(conn_max_age=600)


# Enable HTTP Strict-Transport-Security (HSTS) to force clients to always use secure connections

SECURE_HSTS_SECONDS = 31536000  # One year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Enable browser XSS filtering
SECURE_CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'none'"

# Enable X-Content-Type-Options nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable Referrer-Policy
CSP_DEFAULT_SRC = ("'self'",)

# Enable HTTP Strict-Transport-Security (HSTS) to force clients to always use secure connections

SECURE_HSTS_SECONDS = 31536000  # One year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Enable browser XSS filtering
SECURE_CONTENT_SECURITY_POLICY = "default-src 'self'; script-src 'none'"
