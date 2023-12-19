from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import Template, Theme


@admin.register(Theme)
class ThemeAdmin(ModelAdmin):
    pass


@admin.register(Template)
class TemplateAdmin(ModelAdmin):
    pass
