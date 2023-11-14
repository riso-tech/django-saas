from django.contrib import admin

from .models import Category, Entry


@admin.register(Category)
class CategoryOptions(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    list_display_links = ("name",)


@admin.register(Entry)
class EntryOptions(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "category_alt",
        "user",
    )
    list_display_links = ("title",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
