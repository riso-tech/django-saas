from django.db.models import CASCADE, BooleanField, CharField, ForeignKey, Model
from django.utils.translation import gettext_lazy as _


class UserStampedModel(Model):
    creator = ForeignKey(
        "users.User",
        verbose_name=_("Created by"),
        related_name="%(app_label)s_%(class)s_creator",
        null=True,
        blank=True,
        on_delete=CASCADE,
    )
    last_modified_by = ForeignKey(
        "users.User",
        verbose_name="Last modified by",
        related_name="%(app_label)s_%(class)s_last_modified_by",
        null=True,
        blank=True,
        on_delete=CASCADE,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        request_user = kwargs.pop("request", None).user if kwargs.pop("request", None) else None
        if request_user:
            if not self.pk:
                # set creator if object is new
                self.creator = request_user
            self.last_modified_by = request_user
        super().save(*args, **kwargs)


class MasterModel(Model):
    code = CharField(_("Unique Code"), max_length=100, unique=True)
    is_active = BooleanField(_("Is Active"), default=True)

    name = CharField(_("Name"), max_length=100)
    description = CharField(_("Description"), max_length=255, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
