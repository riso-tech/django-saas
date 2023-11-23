import time

import requests
from requests import Request

from .exceptions import ClientTimeoutError, ServiceRequestError


class ServiceClient:
    def __init__(self, retries=3, timeout=10):
        self.retries = retries
        self.timeout = timeout
        self.session = requests.session()

    def _request_loop(self, http_method, endpoint, data=None, params=None, files=None, json=None, retries=None):
        retry: int = 0
        retries = self.retries if retries is None else retries
        while retry <= retries:
            try:
                return self.request(http_method, endpoint, data, params, files, json)
            except Exception as err:
                if retry < retries and type(err) is ClientTimeoutError:
                    retry += 1
                    time.sleep(retry)
                    continue
                else:
                    raise err

    def request(self, http_method, endpoint, data=None, params=None, files=None, json=None):
        request = Request(
            method=http_method,
            url=endpoint,
            data=data,
            params=params,
            files=files,
            json=json,
            headers=self.session.headers,
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
