from django.core.management import call_command
from django_tenants.test.cases import TenantTestCase as TestCase


class ChecksTests(TestCase):
    def test_run_checks(self):  # noqa
        # pytest-django doesn't run checks, but we should
        call_command("check")
