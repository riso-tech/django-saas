from django.utils.translation import gettext_lazy as _
from rest_framework.utils.serializer_helpers import OrderedDict, ReturnDict
from rest_framework.views import exception_handler

from ..schemas.response import DefaultResponse

UNKNOWN_ERROR = _("Unknown error while processing your request.")
NON_FIELDS_ERRORS = ["detail", "non_field_errors"]


def _stringify_non_generic_types(data):
    """Remove non-generic types from values of dict or list
    For example: {'detail': [ErrorDetail(message = 'Unknown error')]}
    Will be converted to: {'detail': ['Unknown error']} (by str representation of ErrorDetail)
    """
    if type(data) is list:
        for index, item in enumerate(data):
            data[index] = _stringify_non_generic_types(item)
    elif type(data) in [dict, OrderedDict, ReturnDict]:
        for key, value in data.items():
            data[key] = _stringify_non_generic_types(value)
    elif type(data) not in [str, int, bool, float]:
        return str(data) if data is not None else UNKNOWN_ERROR
    return data


def _get_error_message_with_validation_errors(
    error_data: dict | OrderedDict | ReturnDict | list | str,
) -> tuple[str, dict, bool]:
    message, validation_errors, has_child = UNKNOWN_ERROR, {}, False
    if type(error_data) is list and len(error_data) > 0:
        error_item = error_data[0]
        child_message, child_validation_errors, child_has_child = _get_error_message_with_validation_errors(error_item)
        has_child = len(child_validation_errors) > 0 or child_has_child
        message = child_message
    elif type(error_data) in [dict, OrderedDict, ReturnDict] and len(error_data.keys()) > 0:
        validation_errors = error_data
        for field_name, child_error_data in error_data.items():
            child_message, child_validation_errors, child_has_child = _get_error_message_with_validation_errors(
                child_error_data
            )
            delimiter = ":" if (not child_has_child and len(child_validation_errors) == 0) else " >"
            has_child = len(child_validation_errors) > 0 or child_has_child
            message = f"{field_name}{delimiter} {child_message}"
            break
    elif type(error_data) is str:
        has_child = False
        message = error_data
    else:
        has_child = False
        message = UNKNOWN_ERROR
    return message, validation_errors, has_child


def drf_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        default_data = DefaultResponse(
            success=False,
            status_code=response.status_code,
            message=_("Unknown error while processing your request."),
            validation_errors={},
            data=None,
        ).to_dict()
        error_data: str | dict | OrderedDict | ReturnDict | list = _stringify_non_generic_types(response.data or {})
        error_message, validation_errors, __ = _get_error_message_with_validation_errors(error_data)
        for non_field_error in NON_FIELDS_ERRORS:
            replace_text = f"{non_field_error}: "
            if error_message.startswith(replace_text):
                error_message = error_message.replace(replace_text, "")
        default_data["message"] = error_message
        default_data["validation_errors"] = validation_errors
        response.data = default_data
    else:
        default_data = DefaultResponse(
            success=False,
            status_code=500,
            message=str(exc),
            validation_errors={},
            data=None,
        )
        response = default_data

    return response
