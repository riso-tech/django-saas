from django.contrib import admin

from .models import PaymentGatewayApp, PaymentGatewayToken


@admin.register(PaymentGatewayApp)
class PaymentGatewayAppAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "provider",
    )


@admin.register(PaymentGatewayToken)
class PaymentGatewayTokenAdmin(admin.ModelAdmin):
    raw_id_fields = ("app",)
    list_display = ("app", "truncated_token", "expires_at")
    list_filter = ("app", "app__provider", "expires_at")

    @admin.display(description="Token")
    def truncated_token(self, token):
        max_chars = 40
        ret = token.token
        if len(ret) > max_chars:
            ret = ret[0:max_chars] + "...(truncated)"
        return ret
