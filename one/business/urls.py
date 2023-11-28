from django.urls import path

from .views import business_add_view

app_name = "business"

urlpatterns = [path("add/", business_add_view, name="tenant_add")]
