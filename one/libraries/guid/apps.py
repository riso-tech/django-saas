from django.apps import AppConfig


class DjangoGuidConfig(AppConfig):
    name = "one.libraries.guid"

    def ready(self) -> None:
        """
        In order to avoid circular imports we import signals here.
        """
        try:
            import one.libraries.guid.signals  # noqa F401
        except ImportError:
            pass

        from one.libraries.guid.config import settings

        settings.validate()
