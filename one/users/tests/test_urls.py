from django.urls import resolve, reverse

from one.tests.tests.cases import FastTenantTestCase as TestCase
from one.users.models import User


class TestUserUrls(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.user = User.objects.create_user(username="test", password="test")

    def test_detail(self):
        assert reverse("users:detail", kwargs={"username": self.user.username}) == f"/users/{self.user.username}/"
        assert resolve(f"/users/{self.user.username}/").view_name == "users:detail"

    def test_update(self):
        assert reverse("users:update") == "/users/~update/"
        assert resolve("/users/~update/").view_name == "users:update"

    def test_redirect(self):
        assert reverse("users:redirect") == "/users/~redirect/"
        assert resolve("/users/~redirect/").view_name == "users:redirect"
