from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TestsConfig(AppConfig):
    name = "one.tests"
    verbose_name = _("Tests")
