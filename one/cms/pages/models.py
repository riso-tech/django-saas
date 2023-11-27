from django.contrib.flatpages.models import FlatPage
from django.contrib.postgres.fields import ArrayField
from django.db.models import BooleanField, CharField
from django.utils.translation import gettext_lazy as _
from meta.models import ModelMeta


class Page(ModelMeta, FlatPage):
    """FlatPage model
    url: CharField
    title: CharField
    content: TextField
    enable_comments: BooleanField
    template_name: CharField
    registration_required: BooleanField
    sites: ManyToManyField
    """

    published = BooleanField(_("Published"), default=False)

    description = CharField(_("Description"), max_length=255, blank=True, null=True)
    keywords = ArrayField(CharField(max_length=50), verbose_name=_("Keywords"), default=list, blank=True, null=True)

    _metadata = {
        "title": "title",
        "description": "description",
        "keywords": "keywords",
    }

    class Meta:
        verbose_name = _("CMS Page")
        verbose_name_plural = _("CMS Pages")
        db_table = "cms_page"
