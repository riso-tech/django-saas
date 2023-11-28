from django.http import Http404
from django_tenants.middleware.main import TenantMainMiddleware as BaseTenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model

from .constants import BUSINESS_TENANT_REQUIRED_ERROR
from .views import business_not_found


class TenantMainMiddleware(BaseTenantMainMiddleware):
    BusinessTenantNotFound = Http404

    def process_request(self, request):
        tenant_model = get_tenant_model()
        if not tenant_model.objects.exclude(schema_name=get_public_schema_name()).exists():
            return business_not_found(request, self.BusinessTenantNotFound(BUSINESS_TENANT_REQUIRED_ERROR))

        super().process_request(request)
