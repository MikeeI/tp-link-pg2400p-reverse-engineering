import sys
from importlib.metadata import version as package_version
from typing import Annotated

import orjson
import typer

from pg2400p_cli.client import DEFAULT_TIMEOUT_SECONDS, PG2400PClient
from pg2400p_cli.errors import PG2400PError

CLI_NAME = "pg2400p"
PACKAGE_NAME = "pg2400p-cli"

app = typer.Typer(
    name=CLI_NAME,
    help="Inspect TP-Link PG2400P devices without changing their state.",
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
    password: Annotated[
        str,
        typer.Option("--password", help="Device management password."),
    ],
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
        with PG2400PClient(
            host=host,
            password=password,
            timeout_seconds=timeout_seconds,
        ) as client:
            client.authenticate()
    except (PG2400PError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    _emit({"host": host, "authenticated": True}, json_output=json_output)


@app.command()
def info(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    password: Annotated[
        str,
        typer.Option("--password", help="Device management password."),
    ],
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
        with PG2400PClient(
            host=host,
            password=password,
            timeout_seconds=timeout_seconds,
        ) as client:
            client.authenticate()
            device = client.read_device_info()
    except (PG2400PError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

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
    password: Annotated[
        str,
        typer.Option("--password", help="Device management password."),
    ],
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
        with PG2400PClient(
            host=host,
            password=password,
            timeout_seconds=timeout_seconds,
        ) as client:
            client.authenticate()
            links = client.read_peer_links()
    except (PG2400PError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    if json_output:
        _emit_json({"host": host, "peers": links})
        return
    typer.echo(f"host={host}")
    typer.echo(f"peer_count={len(links)}")
    for index, link in enumerate(links):
        typer.echo(f"peer[{index}].mac={link.mac}")
        typer.echo(f"peer[{index}].rx_mbps={link.rx_mbps}")
        typer.echo(f"peer[{index}].tx_mbps={link.tx_mbps}")
        typer.echo(f"peer[{index}].rx_raw={link.rx_raw}")
        typer.echo(f"peer[{index}].tx_raw={link.tx_raw}")


@app.command()
def settings(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    password: Annotated[
        str,
        typer.Option("--password", help="Device management password."),
    ],
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
        with PG2400PClient(
            host=host,
            password=password,
            timeout_seconds=timeout_seconds,
        ) as client:
            client.authenticate()
            result = client.read_powerline_settings()
    except (PG2400PError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

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
def status(
    host: Annotated[str, typer.Option("--host", help="Device IP address or hostname.")],
    password: Annotated[
        str,
        typer.Option("--password", help="Device management password."),
    ],
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
        with PG2400PClient(
            host=host,
            password=password,
            timeout_seconds=timeout_seconds,
        ) as client:
            client.authenticate()
            device = client.read_device_info()
            powerline = client.read_powerline_settings()
            links = client.read_peer_links()
    except (PG2400PError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

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
        typer.echo(f"peer[{index}].mac={link.mac}")
        typer.echo(f"peer[{index}].rx_mbps={link.rx_mbps}")
        typer.echo(f"peer[{index}].tx_mbps={link.tx_mbps}")


def _emit(result: dict[str, str | bool], *, json_output: bool) -> None:
    if json_output:
        _emit_json(result)
        return
    for key, value in result.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        typer.echo(f"{key}={rendered}")


def _emit_json(result: object) -> None:
    sys.stdout.buffer.write(orjson.dumps(result, option=orjson.OPT_APPEND_NEWLINE))
