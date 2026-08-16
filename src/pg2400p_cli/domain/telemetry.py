from dataclasses import dataclass

from pg2400p_cli.domain.errors import ProtocolError


@dataclass(frozen=True, kw_only=True)
class GhnNodeTelemetry:
    did: int
    active: bool
    attenuation_tenths_db: int
    wire_length_m: int

    @property
    def attenuation_db(self) -> float:
        return self.attenuation_tenths_db / 10


@dataclass(frozen=True, kw_only=True)
class TelemetrySeries:
    names: tuple[str, ...]
    values: tuple[int, ...]

    def value(self, name: str) -> int:
        try:
            index = self.names.index(name)
        except ValueError as exc:
            raise ProtocolError(f"telemetry descriptor omitted {name!r}") from exc
        if index >= len(self.values):
            raise ProtocolError(f"telemetry values omitted {name!r}")
        return self.values[index]

    @property
    def named_values(self) -> dict[str, int]:
        return dict(zip(_effective_names(self), self.values, strict=True))

    @property
    def unmapped_values(self) -> tuple[int, ...]:
        return self.values[len(self.names) :]


@dataclass(frozen=True, kw_only=True)
class TelemetrySnapshot:
    host: str
    nodes: tuple[GhnNodeTelemetry, ...]
    xput_indicator_mbps: int
    link_status_descriptor: tuple[str, ...]
    qos: TelemetrySeries
    g9962: TelemetrySeries
    llc_errors: TelemetrySeries
    channel_adaptation: TelemetrySeries
    ethernet: TelemetrySeries
    ethernet_errors: TelemetrySeries
    master_selection: TelemetrySeries
    raw_fields: dict[str, str]


@dataclass(frozen=True, kw_only=True)
class TelemetryInterval:
    seconds: float
    g9962_deltas: dict[str, int]
    qos_deltas: dict[str, int]
    ethernet_deltas: dict[str, int]
    ethernet_error_deltas: dict[str, int]
    llc_error_deltas: dict[str, int]
    channel_adaptation_deltas: dict[str, int]
    master_selection_deltas: dict[str, int]
    tx_bits_per_second: float
    rx_bits_per_second: float
    retransmission_rate: float | None
    receive_bler: float | None


@dataclass(frozen=True, kw_only=True)
class TelemetryReport:
    snapshot: TelemetrySnapshot
    interval: TelemetryInterval | None = None


def calculate_telemetry_interval(
    first: TelemetrySnapshot,
    second: TelemetrySnapshot,
    *,
    seconds: float,
) -> TelemetryInterval:
    if seconds <= 0:
        raise ValueError("telemetry interval must be greater than zero")
    if first.host != second.host:
        raise ValueError("telemetry snapshots must belong to the same host")

    g9962 = _series_deltas(first.g9962, second.g9962, group="G.9962")
    blocks_tx = g9962["BLOCKS_TX"]
    blocks_rx = g9962["BLOCKS_RX"]
    return TelemetryInterval(
        seconds=seconds,
        g9962_deltas=g9962,
        qos_deltas=_series_deltas(first.qos, second.qos, group="QoS"),
        ethernet_deltas=_series_deltas(first.ethernet, second.ethernet, group="Ethernet"),
        ethernet_error_deltas=_series_deltas(
            first.ethernet_errors,
            second.ethernet_errors,
            group="Ethernet errors",
        ),
        llc_error_deltas=_series_deltas(
            first.llc_errors,
            second.llc_errors,
            group="LLC errors",
        ),
        channel_adaptation_deltas=_series_deltas(
            first.channel_adaptation,
            second.channel_adaptation,
            group="channel adaptation",
        ),
        master_selection_deltas=_series_deltas(
            first.master_selection,
            second.master_selection,
            group="master selection",
        ),
        tx_bits_per_second=g9962["Bytes_TX"] * 8 / seconds,
        rx_bits_per_second=g9962["Bytes_RX"] * 8 / seconds,
        retransmission_rate=_ratio(g9962["BLOCKS_RTX"], blocks_tx),
        receive_bler=_ratio(g9962["BLOCKS_ERROR_RX"], blocks_rx),
    )


def _series_deltas(
    first: TelemetrySeries,
    second: TelemetrySeries,
    *,
    group: str,
) -> dict[str, int]:
    if first.names != second.names:
        raise ProtocolError(f"{group} telemetry descriptor changed during interval")
    if len(first.values) != len(second.values):
        raise ProtocolError(f"{group} telemetry width changed during interval")

    deltas: dict[str, int] = {}
    for name, before, after in zip(
        _effective_names(first),
        first.values,
        second.values,
        strict=True,
    ):
        delta = after - before
        if delta < 0:
            raise ProtocolError(f"{group} counter {name!r} decreased during interval")
        deltas[name] = delta
    return deltas


def _effective_names(series: TelemetrySeries) -> tuple[str, ...]:
    return (
        *series.names,
        *(f"UNMAPPED_{index}" for index in range(1, len(series.values) - len(series.names) + 1)),
    )


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None
