from django.apps import AppConfig


class CmsUIConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "one.cms.ui"
    verbose_name = "CMS UI"

    def ready(self):
        try:
            import one.cms.ui.signals  # noqa F401
        except ImportError:
            pass
