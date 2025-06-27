#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

from unittest import TestCase
from unittest.mock import Mock, patch

import pytest

from s2gos_client.api.exceptions import ClientException
from s2gos_client.api.transport import DefaultTransport, TransportArgs
from s2gos_common.models import ApiError, ConformanceDeclaration


class DefaultTransportTest(TestCase):
    def test_call_success_200(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"conformsTo": ["Hello", "World"]}
        mock_response.raise_for_status.return_value = None

        transport = DefaultTransport(server_url="https://api.example.com", debug=True)
        with patch(
            "s2gos_client.transport.requests.request", return_value=mock_response
        ) as mock_request:
            result = transport.call(
                TransportArgs(
                    path="/conformance",
                    method="get",
                    return_types={"200": ConformanceDeclaration},
                    error_types={"401": ApiError},
                )
            )
            mock_request.assert_called_once_with(
                "GET",
                "https://api.example.com/conformance",
                params={},
                json=None,
            )

        self.assertIsInstance(result, ConformanceDeclaration)

    def test_call_success_201(self):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"conformsTo": ["Hello", "World"]}
        mock_response.raise_for_status.return_value = None

        transport = DefaultTransport(server_url="https://api.example.com", debug=True)
        with patch(
            "s2gos_client.transport.requests.request", return_value=mock_response
        ) as mock_request:
            result = transport.call(
                TransportArgs(
                    path="/conformance",
                    method="get",
                    return_types={"201": ConformanceDeclaration},
                    error_types={"401": ApiError},
                )
            )
            mock_request.assert_called_once_with(
                "GET",
                "https://api.example.com/conformance",
                params={},
                json=None,
            )

        self.assertIsInstance(result, ConformanceDeclaration)

    def test_call_success_no_return_type(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"conformsTo": ["Hello", "World"]}
        mock_response.raise_for_status.return_value = None

        transport = DefaultTransport(server_url="https://api.example.com", debug=True)
        with patch(
            "s2gos_client.transport.requests.request", return_value=mock_response
        ) as mock_request:
            result = transport.call(
                TransportArgs(
                    path="/conformance", method="get", error_types={"401": ApiError}
                )
            )
            mock_request.assert_called_once_with(
                "GET",
                "https://api.example.com/conformance",
                params={},
                json=None,
            )
            self.assertEqual({"conformsTo": ["Hello", "World"]}, result)

    # noinspection PyMethodMayBeStatic
    def test_call_fail(self):
        mock_response = Mock()
        mock_response.ok = False
        mock_response.reason = "Conformance not found"
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "So sorry"}
        mock_response.raise_for_status.return_value = None

        transport = DefaultTransport(server_url="https://api.example.com", debug=True)
        with patch(
            "s2gos_client.transport.requests.request", return_value=mock_response
        ):
            with pytest.raises(ClientException, match="Conformance not found"):
                transport.call(
                    TransportArgs(
                        path="/conformance",
                        method="get",
                        return_types={"200": ConformanceDeclaration},
                        error_types={"401": ApiError},
                    )
                )
