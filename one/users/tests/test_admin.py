from django.urls import reverse
from django_tenants.test.cases import FastTenantTestCase as TestCase
from django_tenants.test.client import TenantClient as Client

from one.users.models import User


class TestUserAdmin(TestCase):
    def setUp(self):
        super().setUp()  # required

        self.admin_user = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.user = User.objects.create_user("admin", "admin@example.com", "admin")
        self.admin_client = Client(self.tenant)
        self.admin_client.force_login(self.admin_user)

    def test_changelist(self):
        url = reverse("admin:users_user_changelist")
        response = self.admin_client.get(url)
        assert response.status_code == 200

    def test_search(self):
        url = reverse("admin:users_user_changelist")
        response = self.admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_add(self):
        url = reverse("admin:users_user_add")
        response = self.admin_client.get(url)
        assert response.status_code == 200

        response = self.admin_client.post(
            url,
            data={
                "username": "test",
                "password1": "My_R@ndom-P@ssw0rd",
                "password2": "My_R@ndom-P@ssw0rd",
            },
        )
        assert response.status_code == 302
        assert User.objects.filter(username="test").exists()

    def test_view_user(self):
        user = User.objects.get(username="admin")
        url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        response = self.admin_client.get(url)
        assert response.status_code == 200
