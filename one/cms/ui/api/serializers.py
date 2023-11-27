from rest_framework.serializers import ModelSerializer

from ..models import Template, Theme


class TemplateSerializer(ModelSerializer[Template]):
    class Meta:
        model = Template
        fields = ["id", "name", "description", "content", "thumbnail", "icon"]


class TemplateNestedSerializer(ModelSerializer[Template]):
    class Meta:
        model = Template
        fields = ["id", "name", "description", "thumbnail", "icon"]


class ThemeSerializer(ModelSerializer[Theme]):
    templates = TemplateNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Theme
        fields = ["id", "name", "description", "thumbnail", "template_name", "templates"]
