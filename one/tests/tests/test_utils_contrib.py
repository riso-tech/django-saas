from unittest import mock

from django.contrib.admin.utils import quote
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse
from django_tenants.test.client import TenantClient as Client

from one.tests.models import Choice, Comment, Poll, RelatedData
from one.tests.tests.cases import FastTenantTestCase as TestCase
from one.utils.contrib.admin import BaseActionView, BaseDjangoObjectActions, action, takes_instance_or_queryset

User = get_user_model()


class AppTests(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

        self.poll_1 = Poll.objects.create(question="Do you like me?", pub_date="2012-10-20T18:20:35")
        self.poll_2 = Poll.objects.create(question="Do you wanna build a snow man?", pub_date="2012-10-20T18:20:38")
        self.choice_1 = Choice.objects.create(poll=self.poll_1, choice_text="Yes", votes=0)
        self.choice_2 = Choice.objects.create(poll=self.poll_1, choice_text="No", votes=100)

    def test_setup(self):
        """
        Test setup
        """
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(Poll.objects.all().count(), 2)
        self.assertEqual(Choice.objects.all().count(), 2)

    def test_tool_func_gets_executed(self):
        self.client.login(username="Superuser001", password="superuser001")

        choice_1_id = self.choice_1.id
        votes = self.choice_1.votes
        self.assertEqual(votes, 0)

        response = self.client.get(reverse("admin:tests_choice_actions", args=(choice_1_id, "increment_vote")))
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("admin/changelist.html")

        url = reverse("admin:tests_choice_change", args=(choice_1_id,))
        self.assertEqual(url, f"/admin/tests/choice/{choice_1_id}/change/")

        self.assertTrue(response["location"].endswith(url))
        choice = Choice.objects.get(pk=choice_1_id)
        self.assertEqual(choice.votes, votes + 1)

    def test_tool_can_return_http_response(self):
        self.client.login(username="Superuser001", password="superuser001")
        # we know this url works because of fixtures
        url = reverse("admin:tests_choice_actions", args=(self.choice_2.id, "edit_poll"))
        response = self.client.get(url)
        # we expect a redirect
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["location"].endswith(reverse("admin:tests_poll_change", args=(self.poll_1.id,))))

    def test_can_return_template(self):
        # This is more of a test of render_to_response than the app, but I think
        # it's good to document that this is something we can do.
        self.client.login(username="Superuser001", password="superuser001")

        url = reverse("admin:tests_poll_actions", args=(self.poll_1.id, "delete_all_choices"))
        response = self.client.get(url)
        self.assertTemplateUsed(response, "clear_choices.html")

    def test_message_user_sends_message(self):
        self.client.login(username="Superuser001", password="superuser001")

        url = reverse("admin:tests_poll_actions", args=(self.poll_1.id, "delete_all_choices"))
        self.assertNotIn("messages", self.client.cookies)
        self.client.get(url)
        self.assertIn("messages", self.client.cookies)

    def test_intermediate_page_with_post_works(self):
        self.client.login(username="Superuser001", password="superuser001")

        poll_1_id = self.poll_1.id
        self.assertEqual(Choice.objects.filter(poll=poll_1_id).count(), 2)
        url = reverse("admin:tests_poll_actions", args=(poll_1_id, "delete_all_choices"))

        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Choice.objects.filter(poll=poll_1_id).count(), 0)

    def test_undefined_tool_404s(self):
        self.client.login(username="Superuser001", password="superuser001")

        response = self.client.get(reverse("admin:tests_poll_actions", args=(self.poll_1.id, "weeeewoooooo")))
        self.assertEqual(response.status_code, 404)

    def test_key_error_tool_500s(self):
        self.client.login(username="Superuser001", password="superuser001")

        self.assertRaises(
            KeyError,
            self.client.get,
            reverse("admin:tests_choice_actions", args=(self.choice_1.id, "raise_key_error")),
        )

    def test_render_button(self):
        self.client.login(username="Superuser001", password="superuser001")

        response = self.client.get(reverse("admin:tests_choice_change", args=(self.choice_1.id,)))
        self.assertEqual(response.status_code, 200)


class BaseDjangoObjectActionsTest(TestCase):
    def setUp(self):
        self.instance = BaseDjangoObjectActions()
        self.instance.model = mock.Mock(**{"_meta.app_label": "app", "_meta.model_name": "model"})

    @mock.patch("one.utils.contrib.admin.BaseDjangoObjectActions.admin_site", create=True)
    def test_get_action_urls_trivial_case(self, mock_site):
        urls = self.instance._get_action_urls()

        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0].name, "app_model_actions")

    def test_get_change_actions_gets_attribute(self):
        # Set up
        self.instance.change_actions = mock.Mock()

        # Test
        returned_value = self.instance.get_change_actions(
            request=mock.Mock(), object_id=mock.Mock(), form_url=mock.Mock()
        )

        # Assert
        self.assertEqual(id(self.instance.change_actions), id(returned_value))

    def test_get_button_attrs_returns_defaults(self):
        # TODO: use `mock`
        mock_tool = type("mock_tool", (object,), {})
        attrs, __ = self.instance._get_button_attrs(mock_tool)
        self.assertEqual(attrs["class"], "")
        self.assertEqual(attrs["title"], "")

    def test_get_button_attrs_disallows_href(self):
        mock_tool = type("mock_tool", (object,), {"attrs": {"href": "hreeeeef"}})
        attrs, __ = self.instance._get_button_attrs(mock_tool)
        self.assertNotIn("href", attrs)

    def test_get_button_attrs_disallows_title(self):
        mock_tool = type(
            "mock_tool",
            (object,),
            {
                "attrs": {"title": "i wanna be a title"},
                "short_description": "real title",
            },
        )
        attrs, __ = self.instance._get_button_attrs(mock_tool)
        self.assertEqual(attrs["title"], "real title")

    def test_get_button_attrs_gets_set(self):
        mock_tool = type(
            "mock_tool",
            (object,),
            {"attrs": {"class": "class"}, "short_description": "description"},
        )
        attrs, __ = self.instance._get_button_attrs(mock_tool)
        self.assertEqual(attrs["class"], "class")
        self.assertEqual(attrs["title"], "description")

    def test_get_button_attrs_custom_attrs_get_partitioned(self):
        mock_tool = type("mock_tool", (object,), {"attrs": {"nonstandard": "wombat"}})
        attrs, custom = self.instance._get_button_attrs(mock_tool)
        self.assertEqual(custom["nonstandard"], "wombat")


class BaseActionViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.view = BaseActionView()

    @mock.patch("one.utils.contrib.admin.messages")
    def test_message_user_proxies_messages(self, mock_messages):
        self.view.message_user("request", "message")
        mock_messages.info.assert_called_once_with("request", "message")


class DecoratorTest(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

        self.poll_1 = Poll.objects.create(question="Do you like me?", pub_date="2012-10-20T18:20:35")
        self.poll_2 = Poll.objects.create(question="Do you wanna build a snow man?", pub_date="2012-10-20T18:20:38")
        self.choice_1 = Choice.objects.create(poll=self.poll_1, choice_text="Yes", votes=0)
        self.choice_2 = Choice.objects.create(poll=self.poll_1, choice_text="No", votes=100)

        # WISHLIST don't depend on fixture
        self.obj = self.poll_1
        self.queryset = Poll.objects.all()

    def test_trivial(self):
        # setup
        def myfunc(foo, bar, queryset):
            return queryset

        # make sure my test function outputs the third arg
        self.assertEqual(myfunc(None, None, "foo"), "foo")
        # or the `queryset` kwarg
        self.assertEqual(myfunc(None, None, queryset="bar"), "bar")

    def test_decorated(self):
        # setup
        @takes_instance_or_queryset
        def myfunc(foo, bar, queryset):
            return queryset

        # passing in an instance yields a queryset (using positional args)
        queryset = myfunc(None, None, self.obj)
        # the resulting queryset only has one item, and it's self.obj
        self.assertEqual(queryset.get(), self.obj)

        # passing in a queryset yields the same queryset
        queryset = myfunc(None, None, self.queryset)
        self.assertEqual(queryset, self.queryset)

        # passing in an instance yields a queryset (using keyword args)
        queryset = myfunc(None, None, queryset=self.obj)
        # the resulting queryset only has one item, and it's self.obj
        self.assertEqual(queryset.get(), self.obj)


class DecoratorActionTest(TestCase):
    def test_decorated(self):
        # setup
        @action(description="First action of this admin site.")
        def action_1(modeladmin, request, queryset):
            pass

        @action(permissions=["do_action2"])
        def action_2(modeladmin, request, queryset):
            pass

        @action(label="Third action")
        def action_3(modeladmin, request, queryset):
            pass

        @action(
            attrs={
                "class": "addlink",
            }
        )
        def action_4(modeladmin, request, queryset):
            pass

        self.assertEqual(action_1.short_description, "First action of this admin site.")
        self.assertEqual(action_2.allowed_permissions, ["do_action2"])
        self.assertEqual(action_3.label, "Third action")
        self.assertEqual(
            action_4.attrs,
            {
                "class": "addlink",
            },
        )


class CommentTests(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

    def test_action_on_a_model_with_uuid_pk_works(self):
        self.client.login(username="Superuser001", password="superuser001")
        comment = Comment.objects.create()
        comment_url = reverse("admin:tests_comment_change", args=(comment.pk,))
        action_url = f"/admin/tests/comment/{comment.pk}/actions/hodor/"
        # sanity check that url has an uuid
        self.assertIn("-", action_url)
        response = self.client.get(action_url)
        self.assertRedirects(response, comment_url)

    @mock.patch("one.utils.contrib.admin.ChangeActionView.get")
    def test_action_on_a_model_with_arbitrary_pk_works(self, mock_view):
        mock_view.return_value = HttpResponse()

        action_url = "/admin/tests/comment/{}/actions/hodor/".format(" i am a pk ")

        self.client.login(username="Superuser001", password="superuser001")
        self.client.get(action_url)

        self.assertTrue(mock_view.called)
        self.assertEqual(mock_view.call_args[1]["pk"], " i am a pk ")

    @mock.patch("one.utils.contrib.admin.ChangeActionView.get")
    def test_action_on_a_model_with_slash_in_pk_works(self, mock_view):
        mock_view.return_value = HttpResponse()
        action_url = "/admin/tests/comment/{}/actions/hodor/".format("pk/slash")

        self.client.login(username="Superuser001", password="superuser001")
        self.client.get(action_url)

        self.assertTrue(mock_view.called)
        self.assertEqual(mock_view.call_args[1]["pk"], "pk/slash")


class ExtraTests(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

    def test_action_on_a_model_with_complex_id(self):
        related_data = RelatedData.objects.create(id=1, extra_data="extra_data")
        related_data_url = reverse("admin:tests_relateddata_change", args=(related_data.pk,))
        action_url = f"/admin/tests/relateddata/{quote(related_data.pk)}/actions/fill_up/"

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(action_url)
        self.assertNotEqual(response.status_code, 404)
        self.assertRedirects(response, related_data_url)


class ChangeTests(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()

        self.poll_1 = Poll.objects.create(question="Do you like me?", pub_date="2012-10-20T18:20:35")
        self.poll_2 = Poll.objects.create(question="Do you wanna build a snow man?", pub_date="2012-10-20T18:20:38")
        self.choice_1 = Choice.objects.create(poll=self.poll_1, choice_text="Yes", votes=0)
        self.choice_2 = Choice.objects.create(poll=self.poll_1, choice_text="No", votes=100)

    def test_setup(self):
        """
        Test setup
        """
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(Poll.objects.all().count(), 2)
        self.assertEqual(Choice.objects.all().count(), 2)

    def test_buttons_load(self):
        url = "/admin/tests/choice/"
        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(url)
        self.assertIn("objectactions", response.context_data)
        self.assertIn("Delete all", response.rendered_content)

    def test_changelist_template_context(self):
        url = reverse("admin:tests_poll_changelist")
        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(url)
        self.assertIn("objectactions", response.context_data)
        self.assertIn("tools_view_name", response.context_data)
        self.assertIn("foo", response.context_data)

    def test_changelist_action_view(self):
        url = "/admin/tests/choice/actions/delete_all/"
        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(url)
        self.assertRedirects(response, "/admin/tests/choice/")

    def test_changelist_nonexistent_action(self):
        url = "/admin/tests/choice/actions/xyzzy/"
        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_changelist_can_remove_action(self):
        poll = self.poll_1
        poll.id = None
        poll.question = "Do you like me"
        poll.save()
        self.assertFalse(poll.question.endswith("?"))
        admin_change_url = reverse("admin:tests_poll_change", args=(poll.pk,))
        action_url = f"/admin/tests/poll/{poll.id}/actions/question_mark/"

        self.client.login(username="Superuser001", password="superuser001")

        # button is in the admin
        response = self.client.get(admin_change_url)
        self.assertIn(action_url, response.rendered_content)

        response = self.client.get(action_url)  # Click on the button
        self.assertRedirects(response, admin_change_url)

        # button is not in the admin anymore
        response = self.client.get(admin_change_url)
        self.assertNotIn(action_url, response.rendered_content)


class ChangeListTests(TestCase):
    def setUp(self):
        """
        Create users, categories and entries
        """
        super().setUp()  # required
        self.client = Client(self.tenant)  # required

        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_1.is_staff = True
        self.superuser_1.is_active = True
        self.superuser_1.save()
        self.poll_1 = Poll.objects.create(question="Do you like me?", pub_date="2012-10-20T18:20:35")

    def test_changelist_template_context(self):
        poll = self.poll_1
        url = reverse("admin:tests_poll_change", args=(poll.pk,))

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(url)

        self.assertIn("objectactions", response.context_data)
        self.assertIn("tools_view_name", response.context_data)
        self.assertIn("foo", response.context_data)

    def test_redirect_back_from_secondary_admin(self):
        poll = self.poll_1
        admin_change_url = reverse("admin:tests_poll_change", args=(poll.pk,), current_app="support")
        action_url = f"/support/tests/poll/{poll.pk}/actions/question_mark/"
        self.assertTrue(admin_change_url.startswith("/support/"))

        self.client.login(username="Superuser001", password="superuser001")

        response = self.client.get(action_url)
        self.assertRedirects(response, admin_change_url)
