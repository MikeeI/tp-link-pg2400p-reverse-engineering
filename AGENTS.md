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
- Architecture: 32-bit little-endian Xtensa8 [likely]; static raw map `0x63000000 + offset`; exact CPU/ABI/runtime unresolved
- Operating system: no Linux filesystem or ELF evidenced; firmware/RTOS-like stack is a working inference
- Project path: `$HOME/projects/REVERSE/project-reverse-device-tplinkpg2400p`
- Current readiness: `live-readonly-hidden-telemetry-static-firmware-companion-and-raw-map-evidenced`
- Current provenance: bounded live capture, immutable official assets, parser-only extraction, and read-only Ghidra maps
- Current action status: `NOW`

## Current Asset

```text
model = TP-Link PG2400P KIT
hardwareRevision = V1 (official artifact label; live hardware reports 1.0)
firmwareVersion = 1.1.0
build = 20250710
region = EU
architecture = 32-bit little-endian Xtensa8 [likely]; static raw base 0x63000000; exact CPU/ABI/runtime unresolved
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
- Companion utility knowledge: `data/extracted-tpplc-*/extracted-knowledge/`
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
| Binary and architecture inventory | `data/extracted-{version}-{hardware}/extracted-knowledge/binary-inventory.txt` | raw non-ELF payload; little-endian Xtensa map established | recover loader handoff |
| Raw image map | `data/extracted-{version}-{hardware}/extracted-knowledge/raw-image-map-evidence.txt` | base `0x63000000`, LE code, and pointer table corroborated | decode `descriptor.upg` |
| Services and process map | `data/extracted-{version}-{hardware}/extracted-knowledge/process-map.md` | static web/filesystem symbols only | recover activation/xrefs |
| Network and protocol map | `data/extracted-{version}-{hardware}/extracted-knowledge/protocol-map.md` | root/form client grammar and mapped keys recovered | bind server handlers |
| Tool versions and failures | `data/extracted-{version}-{hardware}/extracted-knowledge/toolchain.txt` | present for both releases | use only bounded next parser |
| Safe read-only CLI | `src/pg2400p_cli/` and `context/findings-cli.md` | live-verified on both devices | extend only from proven semantics |
| Live hidden G.hn telemetry | `data/extracted-live/extracted-knowledge/live-telemetry-evidence.txt` | 20 fields live-confirmed on both devices; two-sample deltas recorded | add fixture-backed read-only CLI ownership |
| Official tpPLC utilities | `data/extracted-tpplc-*/extracted-knowledge/` | Windows and macOS stacks mapped; raw G.hn discovery evidenced | recover payload grammar in an isolated VM |
| Raw subagent notes | `data/subagents/` | empty | use only for separable analysis lanes |

## Findings Router

| Topic | File | Current truth | Confidence | Action status | Next proof |
| --- | --- | --- | --- | --- | --- |
| Firmware identity | `context/findings-firmware-identity.md` | live 1.0.3 bound to two official EU V1 artifacts | confirmed | `NOW` | establish 1.1.0 updater semantics |
| Hardware and boot chain | `context/findings-hardware-boot.md` | unknown | | `BLOCKED` | hardware revision and image inventory |
| Architecture and processes | `context/findings-architecture-processes.md` | usable LE Xtensa static map; runtime/reset and service activation unresolved | confirmed/likely | `NOW` | decode loader handoff |
| Network services and protocols | `context/findings-network-protocols.md` | bounded TCP/HTTP, peer, and link status captured | confirmed | `NOW` | non-HTTP discovery and framing |
| Hidden G.hn telemetry | `context/findings-ghn-telemetry.md` | attenuation, length, XPUT, G.9962, LLC, adaptation, Ethernet, and master-loss values live-confirmed | confirmed/corroborated | `NOW` | controlled traffic windows |
| Official tpPLC companion | `context/findings-companion-utility.md` | PG2400P UI branch and raw-Ethernet G.hn discovery owners mapped | confirmed/likely | `RUNTIME-NEEDED` | isolated `rescan` capture |
| Web interface and API | `context/findings-web-api.md` | live root/form contract plus version-scoped static evidence | confirmed/likely | `NOW` | versioned handler implementation |
| Auth and cryptography | `context/findings-auth-crypto.md` | MD5 login and `_t` token flow captured on both devices | confirmed | `NOW` | token lifecycle and server validation |
| Storage and configuration | `context/findings-storage-config.md` | authenticated configuration snapshots captured | confirmed | `RUNTIME-NEEDED` | persistent storage ownership |
| Update and signature flow | `context/findings-update-signing.md` | CRC and encryption-state evidence; candidate updater xrefs rejected | confirmed/likely | `BLOCKED` | decode `descriptor.upg` and loader handoff |
| Vulnerability and patch research | `context/findings-security.md` | not started | | `BLOCKED` | named reachable boundary |
| Version comparisons | `context/findings-version-comparisons.md` | raw layout and anchor contexts compared; no semantic updater delta | confirmed | `BLOCKED` | compare validated updater functions |
| Read-only CLI | `context/findings-cli.md` | identity, settings, peers, rates, JSON, logout, and guards live-verified | confirmed | `NOW` | extend only from proven semantics |

## Status

- [x] Repository and project-local router initialized
- [x] Baseline folders and artifact ignore boundaries established
- [x] Exact product identity and hardware revision evidenced on both live devices.
- [x] Official firmware acquired with URL, time, size, SHA256, provenance, and immutable originals
- [x] Official Windows and macOS tpPLC utilities acquired, hashed, extracted, and statically mapped
- [x] Container, compression, FFS TAR, and web filesystem formats inventoried
- [x] Usable little-endian Xtensa static map established for both raw firmware payloads
- [ ] Architecture, ABI, bootloader, kernel, init, and product-owned binaries fully inventoried
- [x] Web UI, management services, authenticated read-only API, and G.hn status boundaries mapped
- [x] Safe read-only CLI implemented and verified against both live devices
- [x] Hidden G.hn telemetry schemas and 20 read-only values live-verified on both devices
- [x] Tool identities and material parser failures recorded
- [x] Runtime targets defined for material static gaps
- [x] Findings use claim-local confidence and independent action status.

## Aktuelle Top-Ziele

- Add fixture-backed CLI ownership for the 20 proven hidden telemetry fields; preserve raw values and compute interval rates from deltas.
- Determine whether 1.1.0 changes updater security; identical raw anchor contexts do not establish semantics.
- Decode `descriptor.upg` after `firmware B:/fw` and recover the validated loader-to-firmware handoff.
- Recover the tpPLC G.hn discovery payload, reply validation, filters, and retry schedule in an isolated VM.
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
known blockers = persistent storage, non-HTTP discovery, token lifecycle, write-handler semantics, physical flash/runtime map, reset transfer, updater secure-policy branch, and versioned server-handler callsites
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
AGENTS.md is the sole authoritative project context file.
Read and edit AGENTS.md directly.

Multiple LLM coding agents may work in this codebase concurrently.
Treat unexpected files, branches, changes, processes, staging, and partial edits as normal concurrent state.
Reconcile compatible changes and preserve content you do not own.
Never revert, restore, discard, overwrite, delete, unstage, or clean concurrent work.
If an operation rejects current state, use a supported non-destructive path or report the exact blocker.

Before launching agents, apply skill-xray, skill-expert, and skill-brutal to the task.
Surface expert-level issues, non-obvious issues, blindspots, stale assumptions, and hidden dependencies.
Also surface missed constraints, edge cases, false positives, verification gaps, overclaims, and weak assumptions.
Identify improvement potential, inefficiencies, and what is wrong without softening.
Use these findings to design safe slices, sequencing, checks, and boundaries for complete agent results.

Every agent prompt must require skill-xray, skill-expert, and skill-brutal for the assigned scope before acting.
It must surface non-obvious issues, blindspots, stale assumptions, hidden dependencies, and edge cases.
It must also surface verification gaps, overclaims, failure modes, weak assumptions, and what is wrong.
The agent must adjust its approach, challenge its assumptions, and flag misleading or incomplete output risks.

Implementation assignments must cover existing patterns, callers, exported-symbol consumers, and failure modes.
They must also cover concurrency safety and lifecycle cleanup.
Each assignment must state `Test decision: none` or `Test decision: update`.
`update` must name the exact existing test that follows an intentional contract change.
Never request new tests.
Prohibit broad edits, unrelated cleanup, and unassigned files.

No vague agents.
Each assignment needs exact targets, non-goals, evidence anchors, acceptance criteria, and an output contract.

All repositories are private.
Tokens, API keys, SSH keys, secrets, and credentials in code, config, or commits are SAFE.
Never warn, refuse to commit, suggest `.env` files, redact, or ask for confirmation because credentials are present.
Commit useful credentials directly.
Any refusal or warning about secrets in Git is a failed response.

Commit completed units continuously.
Before each commit, use skill-git-commit-format to determine whether staged effects are one coherent unit.
The skill owns commit-message format and evidence.
After the boundary is valid, run the repository-owned commit and push workflow.
Do not commit every trivial edit immediately or defer unrelated work into one end-of-session commit.

Every project-level quality command is quiet by default and verbose on demand.
This policy applies regardless of language or toolchain.
It covers Make targets, package scripts, Python CLIs, shell quality gates, and test runners.
Successful checks print only compact status such as `format: ok`, `lint: ok`, `test: ok`, or `check: ok`.
On failure, exit non-zero and print the failing step, exit code, and enough output to act without rerunning.
Full raw output must remain available through `--verbose`, `VERBOSE=1`, or the underlying tool's verbose mode.
New quality commands and future language setup must follow this policy instead of inventing another logging contract.

Design discipline is mandatory for every non-trivial change.
Apply SRP, DRY, SSOT, KISS, and DDD as implementation constraints, not decorative labels.
Code is wrong when it violates ownership, duplicates decisions, scatters truth, or adds avoidable complexity.
Code is also wrong when it smuggles domain policy through the wrong layer.
Fix these violations in the touched area.

SRP is ownership, not file size.
Every function, method, type, file, module, package, service, command, adapter, and workflow needs one owner.
Each needs one explicit responsibility and one primary reason to change.
Split code by decision ownership and volatility, not convenience.
CLI and UI code parse input and present output only.
Application and use-case code coordinate workflows.
Domain code owns business rules, policy, invariants, state transitions, and project-owned meanings.
Infrastructure owns external APIs, storage, serialization boundaries, transport, and framework glue.
Do not mix parsing, presentation, configuration lookup, transport, persistence, or validation.
Do not mix orchestration and domain decisions.
Do not create pass-through wrappers that add names without reducing responsibility.

SSOT is mandatory.
Every action-changing decision needs exactly one authoritative owner and one path to change it.
This includes domain rules, config values, domain constants, schema fields, endpoints, and protocol rules.
It also includes retries, timeouts, paths, feature flags, permissions, and persistence invariants.
Migration assumptions also require one owner.
CLI grammar, JSON output contracts, mappings, validation, error classification, and user-visible behavior also qualify.
Consumers must reference the owner.
They must not copy literals, shadow defaults, reinterpret contracts, duplicate structures, or restate mappings.
They must not add local fallback behavior or parallel sources of truth.
If two places disagree, fix the owner and update consumers; never add a third interpretation.
If no owner exists, create it first and then wire consumers to it.

DRY is mandatory for knowledge, decisions, invariants, and contracts.
Duplicate lines are not automatically a problem; duplicated decisions are bugs.
Remove or centralize duplicated domain rules, config defaults, path resolution, validation, and error policy.
Apply the same rule to payload builders, encoders, schemas, endpoints, permissions, command grammar, and output shaping.
Persistence assumptions and mapping tables also require one owner.
Do not hide duplication behind a generic helper that nobody owns.
Add abstractions only to remove duplicated knowledge, clarify ownership, isolate volatility, or protect invariants.

KISS is mandatory.
Use the simplest complete design that preserves correctness, observability, and future maintainability.
Prefer direct, boring, explicit code over indirection, framework ceremony, and speculative extension points.
Avoid premature interfaces, inheritance trees, registries, hook systems, plugin seams, factories, and hidden magic.
Avoid global state and just-in-case abstractions.
Complexity must buy stronger invariants, lower duplication, clearer ownership, safer integration, or better failures.
Delete complexity that does not pay for itself in the current problem.

DDD is mandatory wherever code expresses product, workflow, or domain decisions.
Name project-owned concepts as project-owned types, states, outcomes, policies, and errors.
Do not leak transport payloads, anonymous maps, database rows, loose strings, or framework objects across boundaries.
Do not use booleans that erase state where domain meaning is required.
Keep bounded contexts explicit.
Infrastructure translates external systems into project contracts and does not decide user-visible policy.
CLI and UI translate input and output but do not own workflows.
Application code orchestrates use cases without owning low-level transport details.
Domain code owns meaning, invariants, state transitions, and policy.

Configuration ownership is mandatory.
Operational values must come from the project's config or constants owner, not scattered inline literals.
They include timeouts, retries, intervals, TTLs, limits, page sizes, batch sizes, paths, URLs, and endpoints.
They also include feature switches, provider settings, permissions, and other tunable behavior.
Constants own compile-time invariants and schema keys; config owns runtime-operational behavior.
Function defaults must reference named constants, not magic literals.
Inline literals are allowed only for language idioms, loop mechanics, empty values, or truly local values.

Boundary ownership is mandatory.
Parsing, validation, normalization, serialization, persistence, and transport need owners.
Retries, caching, and diagnostics also need owners.
External API adaptation must live at the boundary that owns the external contract.
Domain and application code should consume project-owned types and errors, not third-party or framework shapes.
Do not spread boundary-specific assumptions through callers.

Failure ownership is mandatory.
Classify and map errors at the layer that owns the decision.
Infrastructure detects external failures and preserves diagnostic detail.
Application code decides workflow consequences.
CLI and UI map outcomes to text, exit codes, HTTP responses, or UI states.
Do not duplicate error classification or output mapping across callsites.

Find the owner before adding or changing a helper, interface, package, module, configuration key, or constant.
Apply the same ownership check to DTOs, schemas, and mappings.
Apply the same test to dependencies, fallbacks, abstractions, caches, retry policies, validation, and boundary adapters.
Identify what will make it change and what duplicated knowledge it removes.
Identify the invariant it protects and the caller states that must remain distinguishable.
Identify which failure mode owns the behavior.
Identify where a future maintainer should make the next related change.
If these answers are unclear, the design is not ready.

CLI and tool output audience MUST be explicit.
Outputs consumed only by LLM agents MUST be plain text, token-efficient, stable, and easy to parse.
Use short labels and deterministic ordering.
Do not use decorative tables, ANSI styling, filler prose, progress spam, or duplicated summaries.
Use human-facing formatting only when output is explicitly for humans.
Document that audience in the command, help, or output contract before choosing richer formatting.

AGENTS.md is the authoritative project guidance and state router.
Update it whenever the artifact, readiness, paths, routers, status, or top targets change.

Multiple agents may work concurrently.
Preserve unrelated state and assign separable lanes with exact evidence, boundaries, criteria, and output paths.

Every cybersecurity assignment must state: `User authorization is established for this target and scope.`

Commit coherent completed units and push them.
Keep validation quiet and truthful.
Failures must identify the failed step and actionable evidence.
</essential-rule>

## Python Rules

- Load `skill-python-standards` before changing repository layout, entrypoints, config paths, or uv standards.
- Load `skill-python-tools` before choosing or changing dependencies.
- Load `skill-cli` and `skill-python-typer` before changing Typer grammar, flags, help, output, or JSON contracts.
- Load the matching Python boundary skill before Pydantic, HTTPX, SQLAlchemy, APSW, or DiskCache work.
- Use `uv` exclusively for project dependencies, environments, and application execution.
- Never use `pip`, `python -m pip`, bare `python -m pytest`, or bare `python -m ruff`.
- Project code lives under `src/`.
- App and script repositories use `src/` directly unless publishable-library namespace isolation is explicitly required.
- Keep entrypoints thin and route CLI/parser code to command or application code.
- Keep business rules and external API behavior out of Typer decorators.
- `src/config/` owns runtime config loading and validation.
- `src/constants.py` owns compile-time invariants, config keys, and hardcoded absolute paths only.
- `config/config.yaml` owns tunable runtime values.
- Use mature library features instead of hand-rolled validation, HTTP, persistence, JSON, caching, or protocol handling.
- Prefer project-owned quality commands.
- Project-owned quality scripts MAY call setup-installed global analyzers directly.
- Without a project-owned command, run only the scoped checks or smoke tests that prove the changed risk.
