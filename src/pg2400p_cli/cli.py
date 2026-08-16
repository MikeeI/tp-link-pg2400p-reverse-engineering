import os
import sys
import unicodedata
from importlib.metadata import version as package_version
from typing import Annotated, Never

import orjson
import typer

from pg2400p_cli.application.inspection import InspectionService
from pg2400p_cli.domain.errors import PG2400PError
from pg2400p_cli.domain.telemetry import TelemetryReport, TelemetrySeries
from pg2400p_cli.infrastructure.client import DEFAULT_TIMEOUT_SECONDS, PG2400PClient

CLI_NAME = "pg2400p"
PACKAGE_NAME = "pg2400p-cli"
PASSWORD_ENVIRONMENT_VARIABLE = "PG2400P_PASSWORD"

app = typer.Typer(
    name=CLI_NAME,
    help=(
        "Inspect TP-Link PG2400P devices without changing their state. "
        f"Set {PASSWORD_ENVIRONMENT_VARIABLE} or use the hidden password prompt."
    ),
    no_args_is_help=True,
    add_completion=False,
    rich_markup_mode=None,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)


def version_callback(ctx: typer.Context, value: bool) -> None:
    if ctx.resilient_parsing or not value:
        return
    typer.echo(f"{CLI_NAME} {package_version(PACKAGE_NAME)}")
    raise typer.Exit()


@app.callback()
def root(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, is_eager=True),
    ] = False,
) -> None:
    del ctx, version


@app.command("auth-check")
def auth_check(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Verify authentication without changing device state."""
    try:
        _inspection_service(host, timeout_seconds).check_authentication()
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    _emit({"host": host, "authenticated": True}, json_output=json_output)


@app.command()
def info(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Read device identity and firmware information."""
    try:
        device = _inspection_service(host, timeout_seconds).read_device_info()
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    _emit(
        {
            "host": device.host,
            "product": device.product,
            "hardware_revision": device.hardware_revision,
            "firmware_version": device.firmware_version,
            "language": device.language,
        },
        json_output=json_output,
    )


@app.command()
def peers(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Read remote G.hn peers and negotiated rates."""
    try:
        links = _inspection_service(host, timeout_seconds).read_peer_links()
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    if json_output:
        _emit_json({"host": host, "peers": links})
        return
    _emit_pair("host", host)
    _emit_pair("peer_count", len(links))
    for index, link in enumerate(links):
        _emit_pair(f"peer[{index}].mac", link.mac)
        _emit_pair(f"peer[{index}].rx_mbps", link.rx_mbps)
        _emit_pair(f"peer[{index}].tx_mbps", link.tx_mbps)
        _emit_pair(f"peer[{index}].rx_raw", link.rx_raw)
        _emit_pair(f"peer[{index}].tx_raw", link.tx_raw)


@app.command()
def settings(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Read performance-relevant Powerline settings."""
    try:
        result = _inspection_service(host, timeout_seconds).read_powerline_settings()
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    values = {
        "host": host,
        "local_mac": result.local_mac,
        "device_name": result.device_name,
        "network_name": result.network_name,
        "lan_power_saving": result.lan_power_saving,
        "traffic_power_saving": result.traffic_power_saving,
        "automatic_compatibility": result.automatic_compatibility,
        "phy_mode": result.phy_mode,
        "technical_standard": result.technical_standard,
        "qos_mode": result.qos_mode,
    }
    _emit(values, json_output=json_output)


@app.command()
def telemetry(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    interval_seconds: Annotated[
        float | None,
        typer.Option(
            "--interval",
            min=0.1,
            help="Take a second sample after this many seconds and calculate deltas.",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Read hidden G.hn link-quality and error telemetry."""
    try:
        report = _inspection_service(host, timeout_seconds).read_telemetry(
            interval_seconds=interval_seconds,
        )
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    if json_output:
        _emit_json(report)
        return
    _emit_telemetry(report)


@app.command()
def status(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    timeout_seconds: Annotated[
        float,
        typer.Option("--timeout", min=0.1, help="HTTP inactivity timeout in seconds."),
    ] = DEFAULT_TIMEOUT_SECONDS,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Write machine-readable JSON to stdout."),
    ] = False,
) -> None:
    """Read identity, settings, peers, and link rates in one session."""
    try:
        snapshot = _inspection_service(host, timeout_seconds).read_status()
    except (PG2400PError, ValueError) as exc:
        _fail(exc)

    device = snapshot.device
    powerline = snapshot.powerline
    links = snapshot.peers

    if json_output:
        _emit_json(
            {
                "device": device,
                "powerline": powerline,
                "peers": links,
            },
        )
        return

    _emit(
        {
            "host": device.host,
            "product": device.product,
            "hardware_revision": device.hardware_revision,
            "firmware_version": device.firmware_version,
            "local_mac": powerline.local_mac,
            "device_name": powerline.device_name,
            "network_name": powerline.network_name,
            "lan_power_saving": powerline.lan_power_saving,
            "traffic_power_saving": powerline.traffic_power_saving,
            "automatic_compatibility": powerline.automatic_compatibility,
            "phy_mode": powerline.phy_mode,
            "technical_standard": powerline.technical_standard,
            "qos_mode": powerline.qos_mode,
            "peer_count": str(len(links)),
        },
        json_output=False,
    )
    for index, link in enumerate(links):
        _emit_pair(f"peer[{index}].mac", link.mac)
        _emit_pair(f"peer[{index}].rx_mbps", link.rx_mbps)
        _emit_pair(f"peer[{index}].tx_mbps", link.tx_mbps)


def _emit_telemetry(report: TelemetryReport) -> None:
    snapshot = report.snapshot
    _emit_pair("host", snapshot.host)
    _emit_pair("xput_indicator_mbps", snapshot.xput_indicator_mbps)
    for index, node in enumerate(snapshot.nodes):
        _emit_pair(f"node[{index}].did", node.did)
        _emit_pair(f"node[{index}].active", node.active)
        _emit_pair(f"node[{index}].attenuation_tenths_db", node.attenuation_tenths_db)
        _emit_pair(f"node[{index}].attenuation_db", node.attenuation_db)
        _emit_pair(f"node[{index}].wire_length_m", node.wire_length_m)

    _emit_series("qos", snapshot.qos)
    _emit_series("g9962", snapshot.g9962)
    _emit_series("llc_errors", snapshot.llc_errors)
    _emit_series("channel_adaptation", snapshot.channel_adaptation)
    _emit_series("ethernet", snapshot.ethernet)
    _emit_series("ethernet_errors", snapshot.ethernet_errors)
    _emit_series("master_selection", snapshot.master_selection)

    interval = report.interval
    if interval is None:
        return
    _emit_pair("interval.seconds", interval.seconds)
    _emit_pair("interval.tx_bits_per_second", interval.tx_bits_per_second)
    _emit_pair("interval.rx_bits_per_second", interval.rx_bits_per_second)
    _emit_pair("interval.retransmission_rate", interval.retransmission_rate)
    _emit_pair("interval.receive_bler", interval.receive_bler)
    _emit_mapping("interval.g9962", interval.g9962_deltas)
    _emit_mapping("interval.qos", interval.qos_deltas)
    _emit_mapping("interval.ethernet", interval.ethernet_deltas)
    _emit_mapping("interval.ethernet_errors", interval.ethernet_error_deltas)
    _emit_mapping("interval.llc_errors", interval.llc_error_deltas)
    _emit_mapping(
        "interval.channel_adaptation",
        interval.channel_adaptation_deltas,
    )
    _emit_mapping("interval.master_selection", interval.master_selection_deltas)


def _emit_series(prefix: str, series: TelemetrySeries) -> None:
    _emit_mapping(prefix, series.named_values)


def _emit_mapping(prefix: str, values: dict[str, int]) -> None:
    for name, value in values.items():
        _emit_pair(f"{prefix}.{name}", value)


def _inspection_service(host: str, timeout_seconds: float) -> InspectionService:
    return InspectionService(
        host=host,
        password=_management_password(),
        timeout_seconds=timeout_seconds,
        client_factory=PG2400PClient,
    )


def _emit(result: dict[str, str | bool], *, json_output: bool) -> None:
    if json_output:
        _emit_json(result)
        return
    for key, value in result.items():
        _emit_pair(key, value)


def _emit_json(result: object) -> None:
    sys.stdout.buffer.write(orjson.dumps(result, option=orjson.OPT_APPEND_NEWLINE))


def _management_password() -> str:
    password = os.environ.get(PASSWORD_ENVIRONMENT_VARIABLE)
    if password is not None:
        if not password:
            raise ValueError(f"{PASSWORD_ENVIRONMENT_VARIABLE} must not be empty")
        return password
    return typer.prompt("Device management password", hide_input=True)


def _fail(exc: PG2400PError | ValueError) -> Never:
    typer.echo(f"Error: {_terminal_safe(str(exc))}", err=True)
    for note in getattr(exc, "__notes__", ()):
        typer.echo(f"Note: {_terminal_safe(note)}", err=True)
    raise typer.Exit(code=1) from exc


def _emit_pair(key: str, value: object) -> None:
    rendered = str(value).lower() if isinstance(value, bool) else str(value)
    typer.echo(f"{_terminal_safe(key)}={_terminal_safe(rendered)}")


def _terminal_safe(value: str) -> str:
    escaped: list[str] = []
    for character in value:
        code_point = ord(character)
        if character == "\t":
            escaped.append(r"\t")
        elif character == "\n":
            escaped.append(r"\n")
        elif character == "\r":
            escaped.append(r"\r")
        elif unicodedata.category(character).startswith("C"):
            width = 2 if code_point <= 0xFF else 4 if code_point <= 0xFFFF else 8
            prefix = "x" if width == 2 else "u" if width == 4 else "U"
            escaped.append(f"\\{prefix}{code_point:0{width}x}")
        elif character in {"\u2028", "\u2029"}:
            escaped.append(f"\\u{code_point:04x}")
        else:
            escaped.append(character)
    return "".join(escaped)
