class ServiceRequestError(Exception):
    """An exception that indicates there is an issue from Service Request."""


class ClientTimeoutError(ServiceRequestError):
    """An exception that indicates there is request timeout."""


class AccountStatusError(ServiceRequestError):
    """An exception that indicates there is an issue with a given account's status."""


class BusinessRuleError(ServiceRequestError):
    """An exception that indicates business rule logic has been violated."""


class ClientSecurityError(ServiceRequestError):
    """This exception will be raised in the event that authorization is failed."""


class ClientSystemError(ServiceRequestError):
    """This exception will be thrown on 500 server responses and fatal errors."""


class ValidationError(ServiceRequestError):
    """An exception that indicates a given value does not match it's required type."""
