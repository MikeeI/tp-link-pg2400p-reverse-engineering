from collections.abc import Callable

import httpx
import pytest

from pg2400p_cli.client import PG2400PClient
from pg2400p_cli.errors import AuthenticationError


def _sequence_transport(
    handlers: list[Callable[[httpx.Request], httpx.Response]],
) -> httpx.MockTransport:
    pending = iter(handlers)

    def handle(request: httpx.Request) -> httpx.Response:
        return next(pending)(request)

    return httpx.MockTransport(handle)


def _preflight(request: httpx.Request) -> httpx.Response:
    assert request.method == "GET"
    assert request.url == "http://10.0.1.184/"
    return httpx.Response(200, text="<html></html>")


def _warmup_login(request: httpx.Request) -> httpx.Response:
    assert request.method == "POST"
    assert request.url == "http://10.0.1.184/"
    assert request.headers["x-requested-with"] == "XMLHttpRequest"
    assert request.headers["origin"] == "http://10.0.1.184"
    assert request.headers["referer"] == "http://10.0.1.184/"
    assert request.content == (
        b"TPLINK.GENERAL.LOGIN_PASSWORD="
        b"f78e7ab810633ab3a6bbaa49d7d6d5eb"
    )
    return httpx.Response(200, text="ERROR=004\n")


def _successful_login(request: httpx.Request) -> httpx.Response:
    assert request.method == "POST"
    return httpx.Response(200, text="ERROR=000\nTOKEN=test-token\n")


def test_authenticate_retries_observed_session_warmup_code() -> None:
    transport = _sequence_transport(
        [_preflight, _warmup_login, _preflight, _successful_login],
    )
    with PG2400PClient(
        host="10.0.1.184",
        password="MyStrongPassword",
        transport=transport,
    ) as client:
        client.authenticate()
        assert client.authenticated is True

def test_read_device_info_uses_only_firmware_confirmed_read_keys() -> None:
    def identity_read(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.params["_t"] == "test-token"
        assert set(request.url.params) == {
            "_t",
            "SYSTEM.PRODUCTION.HW_PRODUCT",
            "SYSTEM.PRODUCTION.HW_REVISION",
            "SYSTEM.GENERAL.FW_VERSION",
            "TPLINK.GENERAL.LANGUAGE",
        }
        return httpx.Response(
            200,
            text=(
                "ERROR=000\r\n"
                "SYSTEM.PRODUCTION.HW_PRODUCT=PG2400P\r\n"
                "SYSTEM.PRODUCTION.HW_REVISION=1.0\r\n"
                "SYSTEM.GENERAL.FW_VERSION=1.1.0 Build 20250710\r\n"
                "TPLINK.GENERAL.LANGUAGE=de_DE\r\n"
            ),
        )

    transport = _sequence_transport([_preflight, _successful_login, identity_read])
    with PG2400PClient(
        host="10.0.1.184",
        password="MyStrongPassword",
        transport=transport,
    ) as client:
        client.authenticate()
        info = client.read_device_info()

    assert info.product == "PG2400P"
    assert info.hardware_revision == "1.0"
    assert info.firmware_version == "1.1.0 Build 20250710"
    assert info.language == "de_DE"


def test_authenticate_maps_invalid_password() -> None:
    def rejected_login(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(200, text="ERROR=006\nLOGIN_TIMES=1\n")

    transport = _sequence_transport([_preflight, rejected_login])
    with PG2400PClient(
        host="10.0.1.184",
        password="wrong",
        transport=transport,
    ) as client:
        with pytest.raises(AuthenticationError, match="1 failed attempt"):
            client.authenticate()


@pytest.mark.parametrize("host", ["", "http://10.0.1.184", "10.0.1.184/path", "bad host"])
def test_client_rejects_non_host_input(host: str) -> None:
    with pytest.raises(ValueError):
        PG2400PClient(host=host, password="unused")
