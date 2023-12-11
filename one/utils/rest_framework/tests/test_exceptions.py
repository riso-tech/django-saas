from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.utils.translation import gettext_lazy
from rest_framework import exceptions as drf_exceptions
from rest_framework import permissions
from rest_framework import response as drf_response
from rest_framework import serializers
from rest_framework import status as drf_status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.test import APIRequestFactory

from ..exceptions import drf_exception_handler


class MockNested1Serializer(serializers.Serializer):
    item_1 = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def validate(self, attrs):
        raise serializers.ValidationError(detail={"detail": ["Test Exception from Nested1Serializer"]})


class MockNested2Serializer(serializers.Serializer):
    items_2 = MockNested1Serializer(required=True, many=True, allow_null=False, allow_empty=False)


class MockNested3Serializer(serializers.Serializer):
    items_3 = MockNested2Serializer(required=True, many=True, allow_null=False, allow_empty=False)

    def process(self):
        pass


class MockUserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = None
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def get_serializer_class(self):
        if self.action == "test_nested_serializer_exceptions":
            return MockNested3Serializer
        raise NotImplementedError()

    @action(methods=["POST"], detail=False)
    def test_nested_serializer_exceptions(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.process()
        return drf_response.Response(status=drf_status.HTTP_200_OK, data=None)


class TestExceptions(TestCase):
    def setUp(self) -> None:
        request = RequestFactory().get("/")
        self.context = {"request": request}

    def test_drf_exception_handle_nested_exceptions(self):
        view = MockUserViewSet.as_view({"post": "test_nested_serializer_exceptions"})
        request = APIRequestFactory().post(
            path="/",
            data={
                "items_3": [
                    {},
                ],
            },
            format="json",
        )
        response = view(request)
        print(response.data)

    def test_drf_exception_handler_response_is_none(self):
        result = drf_exception_handler(
            exc=Exception("Error"),
            context=self.context,
        )
        self.assertEqual(result.status_code, drf_status.HTTP_500_INTERNAL_SERVER_ERROR)

        result = drf_exception_handler(
            exc=Exception("unique constraint"),
            context=self.context,
        )
        self.assertEqual(result.status_code, drf_status.HTTP_500_INTERNAL_SERVER_ERROR)

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_drf_exception_handler_response_data_is_none(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", None)
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(
            exc=None,
            context=self.context,
        )
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], gettext_lazy("Unknown error while processing your request."))

    def test_test_drf_exception_handler_exception_is_list_or_errors(self):
        result = drf_exception_handler(
            exc=drf_exceptions.PermissionDenied(["You do not have permission to perform this action."]),
            context=self.context,
        )
        self.assertEqual(result.status_code, drf_status.HTTP_403_FORBIDDEN)
        self.assertEqual(result.data["message"], "You do not have permission to perform this action.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_empty_dict(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], gettext_lazy("Unknown error while processing your request."))

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_str(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"detail": "This field is required."})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "This field is required.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_list_non_field_errors(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"detail": ["This field is required."]})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "This field is required.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_list_custom_field_name(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"username": ["This field is required."]})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "username: This field is required.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_error_detail(self, mock_exception_handler):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"username": drf_exceptions.ErrorDetail("This field is required.")})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "username: This field is required.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_dict_contains_list_of_errors(
        self, mock_exception_handler
    ):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"orders": {"order_id": ["This field is required."]}})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "orders > order_id: This field is required.")

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_dict_contains_dict_of_errors(
        self, mock_exception_handler
    ):
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(
            mock_response,
            "data",
            {
                "orders": {
                    "sku": {"upc": "Invalid UPC format"},
                }
            },
        )
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "orders > sku > upc: Invalid UPC format")

        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(
            mock_response,
            "data",
            {
                "orders": {
                    "sku": {"upc": ["Invalid UPC format"]},
                }
            },
        )
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "orders > sku > upc: Invalid UPC format")

        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(
            mock_response,
            "data",
            {
                "orders": {
                    "sku": {"detail": ["Invalid UPC format"]},
                }
            },
        )
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "orders > sku > detail: Invalid UPC format")

        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(
            mock_response,
            "data",
            {
                "orders": {
                    "sku": {"detail": drf_exceptions.ErrorDetail("Invalid UPC format")},
                }
            },
        )
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], "orders > sku > detail: Invalid UPC format")

        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(
            mock_response,
            "data",
            {
                "orders": {
                    "sku": {
                        "detail": None,
                    },
                }
            },
        )
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            result.data["message"],
            f'orders > sku > detail: {gettext_lazy("Unknown error while processing your request.")}',
        )

    @patch("one.utils.rest_framework.exceptions.exception_handler")
    def test_test_drf_exception_handler_data_dict_child_value_unknown_type(self, mock_exception_handler):
        # serializers.ValidationError(detail=None)
        mock_response = drf_response.Response(status=drf_status.HTTP_400_BAD_REQUEST)
        setattr(mock_response, "data", {"detail": None})
        mock_exception_handler.return_value = mock_response
        result = drf_exception_handler(exc=None, context=self.context)
        self.assertEqual(result.status_code, drf_status.HTTP_400_BAD_REQUEST)
        self.assertEqual(result.data["message"], gettext_lazy("Unknown error while processing your request."))
