from django.contrib.auth import get_user_model
from django.urls import reverse
from django_tenants.test.client import TenantClient as Client

from one.cms.pages.models import Page
from one.tests.tests.cases import FastTenantTestCase as TestCase

User = get_user_model()


class TestUserViewSet(TestCase):
    def setUp(self):
        super().setUp()  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

        self.page = Page.objects.create(url="/", title="Homepage", template_name="flatpage/default.html")
        self.client = Client(self.tenant)  # required

    def test_get_queryset(self):
        self.client.login(username="Superuser001", password="superuser001")

        response = self.client.get(reverse("api:page-list"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("api:page-list"), data={})
        self.assertEqual(response.status_code, 400)

        data = {"url": "/about", "title": "title", "template_name": "default/default.html", "sites": [self.page.id]}
        response = self.client.post(reverse("api:page-list"), data=data)
        self.assertEqual(response.status_code, 201)

        response = self.client.put(
            reverse("api:page-detail", kwargs={"pk": self.page.id}), data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"content": ""})

        response = self.client.patch(
            reverse("api:page-update-meta", kwargs={"pk": self.page.id}),
            data={"description": "description"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"description": "description", "keywords": []})

        response = self.client.patch(
            reverse("api:page-publish", kwargs={"pk": self.page.id}),
            data={"title": "title2"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"published": False})
