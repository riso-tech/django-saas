import json

from django.test import TestCase
from rest_framework import response as drf_response
from rest_framework import status as drf_statuses
from rest_framework.routers import APIRootView

from ..renderers import JSONRenderer


class TestJSONRenderer(TestCase):
    def setUp(self) -> None:
        self.renderer = JSONRenderer()

    # noinspection PyUnresolvedReferences
    def test_render_context_none(self):
        data = {"foo": "bar"}
        result = self.renderer.render(data=data, accepted_media_type="application/json", renderer_context=None)
        expected_data = b'{"foo":"bar"}'
        self.assertEqual(result, expected_data)

    # noinspection PyUnresolvedReferences
    def test_render_context(self):
        data = {"foo": "bar"}

        response = drf_response.Response(status=drf_statuses.HTTP_400_BAD_REQUEST)
        result = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": None,
            },
        )
        self.assertEqual(result, b'{"foo":"bar"}')

        # skip override response data for browsable api view (debug mode)
        api_root_view = APIRootView()
        response = drf_response.Response(status=drf_statuses.HTTP_200_OK)
        result = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": api_root_view,
            },
        )
        self.assertEqual(result, b'{"foo":"bar"}')

        # override status code from data.code attr
        data = {"foo": "bar", "code": 201}
        response = drf_response.Response(status=drf_statuses.HTTP_200_OK)
        result: bytes = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": None,
            },
        )
        actual_result = json.loads(result.decode("utf-8"))
        actual_status_code = actual_result["status_code"]
        self.assertEqual(actual_status_code, data["code"])

        # parsing pagination data
        data = {"foo": "bar", "page": 1, "limit": 50, "total_pages": 10, "total_items": 500, "results": []}
        response = drf_response.Response(status=drf_statuses.HTTP_200_OK)
        result: bytes = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": None,
            },
        )
        actual_result = json.loads(result.decode("utf-8"))
        pagination_result = actual_result["pagination"]
        self.assertEqual(pagination_result["page"], 1)
        self.assertEqual(pagination_result["limit"], 50)
        self.assertEqual(pagination_result["total_pages"], 10)
        self.assertEqual(pagination_result["total_items"], 500)

        # get default drf detail (non_fields_error) message if available
        data = {"detail": "You do not have permission to perform this action."}
        response = drf_response.Response(status=drf_statuses.HTTP_200_OK)
        result: bytes = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": None,
            },
        )
        actual_result = json.loads(result.decode("utf-8"))
        self.assertEqual(actual_result["message"], data["detail"])

        # get default drf detail (validation error) message if available
        data = {"detail": ["Username should at least have 3 characters", "Password is too weak"]}
        response = drf_response.Response(status=drf_statuses.HTTP_200_OK)
        result: bytes = self.renderer.render(
            data=data,
            accepted_media_type="application/json",
            renderer_context={
                "response": response,
                "view": None,
            },
        )
        actual_result = json.loads(result.decode("utf-8"))
        self.assertEqual(actual_result["message"], data["detail"][0])
