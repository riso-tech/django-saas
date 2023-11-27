from django.db import connection
from django_tenants.test.cases import TenantTestCase as BaseTenantTestCase
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

from one.utils.random import generate_random_string


class TenantTestCase(BaseTenantTestCase):
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
