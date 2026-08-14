# Network services and protocols

## Bounded service inventory

- [confirmed] Nmap 7.94SVN TCP connect scan covered ports `1-1024,8080,8443` on each owned IP with no retries, 25 ms scan delay, and 75 s host timeout.
- [confirmed] Each device was up and had only `80/tcp open http` in that range.
- [confirmed] Nmap reported the remaining 1,025 targeted ports closed by connection refusal on each device.
- [confirmed] No claim is made for TCP ports outside that bounded set or for UDP services.
- [confirmed] ARP/neighbor resolution on `enp3s0` matched `.184 = 8c:90:2d:10:49:e2` and `.185 = 3c:64:cf:59:d4:88`.

## HTTP API protocol

- [confirmed] Plain HTTP root/form API behavior, `_t` tokenization, and `ERROR`/line-pair grammar are in `findings-web-api.md`.
- [confirmed] The G.hn status model uses `DIDMNG.GENERAL.NUM_DIDS`, `DIDMNG.GENERAL.MACS`, `DIDMNG.GENERAL.RX_BPS`, and `DIDMNG.GENERAL.TX_BPS` through authenticated GET requests.
- [confirmed] The link-state instruction is `POST /?_t=<token>` with `COMMAND=lan+link+speed`.
- [confirmed] The static UI maps link codes 0 through 6 to disconnected; 10/100/1000 Mbps half/full duplex respectively.
- [confirmed] The static UI divides each `DIDMNG.GENERAL.{RX,TX}_BPS` value by 32 and truncates to render Mbps.
- [confirmed] Hidden G.hn quality/status GETs, schemas, live measurements, and safety limits are owned by `findings-ghn-telemetry.md`.

## Runtime topology and link snapshot

### `.184` reporting adapter

- [confirmed] `NUM_DIDS=2`.
- [confirmed] MAC array: `00:00:00:00:00:00,8c:90:2d:10:49:e2,3c:64:cf:59:d4:88`.
- [confirmed] RX array: `0,0,14615`; TX array: `0,0,12421`.
- [confirmed] The UI filters the zero MAC and its own MAC, leaving `.185` as the one displayed remote peer.
- [confirmed] By the static display conversion, the `.185` peer row renders RX 456 Mbps and TX 388 Mbps.
- [confirmed] `COMMAND=lan+link+speed` returned `PORT1=6`, `PORT2=0`.
- [confirmed] By the static link-code mapping, LAN 1 is 1000 Mbps full duplex and LAN 2 is disconnected.

### `.185` reporting adapter

- [confirmed] `NUM_DIDS=2`.
- [confirmed] MAC array: `00:00:00:00:00:00,8c:90:2d:10:49:e2,3c:64:cf:59:d4:88`.
- [confirmed] RX array: `0,12421,0`; TX array: `0,14615,0`.
- [confirmed] The UI filters the zero MAC and its own MAC, leaving `.184` as the one displayed remote peer.
- [confirmed] By the static display conversion, the `.184` peer row renders RX 388 Mbps and TX 456 Mbps.
- [confirmed] `COMMAND=lan+link+speed` returned `PORT1=0`, `PORT2=6`.
- [confirmed] By the static link-code mapping, LAN 1 is disconnected and LAN 2 is 1000 Mbps full duplex.

## Hidden quality snapshot

- [confirmed] Directional attenuation/length: `.184 = 43.0 dB / 60 m`; `.185 = 39.7 dB / 59 m`.
- [confirmed] Estimated application throughput: `.184 = 365 Mbps`; `.185 = 310` then `301 Mbps`.
- [confirmed] Approximately 90-second deltas: `.184` receive BLER `2.7221%`, retransmission `0.0589%`; `.185` receive BLER `0.0622%`, retransmission `1.9672%`.
- [confirmed] No packet-, LLC-, or Ethernet-layer error increased; no new discard, channel-adaptation event, or Domain Master loss occurred.
- [confirmed] `FLOWMONITOR.STATS.LINK_STATUS` returned `ERROR=009`; its schema descriptor remained readable.

## State-changing protocol paths intentionally uncalled

- [confirmed] The UI binds peer deletion to `COMMAND=plc remove <MAC>`; it was not called.
- [confirmed] The soft-pair UI binds leaving a network to `COMMAND=plc leave network`; it was not called.
- [confirmed] The powerline reset UI binds to `COMMAND=reset powerline`; it was not called.
- `BLOCKED`: discovery/broadcast, G.hn control-plane, pairing, and reset protocols need artifact or isolated runtime evidence before further probing.

## Action status

- `NOW`: authenticated API exposes bounded identity, peers, rendered rates, Ethernet status, and the proven hidden telemetry set read-only.
- `RUNTIME-NEEDED`: protocol packet framing and non-HTTP discovery remain unobserved.
- `BLOCKED`: no pairing, removal, reset, or unbounded network probe is authorized.

## Provenance

Raw scan/captures are ignored; compact web and telemetry evidence is in `data/extracted-live/extracted-knowledge/{live-web-evidence,live-telemetry-evidence}.txt`.

## Official companion transport evidence

- [confirmed] The current official Windows archive is `tpPLC-2.3.5940.20-windows-PowerLineUtility.zip`.
  Its SHA-256 is `c3375a2842ca6981eb1fddae2257b06680cb914372df679ccd1517f956de69ef`.
  The official PG2400P KIT V1 page owns its provenance.
- [confirmed] The Windows Electron UI routes commands through `plcu.exe` to `plcoperation.dll`.
  `plcoperation.dll` directly imports `WPCAP.DLL` and `PACKET.DLL`.
- [confirmed] `plcoperation.dll` contains `GHN_DEVICE`, `G.hn_%02x%02x`, and a capture-filter format.
- [confirmed] `plcu.exe` contains `G.hn1200`, `G.hn2400`, and `Couldn't load Npcap`.
  The utility bundles no `.sys`, `.inf`, or `.cat` capture-driver file.
- [likely] Windows uses Npcap through the WinPcap-compatible DLL APIs.
  An isolated Windows trace must establish driver selection and current dispatch.

### G.hn L2 discovery framing

- [confirmed] The official macOS backend imports libpcap and contains G.hn constructor and scanner paths.
  A separate function owns raw-Ethernet transmission through `pcap_sendpacket`.
- [confirmed] `make_GHN_DISCOVERY_Packet` writes EtherType `0x2e00`.
  Original `plcu` bytes are `66 c7 45 a6 2e 00` at file offset `0x62da8`.
- [confirmed] `initDiscoveryDestAv` writes broadcast and `00:b0:52:00:00:01` discovery destinations.
  The generic pcap sender can insert an `0x8100` VLAN tag.
- [confirmed] `ghnScanMXLLocalDev` obtains an interface and invokes `_MACDiscoverGet`.
  `_MACDiscoverGet` enumerates interfaces and waits for worker results.
- [confirmed] `ghnMXLGetIP` queries `TCPIP.IPV4.IP_ADDRESS`, then `TCPIP.IPV4.ADDITIONAL_IP_ADDRESS`.
- [likely] The recovered pcap sender carries the constructed G.hn discovery frame; a direct constructor-to-send callsite was not recovered.
- `RUNTIME-NEEDED`: capture payloads, opcodes, parsing, filters, retries, and current Windows equivalence.

### Management boundary

- [confirmed] The current UI recognizes `PG2400P 1.0` and can open its support page or discovered IP.
- [confirmed] HyFi libraries contain three HTTP management routes.
  No recovered model branch connects those routes to PG2400P.
- [likely] PG2400P G.hn control is the raw/config-layer path rather than the recovered HyFi HTTP path.
- `BLOCKED`: do not infer or probe a PG2400P HTTP control route from the companion utility.
