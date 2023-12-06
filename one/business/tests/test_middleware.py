from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django_tenants.test.client import TenantClient as Client
from django_tenants.utils import get_tenant_model

from tests.cases import FastTenantTestCase as TestCase

from ..middlewares import TenantMainMiddleware

User = get_user_model()


class BusinessMiddlewareMissingFirstBusinessTests(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.client = Client(self.tenant)  # required
        self.rf = RequestFactory()
        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

    @patch("one.business.models.Business.objects.exclude")
    def test_missing_first_business_get(self, qs):
        qs.return_value = get_tenant_model().objects.none()
        middleware = TenantMainMiddleware(MagicMock())
        request = self.rf.get("/")

        response = middleware.process_request(request)
        assert response.status_code == 200
        self.assertTemplateUsed("first_business_not_found.html")

    @patch("one.business.models.Business.objects.exclude")
    @patch("one.utils.call_command.call_command")
    @patch("one.utils.call_command.base_call_command")
    @patch("one.users.models.User.objects.filter")
    @patch("django.contrib.sites.models.Site.objects.update")
    def test_missing_first_business_post(self, site_update, user_qs, base_command, command, qs):
        qs.return_value = get_tenant_model().objects.none()
        command.return_value = [], True
        base_command.return_value = None
        user_qs.return_value.first.return_value = self.superuser_1
        site_update.return_value = True
        middleware = TenantMainMiddleware(MagicMock())
        data = {
            "schema_name": self.get_test_schema_name(),
            "name": "name",
            "code": "code",
            "description": "description",
            "is_active": True,
            "is_primary": True,
            "domain": "domain.localhost",
            "email": "email",
            "username": "Superuser001",
            "password1": "password1",
        }
        request = self.rf.post("/", data)

        response = middleware.process_request(request)
        assert response.status_code == 302


class BusinessMiddlewareBusinessNotFoundTests(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.client = Client(self.tenant)  # required
        self.rf = RequestFactory()

    @patch("one.business.models.Business.objects.exclude")
    @patch("one.business.models.Business.objects.filter")
    @patch("one.business.models.Business.objects.get")
    @patch("django_tenants.middleware.main.TenantMainMiddleware.hostname_from_request")
    def test_missing_business_not_found(self, hostname, get_qs, filter_qs, exclude_qs):
        exclude_qs.return_value.exists.return_value = True
        filter_qs.return_value.exists.return_value = False
        get_qs.return_value.first.return_value = self.tenant
        hostname.return_value = "google.com"
        middleware = TenantMainMiddleware(MagicMock())
        request = self.rf.get("/")

        response = middleware.process_request(request)
        assert response.status_code == 200
        self.assertTemplateUsed("business_not_found.html")

    @patch("one.business.models.Business.objects.exclude")
    @patch("one.business.models.Business.objects.filter")
    @patch("one.business.models.Business.objects.get")
    @patch("django_tenants.middleware.main.TenantMainMiddleware.hostname_from_request")
    def test_missing_business_not_found_raise_e(self, hostname, get_qs, filter_qs, exclude_qs):
        exclude_qs.return_value.exists.return_value = True
        filter_qs.return_value.exists.return_value = False
        get_qs.return_value = get_tenant_model().objects.none()
        hostname.return_value = "google.com"
        middleware = TenantMainMiddleware(MagicMock())
        request = self.rf.get("/")

        response = middleware.process_request(request)
        assert response.status_code == 200
        self.assertTemplateUsed("business_not_found.html")
