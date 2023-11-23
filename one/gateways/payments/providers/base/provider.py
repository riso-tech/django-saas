import base64
from datetime import datetime, timedelta

from one.utils.requests.client import ServiceClient


class Provider:
    base_url = None

    def __init__(self, *args, **kwargs):
        self.app = kwargs.get("app", None)
        assert self.app is not None, "Provider must be Init with App instance"
        self.request = kwargs.get("request", None)
        self.client = ServiceClient()

    def authenticate(self):
        raise NotImplementedError("authenticate() must be implemented in Provider subclass")

    def encode_basic_auth(self, username=None, password=None):
        username = username or self.app.client_id
        password = password or self.app.secret
        return "Basic " + base64.b64encode((username + ":" + password).encode()).decode()

    def encode_access_token(self, token_type="Bearer", access_token=None):
        access_token = access_token or self.app.token
        return f"{token_type} {access_token}"

    def get_base_url(self):
        raise NotImplementedError("get_base_url() must implemented in Provider subclass")

    def get_client(self):
        return self.client

    def get_header(self):
        return self.client.session.headers

    def set_header(self, headers):
        self.client.session.headers = headers

    @staticmethod
    def set_expired_datetime(time_unit, time_value):
        return datetime.now() + timedelta(**{time_unit: time_value})
