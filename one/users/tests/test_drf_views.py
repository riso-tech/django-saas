from rest_framework.test import APIRequestFactory

from one.users.api.views import UserViewSet
from one.users.models import User
from tests.cases import FastTenantTestCase as TestCase


class TestUserViewSet(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.user = User.objects.create_user(username="test", password="test")
        self.api_rf = APIRequestFactory()

    def test_get_queryset(self):
        view = UserViewSet()
        request = self.api_rf.get("/fake-url/")
        request.user = self.user

        view.request = request

        assert self.user in view.get_queryset()

    def test_me(self):
        view = UserViewSet()
        request = self.api_rf.get("/fake-url/")
        request.user = self.user

        view.request = request

        response = view.me(request)  # type: ignore

        assert response.data == {
            "username": self.user.username,
            "url": f"http://testserver/api/users/{self.user.username}/",
            "name": self.user.name,
        }
