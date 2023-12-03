from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin, TenantMixin
from model_utils.models import TimeStampedModel

from one.utils.db.models import MasterModel


class Business(TimeStampedModel, MasterModel, TenantMixin):
    # default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True

    # TODO: In case you wanna add more field to business model
    #  you have to update flow create first business in middleware

    class Meta:
        verbose_name = _("Business")
        verbose_name_plural = _("Businesses")


class Domain(DomainMixin):
    class Meta:
        verbose_name = _("Domain")
        verbose_name_plural = _("Domains")
