# macOS tpPLC G.hn transport and management evidence

## `[confirmed]` Raw discovery transport

Artifact: `raw/dmg/TP-LINK PLC Utility/tpPLC.app/Contents/Resources/plcu`, SHA-256 `a3dd21ab03210a94589b9254c05f9e7930eae4d94b6031daff6106f458127a81`.

Ghidra 12.1.2 loaded it as Mac OS X Mach-O, `x86:LE:64:default:gcc`, image base `0x100000000`, read-only disposable project, default analyzers, 180-second per-file timeout; analysis completed in 45 seconds without timeout.

- `make_GHN_DISCOVERY_Packet` is at virtual address `0x100062d30`, file offset `0x62d30`; its body SHA-256 is `798739fb2cc39526ae70e46d25521ebc61bece3ab6d751bdcd7bff38b3251f2a`.
- Original bytes at file offset `0x62da8` are `66 c7 45 a6 2e 00`; Ghidra listing/decompiler identifies this as the Ethernet protocol field initialized to `0x002e`, which is emitted in network byte order as EtherType `0x2e00`.
- `_SendPcapPacket` is at virtual address `0x1000b7b10`; its decompilation initializes a raw Ethernet frame, optionally inserts an `0x8100` VLAN tag, and invokes `pcap_sendpacket` with a 60-byte untagged or 64-byte VLAN-tagged frame.
- `initDiscoveryDestAv` at `0x1000bc5d0` writes broadcast `ff:ff:ff:ff:ff:ff` for audience 0 and `00:b0:52:00:00:01` for audience 1.
- `ghnScanMXLLocalDev` at `0x100060d60` first obtains an interface name and then invokes `_MACDiscoverGet`.
- `_MACDiscoverGet` at `0x1000b7680` enumerates interfaces, creates one worker per interface, waits for results, and returns the final discovery result.

The artifact separately contains the G.hn-specific packet constructor, the G.hn scanner path, and a libpcap raw-Ethernet send owner.

- Confidence: `confirmed` for those static owners and for the packet-constructor EtherType bytes.
- Confidence: `likely` that the recovered raw-send path carries the constructed G.hn discovery frame because no direct constructor-to-send caller was recovered.
- Action: `RUNTIME-NEEDED` for the complete opcode/payload layout, capture filter, receive validation, retry timing, and current Windows applicability.

## `[confirmed]` G.hn IP/configuration layer

`ghnMXLGetIP` at virtual address `0x100062450` calls `configlayerGetParam` with `TCPIP.IPV4.IP_ADDRESS`, then falls back to `TCPIP.IPV4.ADDITIONAL_IP_ADDRESS` and strips its comma suffix.
This confirms the backend can obtain a G.hn device IPv4 address through its configuration layer.
It does not establish that any following HTTP route is used for PG2400P management.

- Confidence: `confirmed`.
- Action: `RUNTIME-NEEDED` for exact config-layer packet encoding and response semantics.

## `[confirmed]` HTTP/JSON management, credential handling, and scope limit

`JsonCommand::MakeHttpJsonObject` at `0x1000a6510` builds HTTP POST request bytes from `_NO_AUTH_POST`, `_HOST`, `_HOST_SUFFIX`, and `_CONTENT_LEN`.
Resolved Mach-O data pointers show `_NO_AUTH_POST` is `POST /userRpm/appPost HTTP/1.1\r\n`, `_HOST` is `Host:`, and `_CONTENT_LEN` is `Content-Length:`.
The function serializes a JSON `cookie` field from Base64 credential material then `simpleEncode` when GDPR data is absent; when GDPR data is present it AES-encodes the payload and RSA-public-encrypts key material into JSON `sign` and `data` fields.
`JsonCommand::MakeRequestLoginDevServerPacket` at `0x1000a8d90` builds an `admin` object containing `issetpwd` and `cookie`, then a `systool` object with `method: "do"` before calling `MakeHttpJsonObject`.

The native backend also contains `/admin/firmware?form=upgrade`, `POST /admin/firmware?form=upgrade HTTP/1.1`, and `POST /?code=7&asyn=1 HTTP/1.1` strings.
The classes/functions are named `HyfiInfoTran`, `JsonCommand`, `LoginDevServer`, and `UpgradeHyfi`; no static model branch ties those HTTP surfaces to PG2400P.

- Confidence: `confirmed` for HTTP construction, credential transforms, and route strings.
- Confidence: `likely` that this is a HyFi-specific path rather than the PG2400P G.hn control path.
- Action: `RUNTIME-NEEDED` for route-to-product binding; capture an isolated known HyFi target separately or reconstruct the MXL config-layer protocol.

## `[confirmed]` PG2400P UI anchor and generic firmware boundary

`raw/dmg/TP-LINK PLC Utility/tpPLC.app/Contents/Resources/_build/ui.build.js:5819-5825` checks `model.indexOf("PG2400P 1.0")` and opens the official PG2400P support URL; adjacent branches cover PG1200 and PG2405P.
The UI also differentiates `type_ghn` and `type_ghn_hyfi` (`ui.build.js:6032-6047`).
The bridge exposes a generic `upgrade` method, but this static UI anchor does not select a model-specific firmware implementation.

- Confidence: `confirmed` for explicit PG2400P support routing and generic update UI.
- Action: `BLOCKED` for PG2400P update flow; next proof is a known G.hn model dispatch/call graph or an isolated disposable-device trace.
