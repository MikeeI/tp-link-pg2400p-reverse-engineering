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

## State-changing protocol paths intentionally uncalled

- [confirmed] The UI binds peer deletion to `COMMAND=plc remove <MAC>`; it was not called.
- [confirmed] The soft-pair UI binds leaving a network to `COMMAND=plc leave network`; it was not called.
- [confirmed] The powerline reset UI binds to `COMMAND=reset powerline`; it was not called.
- `BLOCKED`: discovery/broadcast, G.hn control-plane, pairing, and reset protocols need artifact or isolated runtime evidence before further probing.

## Action status

- `NOW`: the client can expose bounded TCP/HTTP identity, peer enumeration, rendered link rates, and Ethernet status read-only.
- `RUNTIME-NEEDED`: protocol packet framing and non-HTTP discovery remain unobserved.
- `BLOCKED`: no pairing, removal, reset, or unbounded network probe is authorized.

## Provenance

`data/captures/live-tcp-1-1024-8080-8443.nmap` is ignored raw evidence; its SHA-256 and browser-read provenance are in `data/extracted-live/extracted-knowledge/live-web-evidence.txt`.
