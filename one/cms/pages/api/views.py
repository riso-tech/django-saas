from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet

from ...permissions import IsSuperUser
from ..models import Page as FlatPage
from .serializers import (
    FlatPageCreateSerializer,
    FlatPageMetaUpdateSerializer,
    FlatPagePublishSerializer,
    FlatPageUpdateSerializer,
)


class FlatPageViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = FlatPageCreateSerializer
    queryset = FlatPage.objects.all()
    permission_classes = [IsSuperUser]

    def create(self, request, *args, **kwargs):
        self.serializer_class = FlatPageCreateSerializer
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = FlatPageUpdateSerializer
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], url_path="update-meta")
    def update_meta(self, request, *args, **kwargs):
        self.serializer_class = FlatPageMetaUpdateSerializer
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"])
    def publish(self, request, *args, **kwargs):
        self.serializer_class = FlatPagePublishSerializer
        return super().update(request, *args, **kwargs)
