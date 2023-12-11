from one.tests.tests.cases import FastTenantTestCase as TestCase
from one.users.models import User


class TestUserModel(TestCase):
    def setUp(self):
        super().setUp()  # required
        self.user = User.objects.create_user(username="test", password="test")

    def test_user_get_absolute_url(self):
        assert self.user.get_absolute_url() == f"/users/{self.user.username}/"
