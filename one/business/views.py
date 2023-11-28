from urllib.parse import quote

from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Context, Engine, TemplateDoesNotExist, loader
from django.urls import reverse
from django.views.decorators.csrf import requires_csrf_token

from .constants import ERROR_BUSINESS_NOT_FOUND_TEMPLATE_NAME, ERROR_PAGE_TEMPLATE

# These views can be called when CsrfViewMiddleware.process_view() not run,
# therefore need @requires_csrf_token in case the template needs
# {% csrf_token %}.


@requires_csrf_token
def business_not_found(request, exception, template_name=ERROR_BUSINESS_NOT_FOUND_TEMPLATE_NAME):
    if request.method == "GET":
        exception_repr = exception.__class__.__name__
        # Try to get an "interesting" exception message, if any (and not the ugly
        # Resolver404 dictionary)
        try:
            message = exception.args[0]
        except (AttributeError, IndexError):
            pass
        else:
            if isinstance(message, str):
                exception_repr = message
        context = {
            "request_path": quote(request.path),
            "exception": exception_repr,
        }
        try:
            template = loader.get_template(template_name)
            body = template.render(context, request)
        except TemplateDoesNotExist:
            if template_name != ERROR_BUSINESS_NOT_FOUND_TEMPLATE_NAME:
                # Reraise if it's a missing custom template.
                raise
            # Render template (even though there are no substitutions) to allow
            # inspecting the context in tests.
            template = Engine().from_string(
                ERROR_PAGE_TEMPLATE
                % {
                    "title": "Not Found",
                    "details": "The requested resource was not found on this server.",
                },
            )
            body = template.render(Context(context))
        return HttpResponse(body)
    return redirect(reverse("home"))
