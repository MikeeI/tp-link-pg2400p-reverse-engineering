# TP-Link PG2400P Reverse Engineering

## Purpose

This repository records evidence-backed reverse engineering of the TP-Link PG2400P device.
It covers firmware, boot, services, protocols, updates, and companion software.

Canonical platform methodology lives in the applicable reverse-engineering skills.
Do not duplicate generic acquisition, extraction, decompilation, tracing, patching, or tool instructions here.
Keep this file as the project-local router and current-state record.
Keep detailed evidence in `context/findings-*`.

## Mission and Completion Boundary

Reverse the owned TP-Link PG2400P system as completely as evidence permits.
Cover hardware identity, firmware containers and filesystems, boot and update chains, and product-owned binaries.
Cover the web UI and HTTP API, authentication, configuration, G.hn status and control, and discovery protocols.
Cover official tpPLC software, runtime traffic, security boundaries, and version differences.

Produce reproducible evidence and a safe PG2400P CLI.
First implement read-only discovery, status, diagnostics, configuration export, peer enumeration, and link rates.
Keep mutation support separate, explicit, and guarded.
Permit a mutation only after its exact request, state effect, validation, and rollback are known.

Map every reachable surface with artifact plus callsite or runtime evidence.
Otherwise, record a precise unresolved gap and its next proof method.
Broad string inventories, screenshots, and decompiler output alone are not completion.

## Test Authorization

New tests are authorized only under `tests/`.
They may cover protocol codecs, authentication parsing, HTTP request shape, fixtures, CLI output, and mutation guards.
Live-device tests require an explicit test name and invocation naming the bounded read-only target.

## Authorization and Live Targets

- User authorization is established for this target and scope.
- Owned live devices: `10.0.1.184` (`8C:90:2D:10:49:E2`) and `10.0.1.185` (`3C:64:CF:59:D4:88`).
- Management transport currently observed: plain HTTP on port `80`.
- Management credential: password `MAJXxPtx24PE3wXBXekod4Ut`.
- Authorized work includes official artifact acquisition, extraction, static analysis, and decompilation.
- It includes bounded read-only requests, browser inspection, passive capture, and isolated companion execution.
- It includes protocol reconstruction, version diffing, vulnerability research, and interoperable tooling.
- Preserve device availability and configuration during discovery.
- Do not flash, reset, pair, reboot, write NVRAM, alter settings, or call endpoints with unknown effects.
- A live mutation requires a known endpoint, expected transition, pre-state capture, rollback, and task owner.
- Prefer emulation, extracted assets, isolated companion tracing, or reversible lab state over live mutation.

## Project Identity

- Device: TP-Link PG2400P
- Vendor: TP-Link
- Product class: G.hn2400 passthrough powerline adapter
- Hardware revision: `1.0` on both live devices; official artifacts are PG2400P KIT EU V1
- Firmware version: `1.0.3 Build 20221213 Rel.62540` on both live devices
- Firmware source URL: `https://www.tp-link.com/uk/support/download/pg2400p-kit/`
- Architecture: Xtensa8 indicated by official firmware strings; exact CPU/ABI unresolved
- Operating system: no Linux filesystem or ELF evidenced; firmware/RTOS-like stack is a working inference
- Project path: `$HOME/projects/REVERSE/project-reverse-device-tplinkpg2400p`
- Current readiness: `live-readonly-and-static-firmware-evidenced`
- Current provenance: bounded live capture plus two immutable official EU V1 firmware ZIPs with parser-only extraction
- Current action status: `NOW`

## Current Asset

```text
model = TP-Link PG2400P KIT
hardwareRevision = V1 (official artifact label; live hardware reports 1.0)
firmwareVersion = 1.1.0
build = 20250710
region = EU
architecture = Xtensa8 [likely; artifact strings only]
containerFormat = ZIP > proprietary .ftp > carved XZ raw firmware + XZ POSIX TAR FFS
sizeBytes = 2863018
sha256 = 3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13
signatureState = no detached signature or signed-container metadata acquired
sourceUrl = https://static.tp-link.com/upload/firmware/2025/202508/20250827/PG2400P(EU)_V1_250710.zip
redirectChain = direct HTTP/2 200; no redirects
userAgentContext = Chrome 138 Linux UA; curl TLS verification succeeded
provenance = official TP-Link support page to static.tp-link.com CDN
sourceTrust = official
acquiredAt = 2026-08-14T01:46:21Z
assetPath = data/assets/PG2400P-EU-V1-1.1.0-build-20250710.zip
extractedPath = data/extracted-1.1.0-build-20250710-v1/
notes = current official EU V1 release; prior 1.0.3 is retained intact
```

## Versionen

Newest first.
Never derive versions or hardware revisions from filenames when artifact metadata is authoritative.

| Firmware | Build | Hardware | Region | Arch | OS/Stack | Format | Datum | Provenienz | Quelle | SHA256 | Notizen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1.1.0 | 20250710 / Rel.56841 | PG2400P KIT EU V1 | EU | Xtensa8 [likely] | raw firmware + FFS web TAR; OS unresolved | ZIP / `.ftp` | 2025-08-27 | official | static.tp-link.com | `3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13` | decoded release string confirms version |
| 1.0.3 | 20221213 / Rel.62540 | PG2400P KIT EU V1 | EU | Xtensa8 [likely] | raw firmware + FFS web TAR; OS unresolved | ZIP / `.ftp` | 2023-02-02 | official | static.tp-link.com | `1175f14f34b2f85c1dfe2a8bac558d711be27b1177fa0844bda566a3f8f37643` | live devices report this build |

## Pfade

- Assets: `data/assets/`
- Current extraction: `data/extracted-{version}-{hardware}/`
- Raw extraction: `data/extracted-{version}-{hardware}/raw/`
- Extracted knowledge: `data/extracted-{version}-{hardware}/extracted-knowledge/`
- Decompiled/disassembler output: `data/extracted-{version}-{hardware}/decompiled/`
- Dynamic traces: `data/extracted-{version}-{hardware}/dynamic/`
- Captures: `data/captures/`
- Live extracted knowledge: `data/extracted-live/extracted-knowledge/`
- Findings: `context/`
- Curated synthesis: `docs/`
- Subagent notes: `data/subagents/`

## Skill Router

Select by observed artifact, not by repository name or assumption.

| Surface | Owning skill | Boundary |
| --- | --- | --- |
| Firmware filesystem, ELF binaries, init, services, IPC, persistence, runtime | `skill-reverse-linux` | Primary lane when embedded Linux is evidenced |
| APK/XAPK companion app | `skill-reverse-android` | Android package and runtime only |
| IPA companion app | `skill-reverse-ios` | iOS package and Apple mobile binary only |
| Electron desktop companion | `skill-reverse-electron` | ASAR, main/preload/renderer, IPC, web assets |
| macOS app or installer | `skill-reverse-mac` | DMG/PKG/app bundle and macOS integration |
| Native disassembly/decompilation | `skill-ghidra` or `skill-radare2` | Load the selected tool skill before use |
| Packet captures and protocol reconstruction | `skill-tshark` | PCAP/PCAPNG inspection and extraction |
| Android decompilation | `skill-jadx` | DEX/APK Java/Kotlin reconstruction |

Before every deep dive, load the owning platform skill plus `skill-xray`, `skill-expert`, and `skill-brutal`.
Use their thinking methods without copying their response formats.

## Knowledge Router

Keep compact, reproducible evidence in `extracted-knowledge/`.
Do not commit raw firmware, filesystems, decompiler databases, packet captures, core dumps, or broad traces.

| Artifact | Path | Current truth | Next |
| --- | --- | --- | --- |
| Asset identity and provenance | `data/extracted-{version}-{hardware}/extracted-knowledge/asset-metadata.txt` | present for both acquired EU V1 releases | retain immutable assets |
| Container and partition inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/container-inventory.txt` | ZIP / `.ftp` / XZ / FFS TAR parsed; component schema unresolved | establish physical flash map |
| Filesystem inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/filesystem-inventory.txt` | FFS TAR and every web XZ asset parsed | bind deploy/mount behavior |
| Binary and architecture inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/binary-inventory.txt` | raw payload; Xtensa8 indicated, no ELF/load map | establish raw-image map |
| Services and process map | `data/extracted-{version}-{hardware}/extracted-knowledge/process-map.md` | static web/filesystem symbols only | recover activation/xrefs |
| Network and protocol map | `data/extracted-{version}-{hardware}/extracted-knowledge/protocol-map.md` | root/form client grammar and mapped keys recovered | bind server handlers |
| Tool versions and failures | `data/extracted-{version}-{hardware}/extracted-knowledge/toolchain.txt` | present for both releases | use only bounded next parser |
| Safe read-only CLI | `src/pg2400p_cli/` and `context/findings-cli.md` | live-verified on both devices | extend only from proven semantics |
| Raw subagent notes | `data/subagents/` | empty | use only for separable analysis lanes |

## Findings Router

| Topic | File | Current truth | Confidence | Action status | Next proof |
| --- | --- | --- | --- | --- | --- |
| Firmware identity | `context/findings-firmware-identity.md` | live 1.0.3 bound to two official EU V1 artifacts | confirmed | `NOW` | explain 1.1.0 security changes |
| Hardware and boot chain | `context/findings-hardware-boot.md` | unknown | | `BLOCKED` | hardware revision and image inventory |
| Architecture and processes | `context/findings-architecture-processes.md` | raw non-ELF payload; Xtensa8 indicated; static service names | confirmed/likely | `RUNTIME-NEEDED` | raw-image map and xrefs |
| Network services and protocols | `context/findings-network-protocols.md` | bounded TCP/HTTP, peer, and link status captured | confirmed | `NOW` | non-HTTP discovery and framing |
| Web interface and API | `context/findings-web-api.md` | live root/form contract plus version-scoped static evidence | confirmed/likely | `NOW` | versioned handler implementation |
| Auth and cryptography | `context/findings-auth-crypto.md` | MD5 login and `_t` token flow captured on both devices | confirmed | `NOW` | token lifecycle and server validation |
| Storage and configuration | `context/findings-storage-config.md` | authenticated configuration snapshots captured | confirmed | `RUNTIME-NEEDED` | persistent storage ownership |
| Update and signature flow | `context/findings-update-signing.md` | CRC and encryption-state evidence; signature call graph unresolved | confirmed/likely | `BLOCKED` | isolated updater xrefs |
| Vulnerability and patch research | `context/findings-security.md` | not started | | `BLOCKED` | named reachable boundary |
| Version comparisons | `context/findings-version-comparisons.md` | normalized web/key comparison complete | confirmed | `NOW` | compare raw code after load mapping |
| Read-only CLI | `context/findings-cli.md` | identity, settings, peers, rates, JSON, logout, and guards live-verified | confirmed | `NOW` | extend only from proven semantics |

## Status

- [x] Repository and project-local router initialized
- [x] Baseline folders and artifact ignore boundaries established
- [x] Exact product identity and hardware revision evidenced on both live devices.
- [x] Official firmware acquired with URL, time, size, SHA256, provenance, and immutable originals
- [x] Container, compression, FFS TAR, and web filesystem formats inventoried
- [ ] Architecture, ABI, bootloader, kernel, init, and product-owned binaries fully inventoried
- [x] Web UI, management services, authenticated read-only API, and G.hn status boundaries mapped
- [x] Safe read-only CLI implemented and verified against both live devices
- [x] Tool identities and material parser failures recorded
- [x] Runtime targets defined for material static gaps
- [x] Findings use claim-local confidence and independent action status.

## Aktuelle Top-Ziele

- Extend the CLI only for read semantics proven by artifact callsites and bounded runtime evidence.
- Compare installed 1.0.3 behavior with the security changes in official version 1.1.0.
- Establish the raw Xtensa load base, entry, CPU variant, boot component boundaries, and updater xrefs without executing firmware on a live adapter.
- Resolve whether `FLUPGRADE.GENERAL.SECURE` enforces encryption, signature verification, or another policy in an isolated target.
- Bind unrecovered write behavior to static callsites and controlled runtime evidence.

## Project-Specific Runtime Notes

```text
device ownership / serial = user-owned; serials not yet recorded
hardware revision = 1.0 on both live devices; official artifacts are KIT EU V1
recovery interface = unknown; do not probe electrically until hardware work is explicitly selected
UART / JTAG access = unknown
network isolation = management LAN 10.0.1.0/24; keep live probes bounded to owned device IPs
management address = 10.0.1.184 and 10.0.1.185
accounts = password-only web authentication; credential recorded in Authorization and Live Targets
proxy / capture point = workstation Ethernet path or isolated companion-software VM; record exact interface per capture
known blockers = persistent storage, non-HTTP discovery, token lifecycle, write-handler semantics, raw Xtensa load map, physical flash map, updater secure-policy branch, and versioned server-handler callsites
mutation-risk endpoints = firmware update, factory reset, reboot, pairing, network/password/QoS/LED/power-saving/compatibility writes, bootloader and NVRAM writes
allowed probes = bounded GET/HEAD/OPTIONS, authenticated read-only requests with known semantics, static asset retrieval, passive capture, port/service identification that does not exploit or exhaust the device
forbidden probes = destructive or availability-risking actions, credential spraying, unbounded fuzzing, firmware flashing, reset, reboot, pairing changes, and requests with unknown state effects against live devices
cleanup / rollback = close sessions and bounded captures; retain immutable evidence; a future authorized mutation must define and verify rollback before execution
```

## Analysis Discipline

- Treat firmware and extracted content as untrusted input.
- Begin with bounded parser-only extraction.
- Preserve original artifacts and bind conclusions to their SHA256, hardware revision, and firmware version.
- Separate `[confirmed]` evidence from `[likely]` inference.
- Track `NOW`, `RUNTIME-NEEDED`, and `BLOCKED` independently.
- Treat strings, imports, keys, routes, and schemas as candidates until a consumer or runtime trace proves use.
- Parser failures and empty output are not negative evidence.
- Record failures and use another parser or leave the claim open.
- Do not execute firmware binaries on the host.
- Use isolated emulation with explicit state, network, mutation, and rollback boundaries.
- Never overwrite an older extraction.
- Compare versions only after normalization and claim `unchanged` only for surfaces actually compared.
- Store detailed evidence in `context/findings-*`.
- Keep this file to current truths, routes, status, and target-specific constraints.

<essential-rule>
AGENTS.md is the authoritative project guidance and state router.
Update it whenever the artifact, readiness, paths, routers, status, or top targets change.

Multiple agents may work concurrently.
Preserve unrelated state and assign separable lanes with exact evidence, boundaries, criteria, and output paths.

Every cybersecurity assignment must state: `User authorization is established for this target and scope.`

Commit coherent completed units and push them.
Keep validation quiet and truthful.
Failures must identify the failed step and actionable evidence.
</essential-rule>
