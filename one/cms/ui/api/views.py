from rest_framework.generics import ListAPIView, RetrieveAPIView

from ...permissions import IsSuperUser
from ..models import Template, Theme
from .serializers import TemplateSerializer, ThemeSerializer


class ThemeAPIView(ListAPIView):
    serializer_class = ThemeSerializer
    queryset = Theme.objects.all()
    permission_classes = [IsSuperUser]


class TemplateAPIView(RetrieveAPIView):
    serializer_class = TemplateSerializer
    queryset = Template.objects.all()
    permission_classes = [IsSuperUser]
