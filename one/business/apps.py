from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BusinessConfig(AppConfig):
    name = "one.business"
    verbose_name = _("Business")

    def ready(self):
        try:
            import one.business.signals  # noqa: F401
        except ImportError:
            pass
