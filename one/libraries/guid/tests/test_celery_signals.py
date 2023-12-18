import logging
import uuid
from copy import deepcopy
from unittest import mock

from django.conf import settings as django_settings
from django.test import override_settings

from one.libraries.guid import get_guid, set_guid
from one.libraries.guid.config import Settings
from one.libraries.guid.integrations import CeleryIntegration
from one.libraries.guid.integrations.celery.context import celery_current, celery_parent
from one.libraries.guid.integrations.celery.signals import (
    clean_up,
    parent_header,
    publish_task_from_worker_or_request,
    set_transaction_id,
    worker_prerun,
)
from one.libraries.guid.utils import generate_guid


@mock.patch("one.libraries.guid.integrations.celery.signals.settings")
def test_task_publish_includes_correct_headers(settings):
    """
    It's important that we include the correct headers when publishing a task
    to the celery worker pool, otherwise there's no transfer of state.
    """
    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    settings.return_value = mocked_settings
    # Actual testing
    for correlation_id in [None, "test", 123, -1]:
        # Set the id in our context var
        set_guid(correlation_id)

        # Run signal with empty headers
        headers = {}
        publish_task_from_worker_or_request(headers=headers)

        # Makes sure the returned headers contain the correct result
        assert headers[settings.guid_header_name] == correlation_id


@mock.patch("one.libraries.guid.integrations.celery.signals.settings")
def test_task_publish_includes_correct_depth_headers(settings):
    """
    Test log_parent True
    """
    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    settings.return_value = mocked_settings

    headers = {}
    publish_task_from_worker_or_request(headers=headers)
    # The parent header should not be in headers, because
    # There should be no celery_current context
    assert parent_header not in headers

    for correlation_id in ["test", 123, -1]:
        headers = {}
        celery_current.set(correlation_id)
        publish_task_from_worker_or_request(headers=headers)
        # Here the celery-parent-id header should exist
        assert headers[parent_header] == correlation_id


def test_worker_prerun_guid_exists(monkeypatch):
    """
    Tests that GUID is set to the GUID if a GUID exists in the task object.
    """
    # mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    # mocked_settings['INTEGRATIONS'] = [CeleryIntegration(log_parent=True)]
    # settings.return_value = Settings()
    mock_task = mock.Mock()
    mock_task.request = {"Correlation-ID": "704ae5472cae4f8daa8f2cc5a5a8mock"}

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=False)]
    with override_settings(DJANGO_GUID=mocked_settings):
        new_settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", new_settings)
        worker_prerun(mock_task)
    assert get_guid() == "704ae5472cae4f8daa8f2cc5a5a8mock"


def test_worker_prerun_guid_does_not_exist(monkeypatch):
    """
    Tests that a GUID is set if it does not exist
    """
    mock_task = mock.Mock()
    mock_task.request = {"Correlation-ID": None}

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=False)]
    with override_settings(DJANGO_GUID=mocked_settings):
        new_settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", new_settings)

        class MockUUid:
            hex = "704ae5472cae4f8daa8f2cc5a5a8mock"

            def __str__(self):
                return f"{self.hex[:8]}-{self.hex[8:12]}-{self.hex[12:16]}-{self.hex[16:20]}-{self.hex[20:]}"

        monkeypatch.setattr("one.libraries.guid.utils.uuid.uuid4", MockUUid)

        worker_prerun(mock_task)

    assert get_guid() == "704ae5472cae4f8daa8f2cc5a5a8mock"


def test_worker_prerun_guid_log_parent_no_origin(monkeypatch):
    """
    Tests that depth works when there is no origin
    """
    from one.libraries.guid.integrations.celery.signals import parent_header

    mock_task = mock.Mock()
    mock_task.request = {"Correlation-ID": None, parent_header: None}  # No origin

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    with override_settings(DJANGO_GUID=mocked_settings):
        settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", settings)

        mock_uuid_hex = mock.MagicMock(spec=uuid.UUID, name="UUID Mock")
        type(mock_uuid_hex.return_value).hex = mock.PropertyMock(
            side_effect=["704ae5472cae4f8daa8f2cc5a5a8mock", "c494886651cd4baaa8654e4d24a8mock"]
        )

        with mock.patch("uuid.UUID", new=mock_uuid_hex):
            worker_prerun(mock_task)

    assert get_guid() == "704ae5472cae4f8daa8f2cc5a5a8mock"
    assert celery_current.get() == "c494886651cd4baaa8654e4d24a8mock"
    assert celery_parent.get() is None


def test_worker_prerun_guid_log_parent_with_origin(monkeypatch):
    """
    Tests that depth works when there is an origin
    """
    from one.libraries.guid.integrations.celery.signals import parent_header

    mock_task = mock.Mock()
    mock_task.request = {"Correlation-ID": None, parent_header: "1234"}  # No origin

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    with override_settings(DJANGO_GUID=mocked_settings):
        settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", settings)

        mock_uuid_hex = mock.MagicMock(spec=uuid.UUID, name="UUID Mock")
        type(mock_uuid_hex.return_value).hex = mock.PropertyMock(
            side_effect=["704ae5472cae4f8daa8f2cc5a5a8mock", "c494886651cd4baaa8654e4d24a8mock"]
        )

        with mock.patch("uuid.UUID", new=mock_uuid_hex):
            worker_prerun(mock_task)

    assert get_guid() == "704ae5472cae4f8daa8f2cc5a5a8mock"
    assert celery_current.get() == "c494886651cd4baaa8654e4d24a8mock"
    assert celery_parent.get() == "1234"


@mock.patch("one.libraries.guid.integrations.celery.signals.settings")
def test_cleanup(settings):
    """
    Test that cleanup works as expected
    """
    set_guid("123")
    celery_current.set("123")
    celery_parent.set("123")

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    settings.return_value = mocked_settings

    clean_up(task=mock.Mock())
    assert [get_guid(), celery_current.get(), celery_parent.get()] == [None, None, None]


def test_set_transaction_id(monkeypatch, caplog):
    """
    Tests that the `configure_scope()` is executed, given `sentry_integration=True` in CeleryIntegration
    """
    # https://github.com/eisensheng/pytest-catchlog/issues/44
    logger = logging.getLogger("django_guid.celery")  # Ensure caplog can catch logs with `propagate=False`
    logger.addHandler(caplog.handler)

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(sentry_integration=True)]
    with override_settings(DJANGO_GUID=mocked_settings):
        settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", settings)
        guid = generate_guid()
        set_transaction_id(guid)
    logger.removeHandler(caplog.handler)  # Remove handler before test finish
    assert f"Setting Sentry transaction_id to {guid}" in [record.message for record in caplog.records]


def test_dont_set_transaction_id(monkeypatch, caplog):
    """
    Tests that the `configure_scope()` is not executed, given `sentry_integration=False` in CeleryIntegration
    """
    logger = logging.getLogger("django_guid.celery")
    logger.addHandler(caplog.handler)

    mocked_settings = deepcopy(django_settings.DJANGO_GUID)
    mocked_settings["INTEGRATIONS"] = [CeleryIntegration(log_parent=True)]
    with override_settings(DJANGO_GUID=mocked_settings):
        settings = Settings()
        monkeypatch.setattr("one.libraries.guid.integrations.celery.signals.settings", settings)
        guid = generate_guid()
        set_transaction_id(guid)
    logger.removeHandler(caplog.handler)
    assert f"Setting Sentry transaction_id to {guid}" not in [record.message for record in caplog.records]
