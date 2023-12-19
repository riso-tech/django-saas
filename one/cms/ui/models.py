from django.db.models import CASCADE, CharField, ForeignKey, ImageField, Model, TextField
from django.utils.translation import gettext_lazy as _


class Theme(Model):
    name = CharField(_("Theme name"), max_length=255, unique=True)
    description = CharField(_("Description"), max_length=255, blank=True, null=True)
    thumbnail = ImageField(_("Thumbnail"), upload_to="themes", blank=True, null=True)
    template_name = CharField(_("Render Template name"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")
        db_table = "cms_theme"

    def __str__(self):
        return self.name


class Template(Model):
    theme = ForeignKey(Theme, on_delete=CASCADE, related_name="templates")
    name = CharField(_("Template name"), max_length=255)
    description = CharField(_("Description"), max_length=255, blank=True, null=True)
    content = TextField(_("Content"), blank=True, null=True)
    thumbnail = ImageField(_("Thumbnail"), upload_to="templates", blank=True, null=True)
    icon = CharField(_("Icon"), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _("Template")
        verbose_name_plural = _("Templates")
        db_table = "cms_template"

    def __str__(self):
        return f"{self.theme.name} {self.name}"
