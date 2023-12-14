import pytest
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponseRedirect
from django.test import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from one.tests.tests.cases import FastTenantTestCase as TestCase
from one.users.forms import UserAdminChangeForm
from one.users.models import User
from one.users.views import UserRedirectView, UserUpdateView, user_detail_view
from tests.cases import FastTenantTestCase as TestCase

pytestmark = pytest.mark.django_db


class TestUserUpdateView(TestCase):
    """
    TODO:
        extracting view initialization code as class-scoped fixture
        would be great if only pytest-django supported non-function-scoped
        fixture db access -- this is a work-in-progress for now:
        https://github.com/pytest-dev/pytest-django/pull/258
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="test", password="test")
        self.rf = RequestFactory()

    def dummy_get_response(self, request: HttpRequest):  # noqa
        return None

    def test_get_success_url(self):
        view = UserUpdateView()
        request = self.rf.get("/fake-url/")
        request.user = self.user

        view.request = request
        assert view.get_success_url() == f"/users/{self.user.username}/"

    def test_get_object(self):
        view = UserUpdateView()
        request = self.rf.get("/fake-url/")
        request.user = self.user

        view.request = request

        assert view.get_object() == self.user

    def test_form_valid(self):
        view = UserUpdateView()
        request = self.rf.get("/fake-url/")

        # Add the session/message middleware to the request
        SessionMiddleware(self.dummy_get_response).process_request(request)
        MessageMiddleware(self.dummy_get_response).process_request(request)
        request.user = self.user

        view.request = request

        # Initialize the form
        form = UserAdminChangeForm()
        form.cleaned_data = {}
        form.instance = self.user
        view.form_valid(form)

        messages_sent = [m.message for m in messages.get_messages(request)]
        assert messages_sent == [_("Information successfully updated")]


class TestUserRedirectView(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="test", password="test")
        self.rf = RequestFactory()

    def test_get_redirect_url(self):
        view = UserRedirectView()
        request = self.rf.get("/fake-url")
        request.user = self.user

        view.request = request
        assert view.get_redirect_url() == f"/users/{self.user.username}/"


class TestUserDetailView(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="test", password="test")
        self.rf = RequestFactory()

    def test_authenticated(self):
        request = self.rf.get("/fake-url/")
        request.user = self.user
        response = user_detail_view(request, username=self.user.username)

        assert response.status_code == 200

    def test_not_authenticated(self):
        request = self.rf.get("/fake-url/")
        request.user = AnonymousUser()
        response = user_detail_view(request, username=self.user.username)
        login_url = reverse(settings.LOGIN_URL)

        assert isinstance(response, HttpResponseRedirect)
        assert response.status_code == 302
        assert response.url == f"{login_url}?next=/fake-url/"
