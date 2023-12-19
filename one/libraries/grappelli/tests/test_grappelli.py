from django.contrib.admin.widgets import url_params_from_lookup_dict
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.html import escape
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django_tenants.test.client import TenantClient as Client

from one.tests.models import Category, Entry
from one.tests.tests.cases import FastTenantTestCase as TestCase

from ..templatetags.grp_tags import switch_user_dropdown

User = get_user_model()


@override_settings(GRAPPELLI_AUTOCOMPLETE_LIMIT=10)
@override_settings(GRAPPELLI_AUTOCOMPLETE_SEARCH_FIELDS={})
class GrappelliTests(TestCase):
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
        self.superuser_2 = User.objects.create_superuser("Superuser002", "superuser002@example.com", "superuser002")
        self.superuser_2.is_staff = True
        self.superuser_2.is_active = True
        self.superuser_2.save()
        self.editor_1 = User.objects.create_user("Editor001", "editor001@example.com", "editor001")
        self.editor_1.is_staff = True
        self.editor_1.save()
        self.editor_2 = User.objects.create_user("Editor002", "editor002@example.com", "editor002")
        self.editor_2.is_staff = True
        self.editor_2.save()
        self.user_1 = User.objects.create_user("User001", "user001@example.com", "user001")
        self.user_1.is_staff = False
        self.user_1.save()

        # add permissions for editor001
        content_type = ContentType.objects.get_for_model(Category)
        permissions = Permission.objects.filter(content_type=content_type)
        assert permissions.exists()
        self.editor_1.user_permissions.set(permissions)

        # add categories
        for i in range(100):
            Category.objects.create(id=i + 1, name=f"Category No {i}")

        # add entries
        self.entry_superuser = Entry.objects.create(
            title="Entry Superuser", date=timezone.now(), user=self.superuser_1
        )
        self.entry_editor = Entry.objects.create(title="Entry Editor", date=timezone.now(), user=self.editor_1)
        # set to en to check error messages
        translation.activate("en")

    def test_setup(self):
        """
        Test setup
        """
        self.assertEqual(User.objects.all().count(), 5)
        self.assertEqual(Category.objects.all().count(), 100)
        self.assertEqual(Entry.objects.all().count(), 2)

    def test_related_lookup(self):
        """
        Test related lookup
        """
        self.client.login(username="User001", password="user001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": ""}])

        # ok
        response = self.client.get(
            "{}?object_id=1&app_label={}&model_name={}".format(reverse("grp_related_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "1", "label": "Category No 0 (1)", "safe": False}]
        )

        # ok (to_field)
        response = self.client.get(
            "{}?object_id=1&to_field=id&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "1", "label": "Category No 0 (1)", "safe": False}]
        )

        # ok (to_field)
        response = self.client.get(
            "{}?object_id=Category+No+0&to_field=name&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "Category No 0", "label": "Category No 0 (1)", "safe": False}]
        )

        # wrong object_id
        response = self.client.get(
            "{}?object_id=10000&app_label={}&model_name={}".format(reverse("grp_related_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "10000", "label": "?", "safe": False}])

        # wrong object_id (to_field)
        response = self.client.get(
            "{}?object_id=xxx&to_field=name&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "xxx", "label": "?", "safe": False}])

        # filtered queryset (single filter) fails
        response = self.client.get(
            "{}?object_id=1&app_label={}&model_name={}&query_string=id__gte=99".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "1", "label": "?", "safe": False}])

        # filtered queryset (single filter) works
        response = self.client.get(
            "{}?object_id=100&app_label={}&model_name={}&query_string=id__gte=99".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "100", "label": "Category No 99 (100)", "safe": False}]
        )

        # filtered queryset (IN statement) fails
        query_params = {
            "object_id": 1,
            "app_label": "tests",
            "model_name": "category",
            "query_string": urlencode(url_params_from_lookup_dict({"id__in": [99, 100]})),
        }
        query_string = urlencode(query_params)
        response = self.client.get("{}?{}".format(reverse("grp_related_lookup"), query_string))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "1", "label": "?", "safe": False}])

        # filtered queryset (IN statement) works
        query_params = {
            "object_id": 100,
            "app_label": "tests",
            "model_name": "category",
            "query_string": urlencode(url_params_from_lookup_dict({"id__in": [99, 100]})),
        }
        query_string = urlencode(query_params)
        response = self.client.get("{}?{}".format(reverse("grp_related_lookup"), query_string))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "100", "label": "Category No 99 (100)", "safe": False}]
        )

        # filtered queryset (multiple filters) fails
        response = self.client.get(
            "{}?object_id=1&app_label={}&model_name={}&query_string=name__icontains=99:id__gte=99".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "1", "label": "?", "safe": False}])

        # filtered queryset (multiple filters) works
        response = self.client.get(
            "{}?object_id=100&app_label={}&model_name={}&query_string=name__icontains=99:id__gte=99".format(
                reverse("grp_related_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "100", "label": "Category No 99 (100)", "safe": False}]
        )

        # custom queryset (Superuser)
        response = self.client.get(
            "{}?object_id={}&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), self.entry_superuser.id, "tests", "entry"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [{"value": str(self.entry_superuser.id), "label": "Entry Superuser", "safe": False}],
        )
        response = self.client.get(
            "{}?object_id={}&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), self.entry_editor.id, "tests", "entry"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [{"value": str(self.entry_editor.id), "label": "Entry Editor", "safe": False}],
        )

        # custom queryset (Editor)
        # FIXME: this should fail, because the custom admin queryset
        # limits the entry to the logged in user (but we currently do not make use
        # of custom admin querysets)
        self.client.login(username="Editor001", password="editor001")
        response = self.client.get(
            "{}?object_id={}&app_label={}&model_name={}".format(
                reverse("grp_related_lookup"), self.entry_superuser.id, "tests", "entry"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [{"value": str(self.entry_superuser.id), "label": "Entry Superuser", "safe": False}],
        )

        # wrong app_label/model_name
        response = self.client.get("%s?object_id=1&app_label=false&model_name=false" % (reverse("grp_related_lookup")))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": ""}])
        response = self.client.get("%s?object_id=&app_label=false&model_name=false" % (reverse("grp_related_lookup")))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": ""}])

    def test_m2m_lookup(self):
        """
        Test M2M lookup
        """
        self.client.login(username="User001", password="user001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": ""}])

        # ok (single)
        response = self.client.get(
            "{}?object_id=1&app_label={}&model_name={}".format(reverse("grp_m2m_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), [{"value": "1", "label": "Category No 0 (1)", "safe": False}]
        )

        # wrong object_id (single)
        response = self.client.get(
            "{}?object_id=10000&app_label={}&model_name={}".format(reverse("grp_m2m_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": "10000", "label": "?", "safe": False}])

        # ok (multiple)
        response = self.client.get(
            "{}?object_id=1,2,3&app_label={}&model_name={}".format(reverse("grp_m2m_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "Category No 0 (1)", "safe": False},
                {"value": "2", "label": "Category No 1 (2)", "safe": False},
                {"value": "3", "label": "Category No 2 (3)", "safe": False},
            ],
        )

        # wrong object_id (multiple)
        response = self.client.get(
            "{}?object_id=1,10000,3&app_label={}&model_name={}".format(reverse("grp_m2m_lookup"), "tests", "category")
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "Category No 0 (1)", "safe": False},
                {"value": "10000", "label": "?", "safe": False},
                {"value": "3", "label": "Category No 2 (3)", "safe": False},
            ],
        )

        # filtered queryset (single filter) fails
        response = self.client.get(
            "{}?object_id=1,2,3&app_label={}&model_name={}&query_string=id__gte=99".format(
                reverse("grp_m2m_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "?", "safe": False},
                {"value": "2", "label": "?", "safe": False},
                {"value": "3", "label": "?", "safe": False},
            ],
        )

        # filtered queryset (single filter) works
        response = self.client.get(
            "{}?object_id=1,2,3&app_label={}&model_name={}&query_string=id__lte=3".format(
                reverse("grp_m2m_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "Category No 0 (1)", "safe": False},
                {"value": "2", "label": "Category No 1 (2)", "safe": False},
                {"value": "3", "label": "Category No 2 (3)", "safe": False},
            ],
        )

        # filtered queryset (multiple filters) fails
        response = self.client.get(
            "{}?object_id=1,2,3&app_label={}&model_name={}&query_string=name__icontains=99:id__gte=99".format(
                reverse("grp_m2m_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "?", "safe": False},
                {"value": "2", "label": "?", "safe": False},
                {"value": "3", "label": "?", "safe": False},
            ],
        )

        # filtered queryset (multiple filters) works
        response = self.client.get(
            "{}?object_id=1,2,3&app_label={}&model_name={}&query_string=name__icontains=Category:id__lte=3".format(
                reverse("grp_m2m_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [
                {"value": "1", "label": "Category No 0 (1)", "safe": False},
                {"value": "2", "label": "Category No 1 (2)", "safe": False},
                {"value": "3", "label": "Category No 2 (3)", "safe": False},
            ],
        )

    def test_autocomplete_lookup(self):
        """
        Test autocomplete lookup
        """
        self.client.login(username="User001", password="user001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(reverse("grp_related_lookup"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": ""}])

        # term not found
        response = self.client.get(
            "{}?term=XXXXXXXXXX&app_label={}&model_name={}".format(
                reverse("grp_autocomplete_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": None, "label": "0 results"}])

        # ok (99 finds the id and the title, therefore 2 results)
        response = self.client.get(
            "{}?term=Category No 99&app_label={}&model_name={}".format(
                reverse("grp_autocomplete_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [{"value": 99, "label": "Category No 98 (99)"}, {"value": 100, "label": "Category No 99 (100)"}],
        )

        # filtered queryset (single filter)
        response = self.client.get(
            "{}?term=Category&app_label={}&model_name={}&query_string=id__gte=99".format(
                reverse("grp_autocomplete_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            [{"value": 99, "label": "Category No 98 (99)"}, {"value": 100, "label": "Category No 99 (100)"}],
        )

        # filtered queryset (multiple filters)
        response = self.client.get(
            "{}?term=Category&app_label={}&model_name={}&query_string=name__icontains=99:id__gte=99".format(
                reverse("grp_autocomplete_lookup"), "tests", "category"
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), [{"value": 100, "label": "Category No 99 (100)"}])

    def test_switch_login(self):
        """
        Test login users
        """
        self.assertEqual(User.objects.all().count(), 5)
        self.assertEqual(Category.objects.all().count(), 100)

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(reverse("admin:tests_category_changelist"))
        self.assertEqual(response.status_code, 200)

        # template tag (Editor001, Editor002)
        t = switch_user_dropdown(response.context)
        t_cmp_1 = f"/grappelli/switch/user/{self.editor_1.id}/?redirect=/admin/tests/category/"
        t_cmp_2 = "Editor001"
        t_cmp_3 = f"/grappelli/switch/user/{self.editor_2.id}/?redirect=/admin/tests/category/"
        t_cmp_4 = "Editor002"
        self.assertIn(t_cmp_1, t)
        self.assertIn(t_cmp_2, t)
        self.assertIn(t_cmp_3, t)
        self.assertIn(t_cmp_4, t)

        self.client.login(username="Superuser002", password="superuser002")
        response = self.client.get(reverse("admin:tests_category_changelist"))
        self.assertEqual(response.status_code, 200)

        # template tag (Editor001, Editor002)
        t = switch_user_dropdown(response.context)
        t_cmp_1 = f"/grappelli/switch/user/{self.editor_1.id}/?redirect=/admin/tests/category/"
        t_cmp_2 = "Editor001"
        t_cmp_3 = f"/grappelli/switch/user/{self.editor_2.id}/?redirect=/admin/tests/category/"
        t_cmp_4 = "Editor002"
        self.assertIn(t_cmp_1, t)
        self.assertIn(t_cmp_2, t)
        self.assertIn(t_cmp_3, t)
        self.assertIn(t_cmp_4, t)

        self.client.login(username="Editor001", password="editor001")
        response = self.client.get(reverse("admin:tests_category_changelist"))
        self.assertEqual(response.status_code, 200)

        # template tag (empty)
        t = switch_user_dropdown(response.context)
        t_cmp = ""
        self.assertEqual(t, t_cmp)

        self.client.login(username="Editor002", password="editor002")
        response = self.client.get(reverse("admin:tests_category_changelist"))
        self.assertEqual(response.status_code, 403)

        self.client.login(username="User001", password="user001")
        response = self.client.get(reverse("admin:tests_category_changelist"), follow=True)
        self.assertEqual(response.status_code, 200)  # redirect to login, FIXME: better testing

    def test_switch_superuser001_superuser002(self):
        """
        Test switching from superuser001 to superuser002

        That should not work, because one superuser is not allowed to login
        as another superuser (given the standard grappelli settings)
        """
        original_user = User.objects.get(username="Superuser001")
        target_user = User.objects.get(username="Superuser002")

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(
            "{}?redirect={}".format(
                reverse("grp_switch_user", args=[target_user.id]), reverse("admin:tests_category_changelist")
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([m.message for m in list(response.context["messages"])], [_("Permission denied.")])
        self.assertEqual(self.client.session.get("original_user", None), None)
        self.assertEqual(int(self.client.session["_auth_user_id"]), original_user.pk)

    def test_switch_superuser001_editor001(self):
        """
        Test switching from superuser001 to Editor001

        That should work.
        """
        original_user = User.objects.get(username="Superuser001")
        target_user = User.objects.get(username="Editor001")

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(
            "{}?redirect={}".format(
                reverse("grp_switch_user", args=[target_user.id]), reverse("admin:tests_category_changelist")
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.session.get("original_user", None),
            {"id": original_user.id, "username": original_user.username},
        )
        self.assertEqual(int(self.client.session["_auth_user_id"]), target_user.pk)

        # template tag (Superuser001, Editor001, Editor002)
        # now we have an additional list element with the original user, Superuser001
        t = switch_user_dropdown(response.context)
        t_cmp_1 = f"/grappelli/switch/user/{self.superuser_1.id}/?redirect=/admin/tests/category/"
        t_cmp_2 = "Superuser001"
        t_cmp_3 = f"/grappelli/switch/user/{self.editor_1.id}/?redirect=/admin/tests/category/"
        t_cmp_4 = "Editor001"
        t_cmp_5 = f"/grappelli/switch/user/{self.editor_2.id}/?redirect=/admin/tests/category/"
        t_cmp_6 = "Editor002"
        self.assertIn(t_cmp_1, t)
        self.assertIn(t_cmp_2, t)
        self.assertNotIn(t_cmp_3, t)
        self.assertNotIn(t_cmp_4, t)
        self.assertIn(t_cmp_5, t)
        self.assertIn(t_cmp_6, t)

        # switch back to superuser
        response = self.client.get(
            "{}?redirect={}".format(
                reverse("grp_switch_user", args=[original_user.id]), reverse("admin:tests_category_changelist")
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("original_user", None), None)
        self.assertEqual(int(self.client.session["_auth_user_id"]), original_user.pk)

    def test_switch_superuser001_user001(self):
        """
        Test switching from superuser001 to user001

        That should not work, because user001 is not found
        """
        original_user = User.objects.get(username="Superuser001")
        target_user = User.objects.get(username="User001")

        self.client.login(username="Superuser001", password="superuser001")
        response = self.client.get(
            "{}?redirect={}".format(
                reverse("grp_switch_user", args=[target_user.id]), reverse("admin:tests_category_changelist")
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [m.message for m in list(response.context["messages"])],
            [
                _("%(name)s object with primary key %(key)r does not exist.")
                % {"name": "User", "key": escape(target_user.id)}
            ],
        )
        self.assertEqual(self.client.session.get("original_user", None), None)
        self.assertEqual(int(self.client.session["_auth_user_id"]), original_user.pk)

    def test_switch_editor001_user001(self):
        """
        Test switching from editor001 to user001

        That should not work, because editor001 is not a superuser
        """
        original_user = User.objects.get(username="Editor001")
        target_user = User.objects.get(username="User001")

        self.client.login(username="Editor001", password="editor001")
        response = self.client.get(
            "{}?redirect={}".format(
                reverse("grp_switch_user", args=[target_user.id]), reverse("admin:tests_category_changelist")
            ),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual([m.message for m in list(response.context["messages"])], [_("Permission denied.")])
        self.assertEqual(self.client.session.get("original_user", None), None)
        self.assertEqual(int(self.client.session["_auth_user_id"]), original_user.pk)
