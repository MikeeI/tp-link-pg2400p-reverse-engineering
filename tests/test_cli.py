from types import TracebackType

import orjson
import pytest
from typer.testing import CliRunner

from pg2400p_cli.cli import app
from pg2400p_cli.domain.errors import AuthenticationError
from pg2400p_cli.domain.models import DeviceInfo, PeerLink, PowerlineSettings

runner = CliRunner()


class FakeClient:
    def __init__(self, **kwargs: object) -> None:
        self.host = str(kwargs["host"])

    def __enter__(self) -> "FakeClient":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def authenticate(self) -> None:
        return None

    def read_device_info(self) -> DeviceInfo:
        return DeviceInfo(
            host=self.host,
            product="PG2400P",
            hardware_revision="1.0",
            firmware_version="1.0.3 Build 20221213 Rel.62540",
            language="en_GB",
        )

    def read_powerline_settings(self) -> PowerlineSettings:
        return PowerlineSettings(
            local_mac="8c:90:2d:10:49:e2",
            device_name="Device_49E2",
            network_name="HomeGrid",
            lan_power_saving=True,
            traffic_power_saving=False,
            automatic_compatibility=True,
            phy_mode="mimo",
            technical_standard="full_power",
            qos_mode="fair",
        )

    def read_peer_links(self) -> tuple[PeerLink, ...]:
        return (
            PeerLink(
                mac="3c:64:cf:59:d4:88",
                rx_mbps=456,
                tx_mbps=388,
                rx_raw=14615,
                tx_raw=12421,
            ),
        )


def test_status_json_contains_only_one_machine_readable_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pg2400p_cli.cli.PG2400PClient", FakeClient)

    result = runner.invoke(
        app,
        [
            "status",
            "--host",
            "10.0.1.184",
            "--json",
        ],
        env={"PG2400P_PASSWORD": "secret"},
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    payload = orjson.loads(result.stdout)
    assert payload["device"]["product"] == "PG2400P"
    assert payload["powerline"]["phy_mode"] == "mimo"
    assert payload["peers"][0]["rx_mbps"] == 456


def test_expected_authentication_error_uses_stderr(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RejectingClient(FakeClient):
        def authenticate(self) -> None:
            raise AuthenticationError("device rejected the password")

    monkeypatch.setattr(
        "pg2400p_cli.cli.PG2400PClient",
        RejectingClient,
    )

    result = runner.invoke(
        app,
        ["auth-check", "--host", "10.0.1.184"],
        env={"PG2400P_PASSWORD": "wrong"},
    )

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "device rejected the password" in result.stderr


def test_hidden_prompt_does_not_echo_password(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pg2400p_cli.cli.PG2400PClient", FakeClient)

    result = runner.invoke(
        app,
        ["auth-check", "--host", "10.0.1.184"],
        input="prompt-secret\n",
        env={"PG2400P_PASSWORD": None},
    )

    assert result.exit_code == 0
    assert "prompt-secret" not in result.output
    assert "Device management password:" in result.output


def test_human_output_escapes_remote_terminal_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ControlCharacterClient(FakeClient):
        def read_device_info(self) -> DeviceInfo:
            return DeviceInfo(
                host=self.host,
                product="PG\x1b]52;c;payload\x07\n2400P",
                hardware_revision="1.0",
                firmware_version="1.0.3",
                language="en_GB",
            )

    monkeypatch.setattr(
        "pg2400p_cli.cli.PG2400PClient",
        ControlCharacterClient,
    )

    result = runner.invoke(
        app,
        ["info", "--host", "10.0.1.184"],
        env={"PG2400P_PASSWORD": "secret"},
    )

    assert result.exit_code == 0
    assert "\x1b" not in result.stdout
    assert "product=PG\\x1b]52;c;payload\\x07\\n2400P" in result.stdout


def test_error_output_includes_cleanup_failure_note(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class DualFailureClient(FakeClient):
        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: TracebackType | None,
        ) -> None:
            if exc_value is not None:
                exc_value.add_note("session cleanup failed: logout rejected")

        def read_device_info(self) -> DeviceInfo:
            raise AuthenticationError("primary read failure")

    monkeypatch.setattr(
        "pg2400p_cli.cli.PG2400PClient",
        DualFailureClient,
    )

    result = runner.invoke(
        app,
        ["info", "--host", "10.0.1.184"],
        env={"PG2400P_PASSWORD": "secret"},
    )

    assert result.exit_code == 1
    assert "Error: primary read failure" in result.stderr
    assert "Note: session cleanup failed: logout rejected" in result.stderr
