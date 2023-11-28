from django.db.models import BooleanField
from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin, TenantMixin
from model_utils.models import TimeStampedModel

from one.utils.db.models import MasterModel


class Client(TimeStampedModel, MasterModel, TenantMixin):
    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    is_super_business = BooleanField(_("Is Super Business"), default=False, editable=False)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")


class Domain(DomainMixin):
    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
