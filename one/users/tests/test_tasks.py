import pytest
from celery.result import EagerResult
from django.test.utils import override_settings

from one.users.models import User
from one.users.tasks import get_users_count
from tests.cases import FastTenantTestCase as TestCase

pytestmark = pytest.mark.django_db


class TestTasks(TestCase):
    def setUp(self):
        super().setUp()  # required

        for i in range(3):
            User.objects.create_user(f"User00{i}", f"user00{i}@example.com", f"user00{i}")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_user_count(self):
        """A basic test to execute the get_users_count Celery task."""
        task_result = get_users_count.delay()
        assert isinstance(task_result, EagerResult)
        assert task_result.result == 3
