from django.conf import settings

from ..base import Provider


class PaypalProvider(Provider):
    id = "paypal"
    name = "Paypal"

    _DEFAULT_HEADERS = {"Content-Type": "application/json", "Accept": "application/json", "Authorization": ""}

    _ACCESS_TOKEN = {
        "url": "v1/oauth2/token",
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "",
        },
        "data": {"client_id": "", "client_secret": "", "grant_type": "client_credentials"},
        "expected": ["access_token", "token_type", "expires_in"],
    }

    _PAYOUT = {
        "url": "/v1/payments/payouts",
        "method": "POST",
        "headers": _DEFAULT_HEADERS,
        "data": {
            "sender_batch_header": {"email_subject": "You have a payment", "sender_batch_id": "batch-1700754979818"},
            "items": [
                {
                    "recipient_type": "PHONE",
                    "amount": {"value": "1.00", "currency": "USD"},
                    "receiver": "4087811638",
                    "note": "Payouts sample transaction",
                    "sender_item_id": "item-1-1700754979818",
                },
                {
                    "recipient_type": "EMAIL",
                    "amount": {"value": "1.00", "currency": "USD"},
                    "receiver": "ps-rec@paypal.com",
                    "note": "Payouts sample transaction",
                    "sender_item_id": "item-2-1700754979818",
                },
                {
                    "recipient_type": "PAYPAL_ID",
                    "amount": {"value": "1.00", "currency": "USD"},
                    "receiver": "FSMRBANCV8PSG",
                    "note": "Payouts sample transaction",
                    "sender_item_id": "item-3-1700754979818",
                },
            ],
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_base_url()

    def get_access_token(self):
        access_token = self.app.token
        token_type = "Bearer"
        expires_in = self.app.expired_at

        if not self.app.is_authenticated:
            self.get_base_url()

            self._ACCESS_TOKEN["data"]["client_id"] = self.app.client_id
            self._ACCESS_TOKEN["data"]["client_secret"] = self.app.secret
            self._ACCESS_TOKEN["headers"]["Authorization"] = self.encode_basic_auth()
            self._ACCESS_TOKEN["url"] = self.base_url + self._ACCESS_TOKEN["url"]
            self.set_header(self._ACCESS_TOKEN["headers"])
            response = self.client.request(
                self._ACCESS_TOKEN["method"], self._ACCESS_TOKEN["url"], self._ACCESS_TOKEN["data"]
            )

            if response.status_code > 299:
                # TODO: adapter Log error
                return

            access_token_json = response.json()
            if not all(key in access_token_json for key in self._ACCESS_TOKEN["expected"]):
                # TODO: adapter Log error
                return
            access_token = access_token_json["access_token"]
            token_type = access_token_json["token_type"]
            expires_in = access_token_json["expires_in"]

        if isinstance(expires_in, int):
            expired_at = self.set_expired_datetime("seconds", expires_in)
            from ...adapters import get_adapter

            adapter = get_adapter()
            adapter.populate_app(self.app, {"token": access_token, "token_type": token_type, "expired_at": expired_at})

        self._DEFAULT_HEADERS["Authorization"] = self.encode_access_token(token_type, access_token)
        self.set_header(self._DEFAULT_HEADERS)

    def get_base_url(self):
        if any([settings.DEBUG, not self.app.live_mode]):
            self.base_url = "https://api.sandbox.paypal.com/"
        else:
            self.base_url = "https://api.paypal.com/"


provider_classes = [PaypalProvider]
