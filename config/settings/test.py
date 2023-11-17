"""
With these settings, tests run faster.
"""

from .base import *  # noqa
from .base import env

INSTALLED_APPS.remove("django_tenants")  # noqa
MIDDLEWARE.remove("django_tenants.middleware.main.TenantMainMiddleware")  # noqa

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="QFoR5XA5TbHg7bQ3bTWOhRYwsWxmApH4wKM9yNedAMmtOUoAHNhEJtIR9hXVkA6O",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3"},
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# DEBUGGING FOR TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore # noqa: F405

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "http://media.testserver/"

# Test App
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["one.tests"]  # noqa: F405

# Django Tenants
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-DATABASE_ROUTERS
DATABASE_ROUTERS = []

# Your stuff...
# ------------------------------------------------------------------------------
