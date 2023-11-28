from django.shortcuts import render
from django.views.decorators.csrf import requires_csrf_token
from django.views.generic import CreateView

from one.business.forms import CreateTenantForm


@requires_csrf_token
def business_not_found(request):
    template_name = "business_required.html"
    context = {}
    create_tenant_form = CreateTenantForm()
    context["form"] = create_tenant_form
    return render(request, template_name, context)


class BusinessAddView(CreateView):
    template_name = "business_required.html"


business_add_view = BusinessAddView.as_view()
