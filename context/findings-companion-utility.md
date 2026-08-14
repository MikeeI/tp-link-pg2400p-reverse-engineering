# Official tpPLC Companion Utility

## Evidence Scope

- [confirmed] Current Windows asset: `data/assets/tpPLC-2.3.5940.20-windows-PowerLineUtility.zip`.
  SHA-256: `c3375a2842ca6981eb1fddae2257b06680cb914372df679ccd1517f956de69ef`.
- [confirmed] Official source: `https://www.tp-link.com/us/support/download/pg2400p-kit/`.
- [confirmed] The page labels the Windows utility `2.3.5940.20`, published 2026-06-16.
- [confirmed] Its embedded Electron package reports version `2.3.5793.19` and build date `20251010`.
  No evidence explains this vendor-label and payload mismatch.
- [confirmed] Official macOS asset: `data/assets/tpPLC-12.5-macos-PowerlineUtility.zip`.
  SHA-256: `b48356c6b31d572c5fe8e52d3bbff68a262bcfe970514affa12cde870f32e17e`.
- [confirmed] The official page says the macOS utility newly supports PG2400P, PG2405P, and PG1200.
- [confirmed] Each `data/extracted-tpplc-*/extracted-knowledge/` directory records provenance and extraction.

## Current Windows Ownership

- [confirmed] `tpplc.exe` is a PE32 Electron GUI with Electron 22.3.27 and one `app.asar`.
- [confirmed] `_build/js/plcmw.js` sets `UAPI_PATH` to `plcu.exe` and spawns it as a server.
  The same bridge invokes `plcu.exe <command>` for JSON-on-stdout requests.
- [confirmed] `plcu.exe` imports PLC operations from `plcoperation.dll`.
- [confirmed] `plcoperation.dll` directly imports `WPCAP.DLL` and `PACKET.DLL`.
  It owns libpcap-style capture and send operations, G.hn strings, and the capture-filter format.
- [confirmed] `plcoperation.dll` delegates HyFi IP and HTTP operations to `hyfiinfotran.dll`.
- [confirmed] `plcu.exe` contains `Couldn't load Npcap`.
- [confirmed] The extracted cabinet contains no `.sys`, `.inf`, or `.cat` capture-driver file.
- [likely] Windows uses Npcap through the WinPcap-compatible DLL boundary.
  An isolated Windows trace must establish the installed driver and fallback behavior.

## Explicit PG2400P Behavior

- [confirmed] `raw/asar/_build/ui.build.js:6092-6106` checks `model.indexOf("PG2400P 1.0")`.
  The matched branch opens the official PG2400P support page.
- [confirmed] The adjacent `website` action opens the discovered device IP through Windows Explorer.
- [confirmed] The current native payload contains `G.hn1200`, `G.hn2400`, `GHN_DEVICE`, and `G.hn_%02x%02x`.
- [likely] G.hn strings and the raw-capture owner establish the current Windows discovery lane.
  No static G.hn model-to-dispatch callsite was recovered.
- `RUNTIME-NEEDED`: trace only `plcu.exe rescan` in an isolated Windows VM without owned devices reachable.

## Companion Command Boundary

- [confirmed] The renderer constructs the following backend commands:
  `rescan`, `getnmk`, `getqos`, `getmode`, `getPowerSaving`, `getwifi`, `login`, `setled`, `setleds`,
  `reset`, `setqos`, `setmode`, `setPowerSaving`, `adddev`, `setnpws`, `rmdev`, `upgrade`, `setwifi`,
  `setConfig`, and `save_exit`.
- [confirmed] `login` places URI-encoded username and password values in the `plcu.exe login` command string.
- [confirmed] `upgrade` passes one MAC address and two selected paths to `plcu.exe upgrade`.
- `BLOCKED`: no companion command ran because the current backend mixes reads and mutations.

## HTTP, Credentials, and Firmware

- [confirmed] `hyfiinfotran.dll` contains `POST /userRpm/appPost HTTP/1.1`.
- [confirmed] It also contains `POST /admin/firmware?form=upgrade HTTP/1.1` and `POST /?code=7&asyn=1 HTTP/1.1`.
- [confirmed] Its exported surface covers HyFi scan, login, Wi-Fi and PLC parameters, and upgrades.
- [confirmed] The macOS backend forms cookie material from Base64 credentials plus `simpleEncode`.
  When GDPR data exists, it uses AES data encryption and RSA public-key encryption for key material.
- [likely] These HyFi HTTP routes are not the PG2400P G.hn control plane.
  No recovered model branch ties PG2400P to `HyfiInfoTran`.
- [confirmed] Generic QCA, BCM, MSE, HyFi, APFW, and L2 firmware surfaces exist.
- `BLOCKED`: no artifact evidence binds a PG2400P model branch to an update implementation.

## Read-only Protocol Outcome

- [confirmed] The macOS backend uses direct raw-Ethernet discovery through libpcap and EtherType `0x2e00`.
  Exact anchors are in `data/extracted-tpplc-12.5-macos/extracted-knowledge/protocol-map.md`.
- `RUNTIME-NEEDED`: payload opcodes, receive validation, filters, retries, and Windows equivalence remain unresolved.
