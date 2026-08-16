from pathlib import Path

import orjson
import pytest
from typer.testing import CliRunner

from pg2400p_cli.cli import app
from pg2400p_cli.domain.errors import ProtocolError
from pg2400p_cli.domain.telemetry import (
    TelemetryReport,
    calculate_telemetry_interval,
)
from pg2400p_cli.infrastructure.protocol import parse_key_value_response
from pg2400p_cli.infrastructure.telemetry import (
    TELEMETRY_KEYS,
    decode_telemetry_snapshot,
)

FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures"
runner = CliRunner()


def _snapshot(name: str = "telemetry-sample-1.txt"):
    fields = parse_key_value_response(
        (FIXTURE_DIRECTORY / name).read_text(encoding="utf-8"),
    )
    return decode_telemetry_snapshot("10.0.1.184", fields)


def test_live_fixture_covers_all_confirmed_telemetry_fields() -> None:
    snapshot = _snapshot()

    assert len(TELEMETRY_KEYS) == 20
    assert tuple(snapshot.raw_fields) == TELEMETRY_KEYS
    assert snapshot.nodes[2].did == 2
    assert snapshot.nodes[2].attenuation_db == 43.0
    assert snapshot.nodes[2].wire_length_m == 60
    assert snapshot.xput_indicator_mbps == 365
    assert snapshot.g9962.value("BLOCKS_ERROR_RX") == 644888
    assert snapshot.channel_adaptation.unmapped_values == (0, 0, 0, 0)
    assert snapshot.channel_adaptation.named_values["UNMAPPED_4"] == 0


def test_confirmed_samples_produce_interval_rates_and_error_ratios() -> None:
    interval = calculate_telemetry_interval(
        _snapshot(),
        _snapshot("telemetry-sample-2.txt"),
        seconds=89.96,
    )

    assert interval.g9962_deltas["Bytes_TX"] == 247680
    assert interval.g9962_deltas["Bytes_RX"] == 108000
    assert interval.g9962_deltas["BLOCKS_TX"] == 1697
    assert interval.g9962_deltas["BLOCKS_RX"] == 698
    assert interval.g9962_deltas["BLOCKS_RTX"] == 1
    assert interval.g9962_deltas["BLOCKS_ERROR_RX"] == 19
    assert interval.tx_bits_per_second == pytest.approx(247680 * 8 / 89.96)
    assert interval.rx_bits_per_second == pytest.approx(108000 * 8 / 89.96)
    assert interval.retransmission_rate == pytest.approx(1 / 1697)
    assert interval.receive_bler == pytest.approx(19 / 698)
    assert interval.llc_error_deltas == {
        "LLC_CRC_ERRORS": 0,
        "LLC_CIPHER_MIC_ERRORS": 0,
    }
    assert interval.master_selection_deltas["total number of Master Domain losses"] == 0


def test_counter_decrease_invalidates_interval() -> None:
    with pytest.raises(ProtocolError, match="decreased during interval"):
        calculate_telemetry_interval(
            _snapshot("telemetry-sample-2.txt"),
            _snapshot(),
            seconds=1,
        )


def test_telemetry_command_emits_raw_and_decoded_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeInspectionService:
        def read_telemetry(self, *, interval_seconds: float | None) -> TelemetryReport:
            assert interval_seconds is None
            return TelemetryReport(snapshot=_snapshot())

    monkeypatch.setattr(
        "pg2400p_cli.cli._inspection_service",
        lambda host, timeout_seconds: FakeInspectionService(),
    )

    result = runner.invoke(
        app,
        ["telemetry", "--host", "10.0.1.184", "--json"],
        env={"PG2400P_PASSWORD": "unused"},
    )

    assert result.exit_code == 0
    assert result.stderr == ""
    payload = orjson.loads(result.stdout)
    assert payload["snapshot"]["xput_indicator_mbps"] == 365
    assert payload["snapshot"]["nodes"][2]["attenuation_tenths_db"] == 430
    assert payload["snapshot"]["raw_fields"]["QOS.STATS.G9962"].endswith(
        "1795573,644888",
    )
