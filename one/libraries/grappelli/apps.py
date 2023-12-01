from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GrappelliConfig(AppConfig):
    name = "one.libraries.grappelli"
    verbose_name = _("Grappelli")

    def ready(self):
        from .checks import register_checks

        register_checks()
