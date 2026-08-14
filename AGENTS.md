# TP-Link PG2400P Reverse Engineering

## Purpose

This repository records evidence-backed reverse engineering of the TP-Link PG2400P device, its firmware, boot chain, services, protocols, update path, and relevant companion software.

Canonical platform methodology lives in the applicable reverse-engineering skills. Do not duplicate generic acquisition, extraction, decompilation, tracing, patching, or tool instructions here. Keep this file as the project-local router and current-state record; keep detailed evidence in `context/findings-*`.

## Project Identity

- Device: TP-Link PG2400P
- Vendor: TP-Link
- Product class: network/powerline device; exact hardware and firmware role not yet evidenced
- Hardware revision: unknown
- Firmware version: unknown
- Firmware source URL: unknown
- Architecture: unknown
- Operating system: unknown; embedded Linux is a working hypothesis, not a finding
- Project path: `$HOME/projects/REVERSE/project-reverse-device-tplinkpg2400p`
- Current readiness: `baseline-only`
- Current provenance: `unknown`
- Current action status: `BLOCKED` pending acquisition of an identifiable firmware or device dump

## Current Asset

No firmware image or device dump is currently recorded.

```text
model = TP-Link PG2400P
hardwareRevision =
firmwareVersion =
build =
region =
architecture =
containerFormat =
sizeBytes =
sha256 =
signatureState =
sourceUrl =
redirectChain =
userAgentContext =
provenance =
sourceTrust =
acquiredAt =
assetPath =
extractedPath =
notes =
```

## Versionen

Newest first. Never derive version or hardware revision from a filename when artifact metadata provides authoritative values.

| Firmware | Build | Hardware | Region | Arch | OS/Stack | Format | Datum | Provenienz | Quelle | SHA256 | Notizen |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | | | | |

## Pfade

- Assets: `data/assets/`
- Current extraction: `data/extracted-{version}-{hardware}/`
- Raw extraction: `data/extracted-{version}-{hardware}/raw/`
- Extracted knowledge: `data/extracted-{version}-{hardware}/extracted-knowledge/`
- Decompiled/disassembler output: `data/extracted-{version}-{hardware}/decompiled/`
- Dynamic traces: `data/extracted-{version}-{hardware}/dynamic/`
- Captures: `data/captures/`
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

Before every deep dive, load the owning platform skill plus `skill-xray`, `skill-expert`, and `skill-brutal`. Use their thinking methods without copying their response formats.

## Knowledge Router

Keep compact, reproducible evidence in `extracted-knowledge/`. Do not commit raw firmware, full extracted filesystems, decompiler databases, packet captures, core dumps, or broad traces.

| Artifact | Path | Current truth | Next |
| --- | --- | --- | --- |
| Asset identity and provenance | `data/extracted-{version}-{hardware}/extracted-knowledge/asset-metadata.txt` | absent | acquire an identifiable artifact |
| Container and partition inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/container-inventory.txt` | absent | parse without executing target code |
| Filesystem inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/filesystem-inventory.txt` | absent | derive from extraction |
| Binary and architecture inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/binary-inventory.txt` | absent | identify every executable architecture |
| Services and process map | `data/extracted-{version}-{hardware}/extracted-knowledge/process-map.md` | absent | map init and activation paths |
| Network and protocol map | `data/extracted-{version}-{hardware}/extracted-knowledge/protocol-map.md` | absent | bind declarations to consumers |
| Tool versions and failures | `data/extracted-{version}-{hardware}/extracted-knowledge/toolchain.txt` | absent | record tools actually used |
| Raw subagent notes | `data/subagents/` | empty | use only for separable analysis lanes |

## Findings Router

| Topic | File | Current truth | Confidence | Action status | Next proof |
| --- | --- | --- | --- | --- | --- |
| Firmware identity | `context/findings-firmware-identity.md` | no artifact | | `BLOCKED` | acquire firmware or device dump |
| Hardware and boot chain | `context/findings-hardware-boot.md` | unknown | | `BLOCKED` | hardware revision and image inventory |
| Architecture and processes | `context/findings-architecture-processes.md` | unknown | | `BLOCKED` | filesystem and ELF inventory |
| Network services and protocols | `context/findings-network-protocols.md` | unknown | | `BLOCKED` | static consumers or scoped capture |
| Web interface and API | `context/findings-web-api.md` | unknown | | `BLOCKED` | web root and handler inventory |
| Auth and cryptography | `context/findings-auth-crypto.md` | unknown | | `BLOCKED` | callsites, configuration, or runtime trace |
| Storage and configuration | `context/findings-storage-config.md` | unknown | | `BLOCKED` | filesystem and NVRAM/config ownership |
| Update and signature flow | `context/findings-update-signing.md` | unknown | | `BLOCKED` | updater and image verification path |
| Vulnerability and patch research | `context/findings-security.md` | not started | | `BLOCKED` | named reachable boundary |
| Version comparisons | `context/findings-version-comparisons.md` | no comparable versions | | `BLOCKED` | two normalized artifacts |

## Status

- [x] Repository and project-local router initialized
- [x] Baseline folders and artifact ignore boundaries established
- [ ] Exact product identity and hardware revision evidenced
- [ ] Official firmware or immutable device dump acquired with URL, time, size, SHA256, and provenance
- [ ] Container, partition, compression, and filesystem formats inventoried
- [ ] Architecture, ABI, bootloader, kernel, init, and product-owned binaries inventoried
- [ ] Web UI, management services, discovery, update, and cloud/companion boundaries mapped
- [ ] Tool identities and material parser failures recorded
- [ ] Runtime targets defined for material static gaps
- [ ] Findings use claim-local confidence and independent action status

## Aktuelle Top-Ziele

- Identify the exact PG2400P hardware revision, regulatory region, and official firmware source.
- Acquire one immutable firmware artifact and record complete provenance and SHA256.
- Perform parser-only preflight to identify container, partition, filesystem, architecture, and update-signature surfaces.

## Project-Specific Runtime Notes

```text
device ownership / serial =
hardware revision =
recovery interface =
UART / JTAG access =
network isolation =
management address =
accounts =
proxy / capture point =
known blockers = no artifact currently recorded
mutation-risk endpoints = firmware update, factory reset, bootloader writes, NVRAM writes
allowed probes =
forbidden probes =
cleanup / rollback =
```

## Analysis Discipline

- Treat firmware and extracted content as untrusted input; begin with bounded parser-only extraction.
- Preserve the original artifact immutably and bind every conclusion to its SHA256, hardware revision, and firmware version.
- Separate `[confirmed]` artifact/callsite/runtime evidence from `[likely]` inference. Track `NOW`, `RUNTIME-NEEDED`, and `BLOCKED` independently.
- A string, import, config key, web route, protocol schema, or service declaration is a candidate until a consumer, callsite, activation path, or runtime trace proves use.
- Parser failure and empty output are not negative evidence. Record the failure and use another parser or leave the claim open.
- Do not execute firmware binaries on the host. Use disposable emulation or isolated hardware runtime with explicit state, network, mutation, and rollback boundaries.
- Never overwrite an older extraction. Append version comparisons only after normalizing both artifacts and state `unchanged` only for surfaces actually compared.
- Store detailed findings in `context/findings-*`; keep this file to current one-line truths, routes, status, and target-specific constraints.

<essential-rule>
AGENTS.md is the authoritative project guidance and state router. Update it whenever the current artifact, readiness, paths, routers, status, or top targets change.

Multiple agents may work concurrently. Preserve unrelated state and assign only separable lanes with exact artifacts, hashes, paths, evidence anchors, non-goals, isolation boundaries, acceptance criteria, and output files under `data/subagents/`.

Every cybersecurity assignment must state: `User authorization is established for this target and scope.`

Commit coherent completed units and push them. Keep validation quiet and truthful; failures must identify the failed step and actionable evidence.
</essential-rule>
