import time
from typing import Any

import requests
from requests import Request

from .exceptions import ClientTimeoutError, ServiceRequestError


class ServiceClient:
    def __init__(
        self,
        retries: int = 3,
        timeout: int = 10,
    ) -> None:
        self.retries = retries
        self.timeout = timeout
        self.session = requests.session()

    def request_headers(self) -> dict[str, Any]:
        pass

    def _request_loop(
        self,
        http_method: str,
        endpoint: str,
        data=None,
        params=None,
        files=None,
        json=None,
        headers=None,
        retries: int = None,
    ):
        retry: int = 0
        retries = self.retries if retries is None else retries
        while retry <= retries:
            try:
                return self.request(
                    http_method=http_method,
                    endpoint=endpoint,
                    data=data,
                    params=params,
                    files=files,
                    json=json,
                    headers=headers,
                )
            except Exception as err:
                if retry < retries and type(err) is ClientTimeoutError:
                    retry += 1
                    time.sleep(retry)
                    continue
                else:
                    raise err

    def request(
        self,
        http_method: str,
        endpoint: str,
        data: dict[str, Any] | None,
        params: dict[str, Any] | None,
        files: None,
        json: None,
        headers=None,
    ):
        headers = self.request_headers() if not headers else headers
        request = Request(
            method=http_method,
            url=endpoint,
            data=data,
            params=params,
            files=files,
            json=json,
            headers=headers,
        )
        prepared_request = request.prepare()
        try:
            return self.session.send(request=prepared_request, timeout=self.timeout)
        except (
            requests.exceptions.ConnectTimeout,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ):
            raise ClientTimeoutError()
        except Exception:
            raise ServiceRequestError()
