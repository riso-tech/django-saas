from django.contrib import admin

from .forms import PaymentGatewayAppCreationForm
from .models import PaymentGatewayApp


@admin.register(PaymentGatewayApp)
class PaymentGatewayAppAdmin(admin.ModelAdmin):
    add_form = PaymentGatewayAppCreationForm

    list_display = ("name", "provider", "live_mode", "is_authenticated", "truncated_token", "qq")

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during App creation
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    @admin.display(description="Is Authenticated", boolean=True)
    def is_authenticated(self, obj):
        return obj.is_authenticated

    @admin.display(description="Token")
    def truncated_token(self, obj):
        max_chars = 40
        ret = obj.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + "...(truncated)"
        return ret

    @admin.display(description="QQ")
    def qq(self, obj):
        provider = obj.get_provider()
        provider.get_access_token()
        return provider.get_header()
