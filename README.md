# TP-Link PG2400P G.hn Powerline Reverse Engineering

Reverse engineering and read-only diagnostics for the **TP-Link PG2400P KIT (EU V1)**, a G.hn2400 2×2 MIMO powerline adapter. This project documents its proprietary `.ftp` firmware container, likely little-endian Xtensa firmware, HTTP management API, MD5/token authentication, hidden G.9962 telemetry, tpPLC raw-Ethernet discovery, and a safe Python CLI.

**Key result:** both tested PG2400P adapters expose undocumented attenuation, estimated wire length, BLER, retransmission, LLC, Ethernet, and Domain Master counters. Direct per-subcarrier SNR remains unresolved.

> Research status: two official EU V1 firmware releases, two owned live devices, current Windows and macOS tpPLC utilities, static firmware analysis, bounded read-only runtime verification, and 22 focused CLI tests.

## What this project found

| Surface | Result |
| --- | --- |
| Firmware | Official EU V1 releases `1.0.3` and `1.1.0` acquired, hashed, and extracted |
| Container | Proprietary `.ftp` package containing XZ-compressed raw firmware and an FFS TAR |
| Architecture | Likely 32-bit little-endian Xtensa with an RTOS-like service model; no Linux filesystem or ELF evidenced |
| Web API | Root `KEY=` reads, `ERROR=000` grammar, browser-side MD5 login, and `_t` session token |
| Hidden telemetry | Attenuation, wire length, XPUT, G.9962 blocks/errors/retries, LLC errors, Ethernet errors, and master losses |
| tpPLC | Raw-Ethernet G.hn discovery using EtherType `0x2e00` through libpcap/Npcap-compatible code |
| Tooling | Safe read-only Python CLI for identity, settings, peers, and negotiated rates |
| Updates | Package CRC and encryption-state evidence recovered; device-side signature/security policy remains unresolved |

The public PG2400P manuals expose configuration and negotiated link rates, but not the underlying link-quality counters documented here. The adapter is a G.hn device, not a HomePlug AV/AV2 device.

## Hidden G.hn diagnostics

The consumer UI hides the underlying ConfigLayer telemetry. Authenticated read-only GET requests confirmed 20 values on both tested devices, including:

```text
DIDMNG.GENERAL.AVG_ATTENUATION
DIDMNG.GENERAL.WIRE_LENGTH
FLOWMONITOR.INFO.XPUT_INDICATOR
QOS.STATS.G9962
QOS.STATS.RX_LLC_ERRORS
QOS.STATS.CHANNEL_INFO
ETHIFDRIVER.STATS.INFO
ETHIFDRIVER.STATS.ERRORS
MASTERSELECTION.STATS.INFO
```

A roughly 90-second observation window under incidental light traffic produced:

| Metric                              |         Device A |         Device B |
| ----------------------------------- | ---------------: | ---------------: |
| Attenuation                         |        `43.0 dB` |        `39.7 dB` |
| Estimated wire length               |           `60 m` |           `59 m` |
| Negotiated Rx/Tx UI rate            | `456 / 388 Mbps` | `388 / 456 Mbps` |
| Estimated application throughput    |       `365 Mbps` |   `301–310 Mbps` |
| Receive BLER                        |        `2.7221%` |        `0.0622%` |
| Retransmission rate                 |        `0.0589%` |        `1.9672%` |
| New packet, LLC, or Ethernet errors |              `0` |              `0` |

Rates must be calculated from counter deltas:

```text
retransmission_rate = ΔBLOCKS_RTX / ΔBLOCKS_TX
receive_BLER         = ΔBLOCKS_ERROR_RX / ΔBLOCKS_RX
attenuation_dB       = AVG_ATTENUATION / 10
UI_rate_Mbps         = BPS // 32
```

`FLOWMONITOR.STATS.LINK_STATUS_DESC` exposes `TIMER,MSECS,SID,FRAMES,LPDUS,ERROR%,ABORT%`, but the corresponding value returned `ERROR=009` on both devices. No monitor or diagnostic state was enabled to pursue it.

See [G.hn telemetry findings](context/findings-ghn-telemetry.md) and the [exact live samples](data/extracted-live/extracted-knowledge/live-telemetry-evidence.txt).

## Firmware container and architecture

The official TP-Link ZIP contains a vendor-specific `.ftp` update package. Both analyzed releases contain two independently decoded XZ streams:

```text
TP-Link ZIP
└── PG2400P .ftp update package
    ├── XZ-compressed raw firmware payload
    └── XZ-compressed POSIX FFS TAR
        ├── web UI
        └── logfile/logfile.cfg
```

Confirmed artifact facts:

- `1.0.3` raw payload: `3,828,620` bytes, SHA-256 `00213d7d32a1d29c654b38570c798ae176ae24f6223e4e0794aa231d59df545d`
- `1.1.0` raw payload: `3,837,292` bytes, SHA-256 `79745b3a349b2d92ff0a6801f4f35fa2e8893725119334260ba7175c05f47716`
- no parseable ELF header or recognized Linux filesystem in either raw payload
- independent `xtensa8` strings plus valid little-endian Xtensa decoding at static base `0x63000000`
- static Webserver, Filesystem, FlowMonitor, G.9962, firmware-upgrade, and configuration-layer anchors

`0x63000000` is a useful static analysis base, not a proven physical flash or runtime load address. The exact Xtensa core, ABI, RTOS, reset vector, task model, and physical flash map remain unresolved.

See [architecture and process findings](context/findings-architecture-processes.md), [firmware identity](context/findings-firmware-identity.md), and [version comparison](context/findings-version-comparisons.md).

## HTTP API and authentication

The PG2400P web UI uses a root form-style API rather than a documented REST interface.

```text
GET /?KEY1=&KEY2=&_t=<token>

ERROR=000
KEY1=value
KEY2=value
```

Observed semantics:

- model reads use authenticated GET requests with empty `KEY=` query values
- commands use form-encoded POST requests
- responses use `ERROR=<decimal>` followed by CRLF-separated `KEY=VALUE` lines
- `ERROR=000` means success
- `ERROR=004` is used for an invalid or missing token
- `ERROR=009` rejected the inactive FlowMonitor value above
- the browser client applies MD5 before submitting `TPLINK.GENERAL.LOGIN_PASSWORD`
- the authenticated session token is sent as `_t=<token>`

The repository records known mutation routes but does not expose arbitrary commands or writes through the CLI.

See [web API findings](context/findings-web-api.md) and [authentication findings](context/findings-auth-crypto.md).

## tpPLC companion and G.hn discovery

The official Windows utility is an Electron application whose native path reaches `plcu.exe`, `plcoperation.dll`, and WinPcap-compatible `WPCAP.DLL`/`PACKET.DLL` imports. The macOS backend directly imports libpcap.

Recovered G.hn discovery evidence includes:

- `make_GHN_DISCOVERY_Packet`
- `ghnScanMXLLocalDev`
- `_MACDiscoverGet`
- raw-Ethernet transmission through `pcap_sendpacket`
- EtherType `0x2e00`
- broadcast and `00:b0:52:00:00:01` discovery destinations
- optional `0x8100` VLAN framing in the generic sender

The exact payload fields, opcodes, reply validation, capture filters, retry schedule, and current Windows dispatch remain runtime targets.

See [tpPLC companion findings](context/findings-companion-utility.md) and [network protocol findings](context/findings-network-protocols.md).

## Read-only CLI

The Python CLI owns HTTP lifecycle, login, token use, response parsing, logout, and terminal-safe output. It intentionally exposes no firmware, reset, reboot, pairing, password, or configuration-write surface.

### Requirements

- Python `3.13+`
- [uv](https://docs.astral.sh/uv/)
- a reachable, owned PG2400P adapter

### Install and inspect

```bash
git clone git@github.com:MikeeI/tp-link-pg2400p-reverse-engineering.git
cd tp-link-pg2400p-reverse-engineering
uv sync --locked

export PG2400P_PASSWORD='<management-password>'

uv run pg2400p auth-check --host <device-ip>
uv run pg2400p info --host <device-ip> --json
uv run pg2400p peers --host <device-ip> --json
uv run pg2400p settings --host <device-ip> --json
uv run pg2400p status --host <device-ip> --json
```

Human output is deterministic `key=value` text. `--json` emits one JSON value on stdout and keeps diagnostics on stderr. The hidden telemetry set is proven live but is not yet a public CLI command.

See [CLI findings](context/findings-cli.md).

## Firmware and research data sources

Use firmware for the matching hardware revision and region. The analyzed artifacts are PG2400P KIT EU V1 releases.

| Artifact | Official source | SHA-256 |
| --- | --- | --- |
| PG2400P EU V1 `1.0.3 Build 20221213` | [TP-Link CDN](https://static.tp-link.com/upload/firmware/2023/202302/20230202/PG2400P_V1_221213.zip) | `1175f14f34b2f85c1dfe2a8bac558d711be27b1177fa0844bda566a3f8f37643` |
| PG2400P EU V1 `1.1.0 Build 20250710` | [TP-Link CDN](https://static.tp-link.com/upload/firmware/2025/202508/20250827/PG2400P%28EU%29_V1_250710.zip) | `3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13` |
| Firmware history and manuals | [TP-Link UK support](https://www.tp-link.com/uk/support/download/pg2400p-kit/) | Recorded per release |
| Windows and macOS tpPLC | [TP-Link US support](https://www.tp-link.com/us/support/download/pg2400p-kit/) | Recorded per asset |
| Current G.hn data model | [Broadband Forum TR-181](https://github.com/BroadbandForum/cwmp-data-models/blob/306acd3dcf783fd26d3d9281afe73986f4325933/tr-181-2-21-0-ghn.xml) | Upstream source |
| G.hn performance model | [Broadband Forum TR-476](https://www.broadband-forum.org/pdfs/tr-476-1-0-0.pdf) | Upstream source |
| MaxLinear SCT behavior | [DMI920 EVK guide](https://www.maxlinear.com/document?id=23298) | Upstream source |

Vendor firmware, applications, captures, and decompiler databases are not committed. The repository retains hashes, provenance, normalized inventories, protocol maps, exact read-only samples, and compact extracted knowledge. Each `asset-metadata.txt` records the official URL, acquisition time, artifact identity, and hashes needed to reproduce the starting point.

## Evidence map

| Question                         | Evidence owner                                                           |
| -------------------------------- | ------------------------------------------------------------------------ |
| Which firmware was analyzed?     | [Firmware identity](context/findings-firmware-identity.md)               |
| How is the package structured?   | [Architecture and processes](context/findings-architecture-processes.md) |
| What does the local API expose?  | [Web API](context/findings-web-api.md)                                   |
| Which hidden diagnostics work?   | [G.hn telemetry](context/findings-ghn-telemetry.md)                      |
| How does authentication work?    | [Authentication and cryptography](context/findings-auth-crypto.md)       |
| How does tpPLC discover devices? | [Companion utility](context/findings-companion-utility.md)               |
| What changed between releases?   | [Version comparisons](context/findings-version-comparisons.md)           |
| What does the CLI support?       | [Read-only CLI](context/findings-cli.md)                                 |
| What is known about updates?     | [Update and signing](context/findings-update-signing.md)                 |

Compact artifact inventories and protocol maps live under `data/extracted-*/extracted-knowledge/`. Raw captures and vendor binaries remain local and ignored.

## Known limits

- exact Xtensa core, ABI, RTOS, reset vector, and physical flash map remain unresolved
- no direct per-subcarrier SNR value was retrieved
- `FLOWMONITOR.STATS.LINK_STATUS` returns `ERROR=009` without an enabled monitor state
- device-side firmware signature and secure-update enforcement remain unresolved
- raw G.hn discovery payload and reply parsing remain unresolved
- no live configuration mutation, pairing change, reset, reboot, or firmware flash was performed

## Safety boundary

- live tooling is read-only by design
- arbitrary ConfigLayer access and mutation commands are not exposed
- firmware, reset, pairing, and configuration operations require separately proven semantics, validation, and rollback
- firmware and extracted content are treated as untrusted input and are never executed on the analysis workstation
