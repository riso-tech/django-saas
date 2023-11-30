from django.forms import ModelForm

from .models import Page


class CreateHomePageForm(ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
