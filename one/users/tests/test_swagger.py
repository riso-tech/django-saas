import pytest
from django.urls import reverse
from django_tenants.test.client import TenantClient as Client

from one.tests.tests.cases import FastTenantTestCase as TestCase
from one.users.models import User
from tests.cases import FastTenantTestCase as TestCase


class TestSwagger(TestCase):
    def setUp(self):
        super().setUp()  # required

        self.admin_user = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.user = User.objects.create_user("admin", "admin@example.com", "admin")
        self.admin_client = Client(self.tenant)
        self.admin_client.force_login(self.admin_user)

        self.client = Client(self.tenant)

    def test_swagger_accessible_by_admin(self):
        url = reverse("api-docs")
        response = self.admin_client.get(url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_swagger_ui_not_accessible_by_normal_user(self):
        url = reverse("api-docs")
        response = self.client.get(url)
        assert response.status_code == 403

    def test_api_schema_generated_successfully(self):
        url = reverse("api-schema")
        response = self.admin_client.get(url)
        assert response.status_code == 200
