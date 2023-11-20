from django.db.models import BooleanField, CharField, DateField
from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin, TenantMixin


class Client(TenantMixin):
    name = CharField(_("Name of client"), max_length=100)
    paid_until = DateField(_("Expired date"), auto_now_add=True)
    on_trial = BooleanField(_("Is Trial"), default=False)
    created_on = DateField(_("Created on"), auto_now_add=True)

    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")


class Domain(DomainMixin):
    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
