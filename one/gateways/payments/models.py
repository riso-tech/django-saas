from django.db.models import CASCADE, CharField, DateTimeField, JSONField, Model, OneToOneField, TextField
from django.utils.translation import gettext_lazy as _

from . import providers


class PaymentGatewayApp(Model):
    # The provider type, e.g. "PayPal", "Stripe".
    provider = CharField(_("Provider"), max_length=30, choices=providers.registry.as_choices())

    name = CharField(_("name"), max_length=40)
    client_id = CharField(_("Client ID"), max_length=191, help_text=_("App ID, or consumer key"))
    secret = CharField(
        _("secret key"), max_length=191, blank=True, help_text=_("API secret, client secret, or consumer secret")
    )
    key = CharField(_("key"), max_length=191, blank=True, help_text=_("Key"))

    settings = JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payment_gateway_app"
        verbose_name = _("payment gateway application")
        verbose_name_plural = _("payment gateway applications")

    def __str__(self):
        return self.name

    def get_provider(self, request):
        provider_class = providers.registry.get_class(self.provider)
        return provider_class(request=request, app=self)


class PaymentGatewayToken(Model):
    app = OneToOneField(PaymentGatewayApp, verbose_name=_("Payment Gateway App"), on_delete=CASCADE)
    token = TextField(_("token"), help_text=_('"oauth_token" (OAuth1) or access token (OAuth2)'))
    token_secret = TextField(
        _("token secret"), blank=True, help_text=_('"oauth_token_secret" (OAuth1) or refresh token (OAuth2)')
    )
    expires_at = DateTimeField(_("expires at"), blank=True, null=True)

    class Meta:
        db_table = "payment_gateway_token"
        verbose_name = _("payment gateway token")
        verbose_name_plural = _("payment gateway tokens")

    def __str__(self):
        return self.token
