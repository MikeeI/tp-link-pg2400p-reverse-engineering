# Current Windows tpPLC transport map

## `[confirmed]` Owners

- `raw/asar/_build/js/plcmw.js` is the Electron renderer command adapter.
- `plcu.exe` is the spawned server and one-shot command executable on Windows.
- `plcoperation.dll` is the raw packet/capture and PLC operation owner.
- `hyfiinfotran.dll` is the HyFi IP/HTTP management owner behind `plcoperation.dll`.

## `[confirmed]` Discovery and G.hn

`plcmw.js:100-113` maps UI rescan to `plcu.exe rescan` and parses its stdout as JSON.
`plcu.exe` imports `findAllAdapterNetwork` from `PLCOperation.dll`.
`plcoperation.dll` directly imports `WPCAP.DLL` and `PACKET.DLL` and contains the libpcap capture/send symbols documented in `binary-inventory.txt`.
The same DLL contains `GHN_DEVICE`, `G.hn_%02x%02x`, and an Ethernet-destination/EtherType filter format.
This proves the current Windows stack contains raw-Ethernet G.hn discovery machinery, but static evidence does not yet identify the one `rescan` dispatch branch or packet capture timing.

- Confidence: `confirmed` for ownership and capture API.
- Action: `RUNTIME-NEEDED` for packet sequence, device matching, and reply parser.
- Next proof: run only `plcu.exe rescan` in an isolated Windows VM with a disposable capture NIC and no owned devices reachable, then correlate process and pcap output.

## `[confirmed]` PG2400P-specific current UI behavior

`raw/asar/_build/ui.build.js:6092-6106` matches `model.indexOf("PG2400P 1.0")` and opens `https://www.tp-link.com/support/download/pg2400p-kit/`.
`raw/asar/_build/ui.build.js:6118-6120` also opens the discovered device `ip` through `tpPLC.os.website`.
`plcmw.js:385-388` implements Windows `os_website` as `explorer ` plus the supplied IP.
This is a confirmed support-routing and browser-management affordance, not proof that the HTTP management API is used for PG2400P control.

- Confidence: `confirmed`.
- Action: `NOW` for static support/model evidence.

## `[confirmed]` Command and mutation boundary

The adapter constructs these `plcu.exe` commands: `rescan`, `login`, `setled`, `setleds`, `reset`, `getqos`, `setqos`, `getmode`, `setmode`, `getPowerSaving`, `setPowerSaving`, `adddev`, `setnpws`, `rmdev`, `upgrade`, `getwifi`, `setwifi`, `calnmk`, `getnmk`, `getConfig`, `setConfig`, and `save_exit`.
`login` passes MAC, URI-encoded username, and URI-encoded password in a shell command string (`plcmw.js:115-126`).
`upgrade` passes MAC and two user-selected file paths to `plcu.exe` (`plcmw.js:277-299`).
All commands except possibly discovery/status getters are unavailable for live probing under this project’s preserve-state rule.

- Confidence: `confirmed` for command construction.
- Action: `BLOCKED` for live execution; only a disposable VM/lab target with a state/rollback plan may exercise them.

## `[confirmed]` HyFi HTTP and firmware paths; `[likely]` not PG2400P

`hyfiinfotran.dll` contains `POST /userRpm/appPost HTTP/1.1` at 0x34e504, `POST /admin/firmware?form=upgrade HTTP/1.1` at 0x34dfec, and `POST /?code=7&asyn=1 HTTP/1.1` at 0x34e81c.
Its exported surface is named `HyfiInfoTran` and includes login, Wi-Fi/PLC parameter, scan, and upgrade operations.
The current payload has no `PG2400P` literal outside the Electron UI model routing and no static callsite joins that UI model condition to `HyfiInfoTran`.

- Confidence: `confirmed` for the HyFi route strings and exported operation ownership.
- Confidence: `likely` that these HTTP routes are not the PG2400P G.hn control path.
- Action: `RUNTIME-NEEDED` for route-to-device-type binding; capture a known HyFi test device separately or recover the Windows G.hn dispatch call graph.

## `[confirmed]` Firmware handling

`plcmw.js:277-299` exposes an `upgrade` bridge; `plcu.exe` imports QCA/BCM/MSE/HyFi upgrade functions; `plcoperation.dll` contains firmware block/retry strings; `hyfiinfotran.dll` contains the HTTP firmware-upgrade route.
No current Windows static evidence associates a PG2400P model branch with one of those upgrade paths.

- Confidence: `confirmed` for generic utility firmware-capable surfaces.
- Action: `BLOCKED` for PG2400P firmware handling; next proof is a bounded static Windows call graph from a confirmed G.hn model dispatch or a disposable-device trace.
