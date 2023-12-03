from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token
from django_tenants.middleware.main import TenantMainMiddleware as BaseTenantMainMiddleware
from django_tenants.utils import get_public_schema_name, get_tenant_model, schema_context

from one.utils.call_command import call_command


@requires_csrf_token
def business_not_found(request, context):
    template_name = "business_not_found.html"
    return render(request, template_name, context)


class TenantMainMiddleware(BaseTenantMainMiddleware):
    BusinessTenantNotFound = Http404

    def process_request(self, request):
        if settings.STATIC_URL not in request.path:
            tenant_model = get_tenant_model()
            if not tenant_model.objects.exclude(schema_name=get_public_schema_name()).exists():
                context = {}

                if request.method == "POST":
                    params = request.POST
                    schema_name = params["schema_name"]

                    tenant_response, tenant_status = call_command(
                        "create_tenant",
                        {
                            "name": params["name"],
                            "code": params["code"],
                            "description": params["description"],
                            "schema_name": params["schema_name"],
                            "is_active": True if params["is_active"] == "on" else False,
                            "domain_domain": params["domain"],
                            "domain_is_primary": True if params["is_primary"] == "on" else False,
                        },
                    )
                    context["tenant_response"] = tenant_response
                    context["tenant_status"] = tenant_status

                    if tenant_status:
                        user_response, user_status = call_command(
                            "create_tenant_superuser",
                            {
                                "schema_name": params["schema_name"],
                                "email": params["email"],
                                "username": params["username"],
                                "no_input": "",
                            },
                        )
                        context["user_response"] = user_response
                        context["user_status"] = user_status
                        if user_status:
                            with schema_context(schema_name):
                                from django.contrib.auth import get_user_model

                                user = get_user_model().objects.filter(username=params["username"]).first()
                                user.set_password(params["password1"])
                                user.save()

                                from django.contrib.sites.models import Site

                                Site.objects.update(domain=params["domain"], name=params["name"])

                        return redirect(reverse("home"))

                return business_not_found(request, context)

            super().process_request(request)
