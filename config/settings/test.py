"""
With these settings, tests run faster.
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa
from .base import env

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
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES["default"]["ATOMIC_REQUESTS"] = False  # noqa

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
TENANT_APPS += ["one.tests"]  # noqa: F405

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "correlation_id": {"()": "one.libraries.guid.log_filters.CorrelationId"},  # <-- Add correlation ID
        "celery_tracing": {
            "()": "one.libraries.guid.integrations.celery.log_filters.CeleryTracing"
        },  # <-- Add celery IDs
    },
    "formatters": {
        # Basic log format without django-guid filters
        "basic_format": {"format": "%(levelname)s %(asctime)s %(name)s - %(message)s"},
        # Format with correlation ID output to the console
        "correlation_id_format": {"format": "%(levelname)s %(asctime)s [%(correlation_id)s] %(name)s - %(message)s"},
        # Format with correlation ID plus a celery process' parent ID and a unique current ID that will
        # become the parent ID of any child processes that are created (most likely you won't want to
        # display these values in your formatter, but include them just as a filter)
        "celery_depth_format": {
            "format": "%(levelname)s [%(correlation_id)s] [%(celery_parent_id)s-%(celery_current_id)s] %(name)s - %(message)s"  # noqa
        },
    },
    "handlers": {
        "correlation_id_handler": {
            "class": "logging.StreamHandler",
            "formatter": "correlation_id_format",
            # Here we include the filters on the handler - this means our IDs are included in the logger extra data
            # and *can* be displayed in our log message if specified in the formatter - but it will be
            # included in the logs whether shown in the message or not.
            "filters": ["correlation_id", "celery_tracing"],
        },
        "celery_depth_handler": {
            "class": "logging.StreamHandler",
            "formatter": "celery_depth_format",
            "filters": ["correlation_id", "celery_tracing"],
        },
    },
    "loggers": {
        "django": {"handlers": ["correlation_id_handler"], "level": "INFO"},
        "demoproj": {"handlers": ["correlation_id_handler"], "level": "DEBUG"},
        "django_guid": {
            "handlers": ["correlation_id_handler"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django_guid.celery": {
            "handlers": ["celery_depth_handler"],
            "level": "DEBUG",
            "propagate": False,
        },
        "celery": {
            "handlers": ["celery_depth_handler"],
            "level": "INFO",
        },
    },
}


# Sentry
# ------------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default="")

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()],
    environment=env("SENTRY_ENVIRONMENT", default="test"),
    traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=0.0),
)

# Your stuff...
# ------------------------------------------------------------------------------
