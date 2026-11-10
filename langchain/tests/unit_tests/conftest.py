from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import httpx
import pytest


class Recorder:
    """Builds httpx clients on a MockTransport and records each request."""

    def __init__(self, respond: Callable[[httpx.Request], httpx.Response]) -> None:
        self.requests: list[httpx.Request] = []
        self._respond = respond

    def _handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self._respond(request)

    def client(self) -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(self._handle))

    def async_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=httpx.MockTransport(self._handle))

    def body(self, i: int = 0) -> dict[str, Any]:
        return json.loads(self.requests[i].content)


def reply(data: Any, status: int = 200, headers: dict[str, str] | None = None) -> Callable:
    def respond(_: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=data, headers=headers or {})

    return respond


@pytest.fixture(autouse=True)
def no_env_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPIDER_API_KEY", raising=False)
