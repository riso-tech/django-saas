from unittest import mock

from one.libraries.guid.api import clear_guid, get_guid, set_guid
from one.tests.tests.cases import FastTenantTestCase as TestCase


class TestAPI(TestCase):
    @mock.patch("one.libraries.guid.api.guid")
    def test_get_guid(self, mock_guid):
        """Test get_guid function."""
        mock_guid.get.return_value = "123"
        self.assertEqual(get_guid(), "123")

    @mock.patch("one.libraries.guid.api.guid")
    def test_set_guid(self, mock_guid):
        """Test set_guid function."""
        mock_guid.get.return_value = "123"
        new_guid = "456"
        self.assertEqual(set_guid(new_guid), new_guid)
        mock_guid.set.assert_called_once_with(new_guid)

    @mock.patch("one.libraries.guid.api.guid")
    def test_clear_guid(self, mock_guid):
        """Test clear_guid function."""
        mock_guid.get.return_value = "123"
        clear_guid()
        mock_guid.set.assert_called_once_with(None)
