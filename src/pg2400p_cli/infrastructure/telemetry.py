from collections.abc import Mapping

from pg2400p_cli.domain.errors import ProtocolError
from pg2400p_cli.domain.telemetry import (
    GhnNodeTelemetry,
    TelemetrySeries,
    TelemetrySnapshot,
)

DIDS_KEY = "DIDMNG.GENERAL.DIDS"
ACTIVE_KEY = "DIDMNG.GENERAL.ACTIVE"
ATTENUATION_KEY = "DIDMNG.GENERAL.AVG_ATTENUATION"
WIRE_LENGTH_KEY = "DIDMNG.GENERAL.WIRE_LENGTH"
XPUT_KEY = "FLOWMONITOR.INFO.XPUT_INDICATOR"
LINK_STATUS_DESCRIPTOR_KEY = "FLOWMONITOR.STATS.LINK_STATUS_DESC"
QOS_KEY = "QOS.STATS.INFO"
QOS_DESCRIPTOR_KEY = "QOS.STATS.DESC"
G9962_KEY = "QOS.STATS.G9962"
G9962_DESCRIPTOR_KEY = "QOS.STATS.G9962_DESC"
LLC_ERRORS_KEY = "QOS.STATS.RX_LLC_ERRORS"
LLC_ERRORS_DESCRIPTOR_KEY = "QOS.STATS.RX_LLC_ERRORS_DESC"
CHANNEL_KEY = "QOS.STATS.CHANNEL_INFO"
CHANNEL_DESCRIPTOR_KEY = "QOS.STATS.CHANNEL_INFO_DESC"
ETHERNET_KEY = "ETHIFDRIVER.STATS.INFO"
ETHERNET_DESCRIPTOR_KEY = "ETHIFDRIVER.STATS.INFO_DESC"
ETHERNET_ERRORS_KEY = "ETHIFDRIVER.STATS.ERRORS"
ETHERNET_ERRORS_DESCRIPTOR_KEY = "ETHIFDRIVER.STATS.ERRORS_DESC"
MASTER_KEY = "MASTERSELECTION.STATS.INFO"
MASTER_DESCRIPTOR_KEY = "MASTERSELECTION.STATS.DESC"

TELEMETRY_KEYS = (
    DIDS_KEY,
    ACTIVE_KEY,
    ATTENUATION_KEY,
    WIRE_LENGTH_KEY,
    XPUT_KEY,
    LINK_STATUS_DESCRIPTOR_KEY,
    QOS_KEY,
    QOS_DESCRIPTOR_KEY,
    G9962_KEY,
    G9962_DESCRIPTOR_KEY,
    LLC_ERRORS_KEY,
    LLC_ERRORS_DESCRIPTOR_KEY,
    CHANNEL_KEY,
    CHANNEL_DESCRIPTOR_KEY,
    ETHERNET_KEY,
    ETHERNET_DESCRIPTOR_KEY,
    ETHERNET_ERRORS_KEY,
    ETHERNET_ERRORS_DESCRIPTOR_KEY,
    MASTER_KEY,
    MASTER_DESCRIPTOR_KEY,
)


def decode_telemetry_snapshot(
    host: str,
    fields: Mapping[str, str],
) -> TelemetrySnapshot:
    dids = _integers(fields, DIDS_KEY)
    active = _booleans(fields, ACTIVE_KEY)
    attenuation = _integers(fields, ATTENUATION_KEY)
    wire_length = _integers(fields, WIRE_LENGTH_KEY)
    widths = {len(dids), len(active), len(attenuation), len(wire_length)}
    if len(widths) != 1:
        raise ProtocolError("G.hn topology telemetry arrays have different lengths")

    nodes = tuple(
        GhnNodeTelemetry(
            did=did,
            active=is_active,
            attenuation_tenths_db=attenuation_value,
            wire_length_m=wire_length_value,
        )
        for did, is_active, attenuation_value, wire_length_value in zip(
            dids,
            active,
            attenuation,
            wire_length,
            strict=True,
        )
    )
    return TelemetrySnapshot(
        host=host,
        nodes=nodes,
        xput_indicator_mbps=_integer(fields, XPUT_KEY),
        link_status_descriptor=_descriptor(fields, LINK_STATUS_DESCRIPTOR_KEY),
        qos=_series(fields, QOS_DESCRIPTOR_KEY, QOS_KEY),
        g9962=_series(fields, G9962_DESCRIPTOR_KEY, G9962_KEY),
        llc_errors=_series(fields, LLC_ERRORS_DESCRIPTOR_KEY, LLC_ERRORS_KEY),
        channel_adaptation=_series(fields, CHANNEL_DESCRIPTOR_KEY, CHANNEL_KEY),
        ethernet=_series(fields, ETHERNET_DESCRIPTOR_KEY, ETHERNET_KEY),
        ethernet_errors=_series(
            fields,
            ETHERNET_ERRORS_DESCRIPTOR_KEY,
            ETHERNET_ERRORS_KEY,
        ),
        master_selection=_series(fields, MASTER_DESCRIPTOR_KEY, MASTER_KEY),
        raw_fields=dict(fields),
    )


def _series(
    fields: Mapping[str, str],
    descriptor_key: str,
    value_key: str,
) -> TelemetrySeries:
    names = _descriptor(fields, descriptor_key)
    values = _integers(fields, value_key)
    if len(names) > len(values):
        raise ProtocolError(f"{value_key} has fewer values than its descriptor")
    return TelemetrySeries(names=names, values=values)


def _descriptor(fields: Mapping[str, str], key: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in _required(fields, key).split(","))
    if not values or any(not item for item in values):
        raise ProtocolError(f"{key} contains an empty descriptor")
    if len(set(values)) != len(values):
        raise ProtocolError(f"{key} contains duplicate descriptors")
    return values


def _integers(fields: Mapping[str, str], key: str) -> tuple[int, ...]:
    raw_values = _required(fields, key).split(",")
    try:
        values = tuple(int(item.strip()) for item in raw_values)
    except ValueError as exc:
        raise ProtocolError(f"{key} contains a non-integer value") from exc
    if any(value < 0 for value in values):
        raise ProtocolError(f"{key} contains a negative value")
    return values


def _integer(fields: Mapping[str, str], key: str) -> int:
    values = _integers(fields, key)
    if len(values) != 1:
        raise ProtocolError(f"{key} must contain exactly one value")
    return values[0]


def _booleans(fields: Mapping[str, str], key: str) -> tuple[bool, ...]:
    values: list[bool] = []
    for raw_value in _required(fields, key).split(","):
        value = raw_value.strip()
        if value == "YES":
            values.append(True)
        elif value == "NO":
            values.append(False)
        else:
            raise ProtocolError(f"{key} contains unsupported value {value!r}")
    return tuple(values)


def _required(fields: Mapping[str, str], key: str) -> str:
    try:
        return fields[key]
    except KeyError as exc:
        raise ProtocolError(f"telemetry response omitted {key}") from exc
