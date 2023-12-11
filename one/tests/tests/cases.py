from django_tenants.test.cases import FastTenantTestCase as BaseFastTenantTestCase
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

from one.utils.random import generate_random_string


class FastTenantTestCase(BaseFastTenantTestCase):
    @classmethod
    def setup_test_tenant_and_domain(cls):
        cls.tenant = get_tenant_model()(
            schema_name=cls.get_test_schema_name(), name=generate_random_string(), code=generate_random_string()
        )
        cls.setup_tenant(cls.tenant)
        cls.tenant.save(verbosity=cls.get_verbosity())

        # Set up domain
        tenant_domain = cls.get_test_tenant_domain()
        cls.domain = get_tenant_domain_model()(tenant=cls.tenant, domain=tenant_domain, is_primary=True)
        cls.setup_domain(cls.domain)
        cls.domain.save()
        cls.use_new_tenant()
