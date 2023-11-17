from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from one.tests.models import Category

from ..templatetags.grp_tags import switch_user_dropdown

User = get_user_model()


@override_settings(GRAPPELLI_SWITCH_USER_ORIGINAL=lambda user: user.is_superuser)
@override_settings(GRAPPELLI_SWITCH_USER_TARGET=lambda original_user, user: user.is_staff and not user.is_superuser)
class SwitchTests(TestCase):
    def setUp(self):
        """
        Create superusers and editors
        """
        self.superuser_1 = User.objects.create_superuser("Superuser001", "superuser001@example.com", "superuser001")
        self.superuser_2 = User.objects.create_superuser("Superuser002", "superuser002@example.com", "superuser002")
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
        assert permissions.count() > 0
        self.editor_1.user_permissions.set(permissions)

        # add categories
        for i in range(100):
            Category.objects.create(name="Category No %s" % (i))

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
        self.assertIn(t_cmp_3, t)
        self.assertIn(t_cmp_4, t)
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
