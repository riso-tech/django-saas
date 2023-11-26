from one.utils.importlib import import_attribute

from ..payments import app_settings


class DefaultPaymentGatewayApplicationAdapter:
    @staticmethod
    def populate_app(app, data):
        app.token = data["token"]
        app.expired_at = data["expired_at"]
        app.save()
        return app


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
