from django.conf import settings
from django.http import Http404
from django_tenants.middleware.main import TenantMainMiddleware as BaseTenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model

from .views import business_not_found


class TenantMainMiddleware(BaseTenantMainMiddleware):
    BusinessTenantNotFound = Http404

    def process_request(self, request):
        if settings.STATIC_URL not in request.path:
            tenant_model = get_tenant_model()
            if not tenant_model.objects.exclude(schema_name=get_public_schema_name()).exists():
                return business_not_found(request)

        super().process_request(request)
