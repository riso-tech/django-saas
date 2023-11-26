import random
import string
import tempfile

from django.core.management import call_command
from django.db import connection
from django.test import override_settings
from django_tenants.test.cases import TenantTestCase as TestCase
from django_tenants.utils import get_tenant_domain_model, get_tenant_model


def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits  # You can add more characters if needed
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


class TestCollectstatic(TestCase):
    """
    Test manage.py collectstatic --noinput --link

    with different versions of STATICFILES_STORAGE. See
    https://github.com/sehmaschine/django-grappelli/issues/1022
    """

    @classmethod
    def setUpClass(cls):
        cls.sync_shared()
        cls.add_allowed_test_domain()
        cls.tenant = get_tenant_model()(
            schema_name=cls.get_test_schema_name(), name=generate_random_string(), code=generate_random_string()
        )
        cls.setup_tenant(cls.tenant)
        cls.tenant.save(verbosity=cls.get_verbosity())

        # Set up domain
        tenant_domain = cls.get_test_tenant_domain()
        cls.domain = get_tenant_domain_model()(tenant=cls.tenant, domain=tenant_domain)
        cls.setup_domain(cls.domain)
        cls.domain.save()

        connection.set_tenant(cls.tenant)  # noqa

    def test_collect_static(self):
        for storage in [
            "django.contrib.staticfiles.storage.StaticFilesStorage",
            "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        ]:
            with override_settings(
                STATICFILES_STORAGE=storage,
                STATIC_ROOT=tempfile.mkdtemp(),
            ):
                call_command("collectstatic", "--noinput", "--link")
