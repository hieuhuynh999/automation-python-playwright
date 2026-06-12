from typing import Any

import httpx

from automation.config import settings
from automation.logging import log_method
from automation.reporting import attach_text


class BaseApiClient:
    def __init__(self, base_url: str | None = None):
        self.client = httpx.Client(base_url=base_url or settings.api_base_url, timeout=30)

    @log_method("API GET")
    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    @log_method("API POST")
    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    @log_method("API PUT")
    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("PUT", path, **kwargs)

    @log_method("API PATCH")
    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("PATCH", path, **kwargs)

    @log_method("API DELETE")
    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    def close(self) -> None:
        self.client.close()

    @log_method("API request")
    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        response = self.client.request(method, path, **kwargs)
        attach_text(
            "api-response",
            f"{method} {path}\nStatus: {response.status_code}\n{response.text}",
        )
        return response
