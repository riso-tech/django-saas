from functools import wraps
from itertools import chain

from django.contrib import messages
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import TabularInline
from django.contrib.admin.utils import unquote
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.http.response import HttpResponseBase
from django.urls import re_path, reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin


class BaseDjangoObjectActions:
    """
    ModelAdmin mixin to add new actions just like adding admin actions.

    Attributes
    ----------
    model : django.db.models.Model
        The Django Model these actions work on. This is populated by Django.
    change_actions : list of str
        Write the names of the methods of the model admin that can be used as
        tools in the change view.
    changelist_actions : list of str
        Write the names of the methods of the model admin that can be used as
        tools in the changelist view.
    tools_view_name : str
        The name of the Django Object Actions admin view, including the 'admin'
        namespace. Populated by `_get_action_urls`.
    """

    change_actions = []
    changelist_actions = []
    tools_view_name = None

    # EXISTING ADMIN METHODS MODIFIED
    #################################

    def get_urls(self):
        """Prepend `get_urls` with our own patterns."""
        urls = super().get_urls()
        return self._get_action_urls() + urls

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            {
                "objectactions": [
                    self._get_tool_dict(action) for action in self.get_change_actions(request, object_id, form_url)
                ],
                "tools_view_name": self.tools_view_name,
            }
        )
        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            {
                "objectactions": [self._get_tool_dict(action) for action in self.get_changelist_actions(request)],
                "tools_view_name": self.tools_view_name,
            }
        )
        return super().changelist_view(request, extra_context)

    # USER OVERRIDABLE
    ##################

    def get_change_actions(self, request, object_id, form_url):
        """
        Override this to customize what actions get to the change view.

        This takes the same parameters as `change_view`.

        For example, to restrict actions to superusers, you could do:

            class ChoiceAdmin(DjangoObjectActions, admin.ModelAdmin):
                def get_change_actions(self, request, **kwargs):
                    if request.user.is_superuser:
                        return super(ChoiceAdmin, self).get_change_actions(
                            request, **kwargs
                        )
                    return []
        """
        return self.change_actions

    def get_changelist_actions(self, request):
        """
        Override this to customize what actions get to the changelist view.
        """
        return self.changelist_actions

    # INTERNAL METHODS
    ##################

    def _get_action_urls(self):
        """Get the url patterns that route each action to a view."""
        actions = {}

        model_name = self.model._meta.model_name
        # e.g.: polls_poll
        base_url_name = f"{self.model._meta.app_label}_{model_name}"
        # e.g.: polls_poll_actions
        model_actions_url_name = "%s_actions" % base_url_name

        self.tools_view_name = "admin:" + model_actions_url_name

        # WISHLIST use get_change_actions and get_changelist_actions
        # TODO separate change and changelist actions
        for action in chain(self.change_actions, self.changelist_actions):
            actions[action] = getattr(self, action)
        return [
            # change, supports the same pks the admin does
            # https://github.com/django/django/blob/stable/1.10.x/django/contrib/admin/options.py#L555
            re_path(
                r"^(?P<pk>.+)/actions/(?P<tool>\w+)/$",
                self.admin_site.admin_view(  # checks permissions
                    ChangeActionView.as_view(
                        model=self.model,
                        actions=actions,
                        back="admin:%s_change" % base_url_name,
                        current_app=self.admin_site.name,
                    )
                ),
                name=model_actions_url_name,
            ),
            # changelist
            re_path(
                r"^actions/(?P<tool>\w+)/$",
                self.admin_site.admin_view(  # checks permissions
                    ChangeListActionView.as_view(
                        model=self.model,
                        actions=actions,
                        back="admin:%s_changelist" % base_url_name,
                        current_app=self.admin_site.name,
                    )
                ),
                # Dupe name is fine. https://code.djangoproject.com/ticket/14259
                name=model_actions_url_name,
            ),
        ]

    def _get_tool_dict(self, tool_name):
        """Represents the tool as a dict with extra meta."""
        tool = getattr(self, tool_name)
        standard_attrs, custom_attrs = self._get_button_attrs(tool)
        return dict(
            name=tool_name,
            label=getattr(tool, "label", tool_name.replace("_", " ").capitalize()),
            standard_attrs=standard_attrs,
            custom_attrs=custom_attrs,
        )

    def _get_button_attrs(self, tool):
        """
        Get the HTML attributes associated with a tool.

        There are some standard attributes (class and title) that the template
        will always want. Any number of additional attributes can be specified
        and passed on. This is kinda awkward and due for a refactor for
        readability.
        """
        attrs = getattr(tool, "attrs", {})
        # href is not allowed to be set. should an exception be raised instead?
        if "href" in attrs:
            attrs.pop("href")
        # title is not allowed to be set. should an exception be raised instead?
        # `short_description` should be set instead to parallel django admin
        # actions
        if "title" in attrs:
            attrs.pop("title")
        default_attrs = {
            "class": attrs.get("class", ""),
            "title": getattr(tool, "short_description", ""),
        }
        standard_attrs = {}
        custom_attrs = {}
        for k, v in dict(default_attrs, **attrs).items():
            if k in default_attrs:
                standard_attrs[k] = v
            else:
                custom_attrs[k] = v
        return standard_attrs, custom_attrs


class DjangoObjectActions(BaseDjangoObjectActions):
    pass


class BaseActionView(View):
    """
    The view that runs a change/changelist action callable.

    Attributes
    ----------
    back : str
        The urlpattern name to send users back to. This is set in
        `_get_action_urls` and turned into a url with the `back_url` property.
    model : django.db.model.Model
        The model this tool operates on.
    actions : dict
        A mapping of action names to callables.
    """

    back = None
    model = None
    actions = None
    current_app = None

    @property
    def view_args(self):
        """
        tuple: The argument(s) to send to the action (excluding `request`).

        Change actions are called with `(request, obj)` while changelist
        actions are called with `(request, queryset)`.
        """
        raise NotImplementedError

    @property
    def back_url(self):
        """
        str: The url path the action should send the user back to.

        If an action does not return a http response, we automagically send
        users back to either the change or the changelist page.
        """
        raise NotImplementedError

    def get(self, request, tool, **kwargs):
        # Fix for case if there are special symbols in object pk
        for k, v in self.kwargs.items():
            self.kwargs[k] = unquote(v)

        try:
            view = self.actions[tool]
        except KeyError:
            raise Http404("Action does not exist")

        ret = view(request, *self.view_args)
        if isinstance(ret, HttpResponseBase):
            return ret

        return HttpResponseRedirect(self.back_url)

    # HACK to allow POST requests too
    post = get

    def message_user(self, request, message):
        """
        Mimic Django admin actions's `message_user`.

        Like the second example:
        https://docs.djangoproject.com/en/1.9/ref/contrib/admin/actions/#custom-admin-action
        """
        messages.info(request, message)


class ChangeActionView(SingleObjectMixin, BaseActionView):
    @property
    def view_args(self):
        return (self.get_object(),)

    @property
    def back_url(self):
        return reverse(self.back, args=(self.kwargs["pk"],), current_app=self.current_app)


class ChangeListActionView(MultipleObjectMixin, BaseActionView):
    @property
    def view_args(self):
        return (self.get_queryset(),)

    @property
    def back_url(self):
        return reverse(self.back, current_app=self.current_app)


def takes_instance_or_queryset(func):
    """Decorator that makes standard Django admin actions compatible."""

    @wraps(func)
    def decorated_function(self, request, queryset):
        # func follows the prototype documented at:
        # https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#writing-action-functions
        if not isinstance(queryset, QuerySet):
            try:
                # Django >=1.8
                queryset = self.get_queryset(request).filter(pk=queryset.pk)
            except AttributeError:
                try:
                    # Django >=1.6,<1.8
                    model = queryset._meta.model
                except AttributeError:  # pragma: no cover
                    # Django <1.6
                    model = queryset._meta.concrete_model
                queryset = model.objects.filter(pk=queryset.pk)
        return func(self, request, queryset)

    return decorated_function


def action(function=None, *, permissions=None, description=None, label=None, attrs=None):
    """
    Conveniently add attributes to an action function:

        @action(
            permissions=['publish'],
            description='Mark selected stories as published',
            label='Publish'
        )
        def make_published(self, request, queryset):
            queryset.update(status='p')

    This is equivalent to setting some attributes (with the original, longer
    names) on the function directly:

        def make_published(self, request, queryset):
            queryset.update(status='p')
        make_published.allowed_permissions = ['publish']
        make_published.short_description = 'Mark selected stories as published'
        make_published.label = 'Publish'

    This is the django-object-actions equivalent of
    https://docs.djangoproject.com/en/stable/ref/contrib/admin/actions/#django.contrib.admin.action
    """

    def decorator(func):
        if permissions is not None:
            func.allowed_permissions = permissions
        if description is not None:
            func.short_description = description
        if label is not None:
            func.label = label
        if attrs is not None:
            func.attrs = attrs
        return func

    if function is None:
        return decorator
    else:
        return decorator(function)


class GenericRelationAdmin(BaseModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # noqa
        if db_field.name == "content_type":
            if hasattr(self.model, "BASE_MODEL_ALLOWED"):
                q_objects = Q()
                for white_class in self.model.BASE_MODEL_ALLOWED:
                    q_objects |= Q(**white_class)
                kwargs["queryset"] = ContentType.objects.filter(q_objects)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ModelAdmin(BaseModelAdmin):
    ordering = ("-created",)
    readonly_fields = ("created", "modified")

    # override save_model method to add creator
    def save_model(self, request, obj, form, change):
        user = request.user
        if not obj.pk:
            obj.creator = user
        obj.last_modified_by = user
        super().save_model(request, obj, form, change)

    # override save_formset method to add creator
    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        for _form in formset:
            if not _form.cleaned_data.get("DELETE", False) and hasattr(_form.instance, "creator"):
                instance = _form.instance
                if instance.creator is None:
                    instance.creator = request.user
                instance.last_modified_by = request.user
                instance.save()

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return ("id",) + list_display

    def get_list_display_links(self, request, list_display):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().
        """
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            # Use only the first item in list_display as link
            return list(list_display)[0:2]


class MasterModelAdmin(ModelAdmin):
    date_hierarchy = "created"
    readonly_fields = ("created", "modified", "creator", "last_modified_by")

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {"fields": ("code", "name", "description")}),
                (_("User Stamped"), {"fields": ("creator", "last_modified_by")}),
                (_("Time Stamped"), {"fields": ("created", "modified")}),
            )
        else:
            return ((None, {"fields": ("name", "code", "description")}),)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj:
            return readonly_fields + ("code",)  # noqa
        else:
            return readonly_fields

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return list_display + ("code", "is_active")


class GenericRelationTabularInline(TabularInline):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):  # noqa
        if hasattr(self.model, "BASE_MODEL_ALLOWED"):
            q_objects = Q()
            for white_class in self.model.BASE_MODEL_ALLOWED:
                q_objects |= Q(**white_class)
            kwargs["queryset"] = ContentType.objects.filter(q_objects)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
