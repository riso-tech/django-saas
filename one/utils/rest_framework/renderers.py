from collections import OrderedDict

from rest_framework.renderers import BrowsableAPIRenderer as BaseBrowsableAPIRenderer
from rest_framework.renderers import JSONRenderer as BaseJSONRenderer
from rest_framework.response import Response

from ..schemas.response import DefaultResponse, Pagination


class JSONRenderer(BaseJSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            response: Response = renderer_context["response"]
            msg: str = "OK"
            code: int = response.status_code

            if response.status_code > 399:
                return super().render(data, accepted_media_type, renderer_context)

            if "view" in renderer_context and type(renderer_context["view"]).__name__ == "APIRootView":
                return super().render(data, accepted_media_type, renderer_context)

            if isinstance(data, dict):
                msg = data.pop("msg", msg)
                _code = data.get("code", None)
                if type(_code) is int:
                    code = _code
                data = data.pop("data", data)

            res = DefaultResponse(data=data, status_code=code, message=msg).to_dict()

            if type(res["data"]) is OrderedDict or type(res["data"]) is dict:
                if (
                    "page" in res["data"]
                    and "limit" in res["data"]
                    and "total_pages" in res["data"]
                    and "total_items" in res["data"]
                    and "results" in res["data"]
                ):
                    # noinspection PyTypedDict
                    pagination = Pagination(
                        res["data"]["page"],
                        res["data"]["limit"],
                        res["data"]["total_pages"],
                        res["data"]["total_items"],
                    )
                    res["pagination"] = pagination.to_dict()
                    res["data"] = res["data"]["results"]
                elif "detail" in res["data"] and len(res["data"]) == 1:
                    _message_detail = res["data"]["detail"]
                    if type(_message_detail) is list and len(_message_detail):
                        res["message"] = str(_message_detail[0])
                    else:
                        res["message"] = str(_message_detail)
            return super().render(res, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)


class BrowsableAPIRenderer(BaseBrowsableAPIRenderer):
    pass
