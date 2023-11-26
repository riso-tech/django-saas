import importlib
from collections import OrderedDict

from ..app_settings import PROVIDERS


class ProviderRegistry:
    def __init__(self):
        self.provider_map = OrderedDict()
        self.loaded = False

    def get_class_list(self):
        self.load()
        return list(self.provider_map.values())

    def register(self, cls):
        self.provider_map[cls.id] = cls

    def get_class(self, id):
        return self.provider_map.get(id)

    def as_choices(self):
        self.load()
        for provider_cls in self.provider_map.values():
            yield provider_cls.id, provider_cls.name

    def load(self):
        if not self.loaded:
            providers = PROVIDERS
            for provider_path in providers:
                try:
                    provider_module = importlib.import_module(provider_path)
                except ImportError:
                    pass
                else:
                    for cls in getattr(provider_module, "provider_classes", []):
                        self.register(cls)

            self.loaded = True


registry = ProviderRegistry()
