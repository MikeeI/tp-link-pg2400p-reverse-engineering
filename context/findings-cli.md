# Read-only CLI

Source: `src/pg2400p_cli/`
Action status: `NOW`
Live verification: both owned PG2400P devices on 2026-08-14

## Contract

- [confirmed] The installed command is `pg2400p`.
- [confirmed] `auth-check`, `info`, `peers`, `settings`, and `status` are read-only command surfaces.
- [confirmed] Human output is stable `key=value` text.
- [confirmed] `--json` emits one JSON value on stdout and keeps diagnostics on stderr.
- [confirmed] HTTP sessions own preflight, MD5 login, `_t` token use, logout, and transport cleanup.
- [confirmed] Credentials come from `PG2400P_PASSWORD` or a hidden prompt; no public command accepts a password argument.
- [confirmed] Human output visibly escapes terminal controls; JSON preserves raw values with JSON escaping.
- [confirmed] Cleanup failures remain visible beside a primary command failure, while transport closure remains unconditional.
- [confirmed] The client accepts only `get compatibility mode`, `get qos`, and `logout` as POST commands.
- [confirmed] No generic field-write, arbitrary `COMMAND`, firmware, reset, reboot, pairing, or configuration API is exposed.

## Protocol Ownership

- [confirmed] `protocol.py` owns MD5 encoding and strict CRLF-compatible `KEY=VALUE` parsing.
- [confirmed] `client.py` owns HTTP lifecycle, allowed requests, response errors, and field-to-model translation.
- [confirmed] `models.py` owns device identity, peer-link, and performance-relevant settings results.
- [confirmed] `cli.py` owns Typer grammar, presentation, JSON output, and expected-error translation.

## Live Results

The following command completed successfully against both devices and sent `COMMAND=logout` during cleanup.
The password was supplied through `PG2400P_PASSWORD`, not the process argument vector:

```bash
uv run --locked pg2400p status \
  --host <device-ip> \
  --json
```

- [confirmed] Both devices report `PG2400P`, hardware `1.0`, and firmware `1.0.3 Build 20221213 Rel.62540`.
- [confirmed] Both devices use domain `HomeGrid`, LAN power saving, automatic compatibility, MIMO, and fair QoS.
- [confirmed] Traffic-based power saving is disabled on both devices.
- [confirmed] Both devices report the technical standard as `full_power`.
- [confirmed] `.184` reports `.185` at RX `456 Mbps` and TX `388 Mbps` after the UI-defined `/ 32` conversion.
- [confirmed] `.185` reports `.184` at RX `388 Mbps` and TX `456 Mbps` after the same conversion.

## Verification

- [confirmed] Ruff formatting and linting completed successfully for `src` and `tests`.
- [confirmed] Pyright completed with zero errors and zero warnings.
- [confirmed] Pytest completed with 22 focused protocol, request-shape, cleanup, credential, output, and safety tests.
- [confirmed] Aggregate live `status --json` completed on both devices without configuration changes.
- [confirmed] A focused security review found and drove fixes for argv secret exposure, dual-failure cleanup reporting, and terminal-control output.

## Limits

- [confirmed] Hidden telemetry is proven live in `findings-ghn-telemetry.md` but not yet exposed by the CLI.
  `FLOWMONITOR.INFO.XPUT_INDICATOR` is a firmware estimate, not measured application throughput.
- [unresolved] Server-side implementations remain unbound until the raw Xtensa image has a reliable load map and xrefs.
- [unresolved] Write behavior remains intentionally unavailable until exact state effects and rollback are proven.
