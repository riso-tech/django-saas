from rest_framework.serializers import ModelSerializer

from ..models import Page as FlatPage


class FlatPageUpdateSerializer(ModelSerializer[FlatPage]):
    class Meta:
        model = FlatPage
        fields = ["content"]


class FlatPageMetaUpdateSerializer(ModelSerializer[FlatPage]):
    class Meta:
        model = FlatPage
        fields = ["description", "keywords"]


class FlatPagePublishSerializer(ModelSerializer[FlatPage]):
    class Meta:
        model = FlatPage
        fields = ["published"]


class FlatPageCreateSerializer(ModelSerializer[FlatPage]):
    class Meta:
        model = FlatPage
        fields = ["url", "title", "template_name", "sites"]
