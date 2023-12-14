from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect, requires_csrf_token

from ..settings import ADMIN_URL, CMS_ENABLED
from .models import Page as FlatPage

DEFAULT_TEMPLATE = "flatpages/default.html"


@requires_csrf_token
def homepage_not_found(request):
    template_name = "cms/homepage_not_found.html"
    return render(request, template_name, {})


def flatpage(request, url):
    """
    Public interface to the flat page view.

    Models: `flatpages.flatpages`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`flatpages/default.html` if template_name is not defined.
    Context:
        flatpage
            `flatpages.flatpages` object
    """
    if not CMS_ENABLED:
        return redirect(ADMIN_URL)

    Site.objects.clear_cache()
    if not url.startswith("/"):
        url = "/" + url

    site_id = get_current_site(request).id

    try:
        f = get_object_or_404(FlatPage, url=url, sites=site_id)
    except Http404:
        if not url.endswith("/") and settings.APPEND_SLASH:
            url += "/"
            f = get_object_or_404(FlatPage, url=url, sites=site_id)
            return HttpResponsePermanentRedirect("%s/" % request.path)
        else:
            return homepage_not_found(request)
    return render_flatpage(request, f)


@csrf_protect
def render_flatpage(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(request.path)
    if f.template_name:
        template = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        template = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.content)

    return HttpResponse(template.render({"flatpage": f, "meta": f.as_meta(request)}, request))
