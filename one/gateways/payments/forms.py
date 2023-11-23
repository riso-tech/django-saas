from django.forms import ModelForm

from .models import PaymentGatewayApp


class PaymentGatewayAppCreationForm(ModelForm):
    class Meta:
        model = PaymentGatewayApp
        fields = ("provider", "live_mode", "name", "client_id", "secret", "key")
