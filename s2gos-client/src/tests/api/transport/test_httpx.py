#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from typing import Any, Callable
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from s2gos_client.api.exceptions import ClientException
from s2gos_client.api.transport import TransportArgs
from s2gos_client.api.transport.httpx import HttpxTransport
from s2gos_common.models import ApiError, ConformanceDeclaration


def make_mocked_transport(
    status_code: int,
    return_value: Any,
    side_effect: Callable | None = None,
    reason: str | None = None,
):
    response = MagicMock()
    response.status_code = status_code
    response.reason = reason
    response.json.return_value = return_value
    response.raise_for_status.side_effect = side_effect

    sync_httpx = MagicMock()
    sync_httpx.request.return_value = response

    async_httpx = MagicMock()
    async_httpx.request = AsyncMock(return_value=response)

    transport = HttpxTransport(server_url="https://api.example.com")
    transport.sync_httpx = sync_httpx
    transport.async_httpx = async_httpx
    return transport


class HttpxSyncTransportTest(TestCase):
    def test_call_success_200(self):
        transport = make_mocked_transport(
            200,
            {"conformsTo": ["Hello", "World"]},
        )
        result = transport.call(
            TransportArgs(
                path="/conformance",
                method="get",
                return_types={"200": ConformanceDeclaration},
                error_types={"401": ApiError},
            )
        )
        # noinspection PyUnresolvedReferences
        transport.sync_httpx.request.assert_called_once_with(
            "GET",
            "https://api.example.com/conformance",
            params={},
            json=None,
        )
        self.assertIsInstance(result, ConformanceDeclaration)

    def test_call_success_201(self):
        transport = make_mocked_transport(
            201,
            {"conformsTo": ["Hello", "World"]},
        )
        result = transport.call(
            TransportArgs(
                path="/conformance",
                method="get",
                return_types={"201": ConformanceDeclaration},
                error_types={"401": ApiError},
            )
        )
        # noinspection PyUnresolvedReferences
        transport.sync_httpx.request.assert_called_once_with(
            "GET",
            "https://api.example.com/conformance",
            params={},
            json=None,
        )
        self.assertIsInstance(result, ConformanceDeclaration)

    def test_call_success_no_return_type(self):
        transport = make_mocked_transport(
            200,
            {"conformsTo": ["Hello", "World"]},
        )
        result = transport.call(
            TransportArgs(
                path="/conformance", method="get", error_types={"401": ApiError}
            )
        )
        # noinspection PyUnresolvedReferences
        transport.sync_httpx.request.assert_called_once_with(
            "GET",
            "https://api.example.com/conformance",
            params={},
            json=None,
        )
        self.assertEqual({"conformsTo": ["Hello", "World"]}, result)

    # noinspection PyMethodMayBeStatic
    def test_call_fail(self):
        def panic():
            raise httpx.HTTPError("Panic!")

        transport = make_mocked_transport(
            401,
            {"type": "error", "detail": "So sorry"},
            side_effect=panic,
            reason="Conformance not found",
        )
        args = TransportArgs(
            path="/conformance",
            method="get",
            return_types={"200": ConformanceDeclaration},
            error_types={"401": ApiError},
        )
        with pytest.raises(ClientException, match="Panic!") as e:
            transport.call(args)
        ce: ClientException = e.value
        self.assertEqual("Panic! (status 401)", str(ce))
        self.assertEqual(ApiError(type="error", detail="So sorry"), ce.api_error)

    def test_close(self):
        sync_httpx = MagicMock()

        transport = HttpxTransport(server_url="https://api.example.com")
        transport.sync_httpx = sync_httpx

        transport.close()
        self.assertIsNone(transport.sync_httpx)


class HttpxAsyncTransportTest(IsolatedAsyncioTestCase):
    async def test_async_call_success(self):
        transport = make_mocked_transport(
            200,
            {"conformsTo": ["Hello", "World"]},
        )
        result = await transport.async_call(
            TransportArgs(
                path="/conformance",
                method="get",
                return_types={"200": ConformanceDeclaration},
                error_types={"401": ApiError},
            )
        )
        # noinspection PyUnresolvedReferences
        transport.async_httpx.request.assert_called_once_with(
            "GET",
            "https://api.example.com/conformance",
            params={},
            json=None,
        )
        self.assertIsInstance(result, ConformanceDeclaration)

    async def test_async_close(self):
        async_httpx = MagicMock()

        transport = HttpxTransport(server_url="https://api.example.com")
        transport.async_httpx = async_httpx
        transport.async_httpx.aclose = AsyncMock(return_value=None)

        await transport.async_close()
        self.assertIsNone(transport.async_httpx)
