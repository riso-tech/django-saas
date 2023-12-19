from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model, decorators
from django.utils.translation import gettext_lazy as _

from one.users.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://django-allauth.readthedocs.io/en/stable/advanced.html#admin
    admin.site.login = decorators.login_required(admin.site.login)  # type: ignore[method-assign]

if "allauth.account" in settings.INSTALLED_APPS:
    from allauth.account.models import EmailAddress

    admin.site.unregister(EmailAddress)

if "rest_framework.authtoken" in settings.INSTALLED_APPS:
    from rest_framework.authtoken.models import TokenProxy

    admin.site.unregister(TokenProxy)

if "django.contrib.sites" in settings.INSTALLED_APPS:
    from django.contrib.sites.models import Site

    admin.site.unregister(Site)


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]

    def get_fieldsets(self, request, obj=None):
        """Add `is_active` and `groups` fields to fieldsets for non-superusers."""
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            permission_fieldset = (
                (
                    _("Permissions"),
                    {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
                ),
            )
            return self.fieldsets + permission_fieldset
        return self.fieldsets + ((_("Permissions"), {"fields": ("is_active", "groups")}),)

    def get_queryset(self, request):
        """Limit queryset to exclude superusers for non-superusers."""
        if request.user.is_superuser:
            return super().get_queryset(request)
        return super().get_queryset(request).exclude(is_superuser=True)
