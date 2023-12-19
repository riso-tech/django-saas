from django.apps import AppConfig


class CmsPagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "one.cms.pages"
    verbose_name = "CMS"

    def ready(self):
        try:
            import one.cms.pages.signals  # noqa F401
        except ImportError:
            pass
