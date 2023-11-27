from django.contrib import admin
from django.contrib.flatpages.models import FlatPage

admin.site.unregister(FlatPage)
