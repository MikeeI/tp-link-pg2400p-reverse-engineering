from collections.abc import Callable

import httpx
import pytest

from pg2400p_cli.domain.errors import AuthenticationError, ProtocolError
from pg2400p_cli.infrastructure.client import PG2400PClient


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
    assert request.content == (b"TPLINK.GENERAL.LOGIN_PASSWORD=f78e7ab810633ab3a6bbaa49d7d6d5eb")
    return httpx.Response(200, text="ERROR=004\n")


def _successful_login(request: httpx.Request) -> httpx.Response:
    assert request.method == "POST"
    return httpx.Response(200, text="ERROR=000\nTOKEN=test-token\n")


def _logout(request: httpx.Request) -> httpx.Response:
    assert request.method == "POST"
    assert request.url.params["_t"] == "test-token"
    assert request.content == b"COMMAND=logout"
    return httpx.Response(200, text="ERROR=000\r\n")


def test_authenticate_retries_observed_session_warmup_code() -> None:
    transport = _sequence_transport(
        [_preflight, _warmup_login, _preflight, _successful_login, _logout],
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

    transport = _sequence_transport(
        [_preflight, _successful_login, identity_read, _logout],
    )
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


def test_read_peer_links_matches_observed_runtime_conversion() -> None:
    def peer_read(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(
            200,
            text=(
                "ERROR=000\r\n"
                "SYSTEM.PRODUCTION.MAC_ADDR=8c:90:2d:10:49:e2\r\n"
                "DIDMNG.GENERAL.MACS="
                "00:00:00:00:00:00,8c:90:2d:10:49:e2,3c:64:cf:59:d4:88\r\n"
                "DIDMNG.GENERAL.RX_BPS=0,0,14615\r\n"
                "DIDMNG.GENERAL.TX_BPS=0,0,12421\r\n"
            ),
        )

    transport = _sequence_transport([_preflight, _successful_login, peer_read, _logout])
    with PG2400PClient(
        host="10.0.1.184",
        password="MyStrongPassword",
        transport=transport,
    ) as client:
        client.authenticate()
        peers = client.read_peer_links()

    assert len(peers) == 1
    assert peers[0].mac == "3c:64:cf:59:d4:88"
    assert peers[0].rx_raw == 14615
    assert peers[0].tx_raw == 12421
    assert peers[0].rx_mbps == 456
    assert peers[0].tx_mbps == 388


def test_read_powerline_settings_maps_firmware_defined_values() -> None:
    def settings_read(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(
            200,
            text=(
                "ERROR=000\r\n"
                "SYSTEM.PRODUCTION.MAC_ADDR=8c:90:2d:10:49:e2\r\n"
                "NODE.GENERAL.DEVICE_NAME=Device_49E2\r\n"
                "NODE.GENERAL.DOMAIN_NAME=HomeGrid\r\n"
                "POWERSAVING.GENERAL.MODE=1\r\n"
                "MSPS.THROUGHPUT.ENABLE=YES\r\n"
                "INTERFMITIGATION.XDSL.ENABLED=YES\r\n"
                "PHYMNG.GENERAL.RUNNING_PHYMODE_ID=7\r\n"
            ),
        )

    def technical_read(request: httpx.Request) -> httpx.Response:
        assert request.content == b"COMMAND=get+compatibility+mode"
        return httpx.Response(200, text="ERROR=000\r\nRESULT=1\r\n")

    def qos_read(request: httpx.Request) -> httpx.Response:
        assert request.content == b"COMMAND=get+qos"
        return httpx.Response(200, text="ERROR=000\r\nRESULT=2\r\n")

    transport = _sequence_transport(
        [
            _preflight,
            _successful_login,
            settings_read,
            technical_read,
            qos_read,
            _logout,
        ],
    )
    with PG2400PClient(
        host="10.0.1.184",
        password="MyStrongPassword",
        transport=transport,
    ) as client:
        client.authenticate()
        settings = client.read_powerline_settings()

    assert settings.device_name == "Device_49E2"
    assert settings.network_name == "HomeGrid"
    assert settings.lan_power_saving is True
    assert settings.traffic_power_saving is True
    assert settings.automatic_compatibility is True
    assert settings.phy_mode == "mimo"
    assert settings.technical_standard == "full_power"
    assert settings.qos_mode == "gaming"


def test_unapproved_command_is_blocked_before_transport() -> None:
    def unexpected_request(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"unexpected request: {request.method} {request.url}")

    with (
        PG2400PClient(
            host="10.0.1.184",
            password="unused",
            transport=httpx.MockTransport(unexpected_request),
        ) as client,
        pytest.raises(ProtocolError, match="not approved"),
    ):
        client._post_command("set qos 2")


def test_authenticate_maps_invalid_password() -> None:
    def rejected_login(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        return httpx.Response(200, text="ERROR=006\nLOGIN_TIMES=1\n")

    transport = _sequence_transport([_preflight, rejected_login])
    with (
        PG2400PClient(
            host="10.0.1.184",
            password="wrong",
            transport=transport,
        ) as client,
        pytest.raises(AuthenticationError, match="1 failed attempt"),
    ):
        client.authenticate()


def test_operation_and_logout_failures_remain_visible_after_transport_close() -> None:
    def failed_read(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(200, text="ERROR=900\r\n")

    def failed_logout(request: httpx.Request) -> httpx.Response:
        assert request.content == b"COMMAND=logout"
        return httpx.Response(200, text="ERROR=901\r\n")

    transport = _sequence_transport(
        [_preflight, _successful_login, failed_read, failed_logout],
    )
    client = PG2400PClient(
        host="10.0.1.184",
        password="MyStrongPassword",
        transport=transport,
    )

    with pytest.raises(ProtocolError) as exc_info, client:
        client.authenticate()
        client.read_device_info()

    assert any("session cleanup failed" in note for note in getattr(exc_info.value, "__notes__", ()))
    assert client._client.is_closed


@pytest.mark.parametrize("host", ["", "http://10.0.1.184", "10.0.1.184/path", "bad host"])
def test_client_rejects_non_host_input(host: str) -> None:
    with pytest.raises(ValueError):
        PG2400PClient(host=host, password="unused")
