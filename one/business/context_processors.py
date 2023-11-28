from .constants import BUSINESS_TENANT_REQUIRED_ERROR


def tenant_constants(request):
    """Expose some constants from django-tenant in templates."""
    return {"BUSINESS_TENANT_REQUIRED_ERROR": BUSINESS_TENANT_REQUIRED_ERROR}
