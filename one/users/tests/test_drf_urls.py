from django.urls import resolve, reverse

from one.users.models import User
from tests.cases import FastTenantTestCase as TestCase


class TestUserDrfUrls(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.user = User.objects.create_user(username="test", password="test")

    def test_user_detail(self):
        assert (
            reverse("api:user-detail", kwargs={"username": self.user.username}) == f"/api/users/{self.user.username}/"
        )
        assert resolve(f"/api/users/{self.user.username}/").view_name == "api:user-detail"

    def test_user_list(self):
        assert reverse("api:user-list") == "/api/users/"
        assert resolve("/api/users/").view_name == "api:user-list"

    def test_user_me(self):
        assert reverse("api:user-me") == "/api/users/me/"
        assert resolve("/api/users/me/").view_name == "api:user-me"
