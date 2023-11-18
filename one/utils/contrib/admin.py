from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import TabularInline
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


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
