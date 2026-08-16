# G.hn telemetry

## Scope and evidence model

This file owns hidden PG2400P link-quality telemetry: external semantics, firmware correlation, live support, measurements, and safety.

- `[confirmed-live]`: both owned PG2400P V1 devices, firmware `1.0.3 Build 20221213 Rel.62540`.
- `[confirmed-artifact]`: shipped TP-Link firmware content, independent of live behavior.
- `[corroborated]`: standard, MaxLinear material, public SCT implementation, or related G.hn product; not PG2400P runtime proof.
- Exact live evidence: `data/extracted-live/extracted-knowledge/live-telemetry-evidence.txt`.

## Conclusion

- [confirmed-live] Both devices expose 20 hidden read-only ConfigLayer telemetry fields through authenticated `GET /?_t=<token>&KEY=`.
- [confirmed-live] Returned data covers attenuation, wire length, estimated application throughput, G.9962 blocks/retries/errors, QoS drops, LLC integrity, channel-adaptation events, Ethernet counters/errors, and Domain Master losses.
- [confirmed-live] One requested value failed identically: `FLOWMONITOR.STATS.LINK_STATUS` returned `ERROR=009`; its descriptor remained readable.
- [confirmed-live] No direct per-subcarrier SNR array was read. `QOS.STATS.CHANNEL_INFO` exposes cumulative SNR-change/adaptation events, not SNR magnitude.
- [confirmed-live] The observed link was operational and upper-layer clean, but directionally asymmetric: `.184` received more bad blocks; `.185` retransmitted more blocks.

## Evidence chain

### Shipped TP-Link firmware

- [confirmed-artifact] Both firmware releases ship byte-identical `raw/ffs/logfile/logfile.cfg` files requesting `DIDMNG.GENERAL.{DIDS,MACS,TX_BPS,RX_BPS}`, `ETHIFDRIVER.STATS.{INFO_DESC,INFO}`, `QOS.STATS.{DESC,INFO}`, `FLOWMONITOR.INFO.XPUT_INDICATOR`, and `MASTERSELECTION.STATS.{DESC,INFO}`.
- [confirmed-artifact] The 1.0.3 raw payload contains `QOS.STATS.G9962` at raw offset `0x2d4238` and `FLOWMONITOR.GENERAL.DID_ESTIMATE` at `0x2d8170`; nearby tables contain `CHANNEL_INFO`, `RX_LLC_ERRORS`, `XPUT_INDICATOR`, `AVG_ATTENUATION`, and `WIRE_LENGTH` suffixes.
- [confirmed-artifact] Raw code/data names include FlowMonitor BLER/SNR evolution, SNR conversion/filtering, FEC, channel adaptation, and detailed Ethernet error statistics.
- [confirmed-artifact] The UI divides `DIDMNG.GENERAL.{RX,TX}_BPS` by `32`; external schema defines BPS as Bits Per Symbol, resolving the misleading name without changing the observed UI conversion.

### Standards and vendor semantics

- [corroborated] Current Broadband Forum TR-181 defines G.hn PHY throughput and performance monitoring, including `BlocksResent`, `BlocksErrorsReceived`, and grouped SNR in `0.1 dB`: https://github.com/BroadbandForum/cwmp-data-models/blob/306acd3dcf783fd26d3d9281afe73986f4325933/tr-181-2-21-0-ghn.xml
- [corroborated] BBF TR-476 expects `TxPhyRate`, `RxPhyRate`, `BlocksErrorReceived`, and `BlocksReceived`; it permits TR-069/USP/TR-181 or HomeGrid LCMP/HGF-DM access and names `FLOWMONITOR.INFO.XPUT_INDICATOR`: https://www.broadband-forum.org/pdfs/tr-476-1-0-0.pdf
- [corroborated] MaxLinear's DMI920 guide documents Spirit SCT and `FLOWMONITOR.GENERAL.DID_ESTIMATE=<remote DID>` as a forced channel/bit-rate re-estimation: https://www.maxlinear.com/document?id=23298
- [corroborated] A public SCT parameter catalog with MaxLinear notice supplies exact names, types, units, resets, and column schemas: https://github.com/SanyamGarg12/Velmenni-Frontend-LC-LYNC/blob/39584ee93c573270cdd3b364d4e3eae2891501d4/backend/parameter_description.html
- [corroborated] Its companion Java implementation parses `LINK_STATUS`, FEC/error percentages, XPUT, and Rx/Tx BPS: https://github.com/SanyamGarg12/Velmenni-Frontend-LC-LYNC/blob/39584ee93c573270cdd3b364d4e3eae2891501d4/SctDevice.java
- [corroborated] Positron GAM exposes endpoint statistics, estimated wire length, and directional maximum SNR on another commercial G.hn stack: https://www.positronaccess.com/archive-upload/GAM_CLI_Guide-v1_2_0-180-0187-001-R01.pdf
- [corroborated] TP-Link's public utility/device guides expose rate/configuration but no SNR/error UI: https://static.tp-link.com/1910012154_tpPLC%20Utility_UG.pdf and https://static.tp-link.com/upload/manual/2022/202207/20220711/1910013220_PG2400P%20KIT%28EU%29%E5%A4%9A%E6%9C%BA%E5%9E%8B_UG_REV1.0.0.pdf

Exact proprietary symbols such as `ghnMXLGetNwInfoFromMXL`, `ghnMXLGetEthSts`, `ghnScanMXLLocalDev`, `make_GHN_DISCOVERY_Packet`, and `configlayerGetParam` had no public exact match. Public evidence therefore establishes chipset-family semantics, not source identity or TP-Link handler ownership.

## Live field support

All successful values returned `HTTP 200`, `ERROR=000` on both devices.

| Group | Confirmed live keys | Semantics |
| --- | --- | --- |
| Topology/line | `DIDMNG.GENERAL.DIDS`, `.ACTIVE`, `.AVG_ATTENUATION`, `.WIRE_LENGTH` | DIDs, active flags, `0.1 dB`, meters |
| Flow | `FLOWMONITOR.INFO.XPUT_INDICATOR` | global estimated application throughput, Mbps |
| Flow schema | `FLOWMONITOR.STATS.LINK_STATUS_DESC` | `TIMER,MSECS,SID,FRAMES,LPDUS,ERROR%,ABORT%` |
| QoS summary | `QOS.STATS.INFO`, `.DESC` | cumulative discarded/transmitted packets and discarding DIDs |
| G.9962 | `QOS.STATS.G9962`, `.G9962_DESC` | 23 traffic, discard, management, block, retry, and error counters |
| LLC | `QOS.STATS.RX_LLC_ERRORS`, `.RX_LLC_ERRORS_DESC` | bad LLC CRC and cipher MIC counters |
| Adaptation | `QOS.STATS.CHANNEL_INFO`, `.CHANNEL_INFO_DESC` | BLER/SNR triggers and adaptation outcomes |
| Ethernet | `ETHIFDRIVER.STATS.INFO`, `.INFO_DESC`, `.ERRORS`, `.ERRORS_DESC` | traffic, queue-full, aggregate and detailed errors |
| Master | `MASTERSELECTION.STATS.INFO`, `.DESC` | cumulative Domain Master losses |

Rejected on both devices:

```text
FLOWMONITOR.STATS.LINK_STATUS
ERROR=009
```

Its readable descriptor plus failing value suggests disabled/uninitialized runtime collection or a required monitor state. No state was enabled to test that hypothesis.

## G.9962 schema and calculations

Live `QOS.STATS.G9962_DESC` order:

```text
Bytes_TX, Bytes_RX, PKTS_TX, PKTS_RX, Errors_TX, Errors_RX,
UCAST_PKTS_TX, UCAST_PKTS_RX, DISCARD_PKTS_TX, DISCARD_PKTS_RX,
MCAST_TX, MCAST_RX, BCAST_TX, BCAST_RX, UNKNOWN_PROTO_PKTS_RX,
MGMT_BYTES_TX, MGMT_BYTES_RX, MGMT_PKTS_TX, MGMT_PKTS_RX,
BLOCKS_TX, BLOCKS_RX, BLOCKS_RTX, BLOCKS_ERROR_RX
```

Use deltas; lifetime ratios obscure bursts and different uptime:

```text
retransmission_rate = ΔBLOCKS_RTX / ΔBLOCKS_TX
receive_BLER         = ΔBLOCKS_ERROR_RX / ΔBLOCKS_RX
attenuation_dB       = AVG_ATTENUATION / 10
UI_rate_Mbps         = BPS // 32
```

`AVG_ATTENUATION=2000` means not calculated; the external schema requires at least `10 Mbps` traffic. `WIRE_LENGTH=0` means not calculated and depends on the medium propagation factor.

## Live snapshot

Two samples were separated by device-reported QoS intervals of `89.96 s` (`.184`) and `89.24 s` (`.185`). Traffic was incidental and light; results describe that window, not capacity under load.

| Metric | `10.0.1.184` | `10.0.1.185` |
| --- | ---: | ---: |
| Remote DID position | 2 | 1 |
| Active | yes | yes |
| Attenuation | `43.0 dB` | `39.7 dB` |
| Estimated wire length | `60 m` | `59 m` |
| Rx BPS / UI rate | `14615` / `456 Mbps` | `12421` / `388 Mbps` |
| Tx BPS / UI rate | `12421` / `388 Mbps` | `14615` / `456 Mbps` |
| XPUT indicator | `365 Mbps` | `310` then `301 Mbps` |
| Δ blocks Tx / Rx | `1697 / 698` | `610 / 1607` |
| Δ blocks retransmitted | `1` | `12` |
| Δ bad blocks received | `19` | `1` |
| Retransmission rate | `0.0589%` | `1.9672%` |
| Receive BLER | `2.7221%` | `0.0622%` |
| Δ packet errors Tx/Rx | `0 / 0` | `0 / 0` |
| Δ packet discards Tx/Rx | `0 / 0` | `0 / 0` |
| LLC CRC / cipher-MIC errors | `0 / 0` | `0 / 0` |
| Δ detailed Ethernet errors | `0` | `0` |
| Δ channel-adaptation counters | `0` | `0` |
| Domain Master losses, cumulative / Δ | `1 / 0` | `0 / 0` |

Directional correlation supports the counter interpretation: `.184` received `19` bad blocks while `.185` retransmitted `12`; `.185` received `1` bad block while `.184` retransmitted `1`. Samples were sequential, so exact equality is not expected.

No packet-, LLC-, or Ethernet-layer error increased. G.hn recovery contained the observed block corruption during this window, although retries/errors can still reduce throughput or increase latency. `.184` had `183` historical QoS discards but no new discard; `.185` remained at zero.

Historical `CHANNEL_INFO` values were `.184 = 6,21,0,14,44,36,0,0,0,0` and `.185 = 2,22,0,6,32,21,0,0,0,0`; the descriptor names only six columns. Treat the trailing layout and absolute counts as unresolved. Both arrays were unchanged during observation; the named `SNR decr` position was zero.

## CLI ownership

- [confirmed] `pg2400p telemetry --host <host> --json` returns one decoded snapshot and all 20 exact raw values.
- [confirmed] `--interval <seconds>` takes two snapshots in one authenticated session and uses measured elapsed time.
- [confirmed] Interval output includes all counter deltas, TX/RX bit rates, retransmission rate, and receive BLER.
- [confirmed] Descriptor/value width drift and decreasing counters fail explicitly instead of producing false rates.
- [confirmed] Variable trailing `CHANNEL_INFO` values remain available as `UNMAPPED_<index>` and in `raw_fields`.
- [confirmed-live] Snapshot and one-second interval collection completed on `.184` without changing device state.
- [runtime] `.184` currently reports no remote peer, zero XPUT, and uncalculated attenuation and wire length.

```bash
uv run --locked pg2400p telemetry \
  --host <device-ip> \
  --interval 5 \
  --json
```

## Safety and state verification

- [confirmed-live] Probe boundary: authenticated field GETs plus normal login/logout only; no setter, reset, re-estimation, diagnostic enable, or configuration command.
- [confirmed-live] Identity, firmware, local MAC, domain, PHY mode, peer count/MACs, and Rx/Tx BPS matched before, immediately after, and after the second sample.
- [confirmed-live] Both roots remained `HTTP 200`, `12321` bytes, SHA-256 `2048bb33776afb3c8e2fdd3dbaad1c162b43d1739b37b0234dccc870d6bcd4bf`.
- `BLOCKED`: `FLOWMONITOR.GENERAL.DID_ESTIMATE`, `*.RESET`, diagnostics enables, AFE/gain, SNR collection controls, and other writable ConfigLayer keys on live devices.
- `NOW`: collect passive CLI interval snapshots when the remote peer returns.
- `RUNTIME-NEEDED`: controlled traffic windows to characterize directionality, BLER, retries, XPUT, attenuation stability, and adaptation events.
