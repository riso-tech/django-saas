from django.urls import path

from .views import homepage_add_view

app_name = "flatpages"

urlpatterns = [path("add/", homepage_add_view, name="homepage_add")]
