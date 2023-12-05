from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import RequestFactory
from django_tenants.test.client import TenantClient as Client

from tests.cases import FastTenantTestCase as TestCase

from ..middlewares import TenantMainMiddleware

User = get_user_model()


class BusinessMiddlewareTests(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.client = Client(self.tenant)  # required
        self.rf = RequestFactory()

    def dummy_get_response(self, request: HttpRequest):  # noqa
        return None

    def test_middleware(self):
        request = self.rf.get("/fake-url/")

        # Add the session/message middleware to the request
        response = TenantMainMiddleware(self.dummy_get_response).process_request(request)
        assert response.status_code == 200
        self.assertTemplateUsed("business_not_found.html")

    @patch("one.business.models.Business.objects.exclude")
    def test_middleware_missing_first_business(self, qs):
        request = self.rf.get("/fake-url/")
        qs.return_value.exists.return_value = False
        # Add the session/message middleware to the request
        response = TenantMainMiddleware(self.dummy_get_response).process_request(request)
        assert response.status_code == 200
        self.assertTemplateUsed("first_business_not_found.html")
