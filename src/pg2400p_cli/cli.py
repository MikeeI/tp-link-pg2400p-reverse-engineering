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


def _emit(result: dict[str, str | bool], *, json_output: bool) -> None:
    if json_output:
        sys.stdout.buffer.write(orjson.dumps(result, option=orjson.OPT_APPEND_NEWLINE))
        return
    for key, value in result.items():
        rendered = str(value).lower() if isinstance(value, bool) else value
        typer.echo(f"{key}={rendered}")
