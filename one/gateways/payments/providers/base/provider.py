import base64

from one.utils.requests.client import ServiceClient


class Provider:
    def __init__(self, request=None, app=None):
        self.client = ServiceClient()
        self.request = request
        self.app = app

    def get_client(self):
        return self.client

    def basic_auth_header(self, username=None, password=None):
        username = username or self.app.client_id
        password = password or self.app.client_secret
        return "Basic " + base64.b64encode((username + ":" + password).encode()).decode()
