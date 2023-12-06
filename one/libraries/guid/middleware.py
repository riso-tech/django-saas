import asyncio
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Union

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.utils.decorators import sync_and_async_middleware

from .config import settings
from .context import guid
from .utils import get_id_from_header, ignored_url

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger("django_guid")


def process_incoming_request(request: "HttpRequest") -> None:
    """
    Processes an incoming request. This function is called before the view and later middleware.
    Same logic for both async and sync views.
    """
    if not ignored_url(request=request):
        # Process request and store the GUID in a contextvar
        guid.set(get_id_from_header(request))

        # Run all integrations
        for integration in settings.integrations:
            logger.debug("Running integration: `%s`", integration.identifier)
            integration.run(guid=guid.get())


def process_outgoing_request(response: "HttpResponse", request: "HttpRequest") -> None:
    """
    Process an outgoing request. This function is called after the view and before later middleware.
    """
    if not ignored_url(request=request):
        if settings.return_header:
            response[settings.guid_header_name] = guid.get()  # Adds the GUID to the response header
            if settings.expose_header:
                response["Access-Control-Expose-Headers"] = settings.guid_header_name

        # Run tear down for all the integrations
        for integration in settings.integrations:
            logger.debug("Running tear down for integration: `%s`", integration.identifier)
            integration.cleanup()


@sync_and_async_middleware
def guid_middleware(get_response: Callable) -> Callable:
    """
    Add this middleware to the top of your middlewares.
    """
    # One-time configuration and initialization.
    if not apps.is_installed("one.libraries.guid"):
        raise ImproperlyConfigured("django_guid must be in installed apps")
    # fmt: off
    if asyncio.iscoroutinefunction(get_response):
        async def middleware(request: 'HttpRequest') -> Union['HttpRequest', 'HttpResponse']:
            logger.debug('async middleware called')
            process_incoming_request(request=request)
            # ^ Code above this line is executed before the view and later middleware
            response = await get_response(request)
            process_outgoing_request(response=response, request=request)
            return response
    else:
        def middleware(request: 'HttpRequest') -> Union['HttpRequest', 'HttpResponse']:  # type: ignore
            logger.debug('sync middleware called')
            process_incoming_request(request=request)
            # ^ Code above this line is executed before the view and later middleware
            response = get_response(request)
            process_outgoing_request(response=response, request=request)
            return response
    # fmt: on
    return middleware
