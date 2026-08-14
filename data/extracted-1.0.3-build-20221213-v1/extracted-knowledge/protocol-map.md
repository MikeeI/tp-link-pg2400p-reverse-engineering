# Static web protocol map
Source: decoded FFS web assets; each path/hash is in `web-asset-inventory.tsv`. Offsets are decoded-file bytes.

## Confirmed client request/response contract
- `js/su/frame.js`@43335: default model read assigns `GET` and `$.su.url("", data)`; client supplies requested configuration keys as form fields.
- `js/su/frame.js`@52740: writes use `POST`; do not use for this read-only lane.
- `js/app/url.js`@588: session key literal is `_t`; the builder appends it to the relative root URL when a session exists.
- `js/su/frame.js`@48780: response parser recognizes `ERROR=<decimal>` followed by CR/LF-separated `KEY=VALUE` records; it excludes the `ERROR` record from parsed data and splits each line at its first `=`.
- `modules/main/models.js`@141: identity fields are `SYSTEM.PRODUCTION.HW_PRODUCT`, `SYSTEM.PRODUCTION.HW_REVISION`, and `SYSTEM.GENERAL.FW_VERSION`.
- `modules/networkMap/mapInternet/models.js`@102: peer/status fields are `DIDMNG.GENERAL.NUM_DIDS`, `DIDMNG.GENERAL.MACS`, `DIDMNG.GENERAL.RX_BPS`, and `DIDMNG.GENERAL.TX_BPS`; @648 divides rates by 32 for displayed Mbps.
- `modules/networkMap/mapInternet/controllers.js`: the UI loads the peer-count and peer-store models, drops `00:00:00:00:00:00`, and excludes its own MAC; this is a read-only consumer callsite.

## Authentication clue
- [confirmed] `modules/login/localLogin/controllers.js`@843 applies `md5()` to the entered password before delegating login. `modules/login/localLogin/models.js`@276 writes the result as `TPLINK.GENERAL.LOGIN_PASSWORD` through `MERProxyNew`. This proves the client-side flow, not server-side password storage or an authenticated request transcript.

## Web UI/update route
- [confirmed] `modules/advanced/system/firmware/models.js`@279 declares `COMMAND=firmware upgrade`; its controller checks `.ftp` and calls Ajax upload @1400. This is mutation-risking and excluded from the CLI.
- [confirmed] Static UI route/module inventory is in `config/navigator.json`; browser assets are rooted under `web/`, while management data requests are relative root requests, not a discovered `/cgi-bin/...` route.

## Client-mapped configuration/status keys (not a GET safety allowlist)
Each entry is a decoded client field mapping. Only the identity and `DIDMNG.GENERAL.*` sets above have named static model-load callsites; other mappings may also be written by their model and require a specific read callsite or live evidence before use.
- `AFE.GENERAL.ID`: web/modules/powerLine/compatibilityMode/models.js@233
- `CLOCK.GENERAL.TIME_ZONE`: web/modules/advanced/system/timeSettings/models.js@102
- `DHCP.GENERAL.ENABLED_IPV4`: web/modules/advanced/network/lanAdv/script.js@4715, web/modules/networkMap/mapRepeater/models.js@1012
- `DHCP.GENERAL.ENABLED_IPV6`: web/modules/advanced/network/lanAdv/script.js@5111, web/modules/networkMap/mapRepeater/models.js@1268
- `DIDMNG.GENERAL.MACS`: web/modules/networkMap/mapInternet/models.js@258, web/modules/networkMap/mapInternet/models.js@457
- `DIDMNG.GENERAL.NUM_DIDS`: web/modules/networkMap/mapInternet/models.js@102
- `DIDMNG.GENERAL.RX_BPS`: web/modules/networkMap/mapInternet/models.js@300, web/modules/networkMap/mapInternet/models.js@598
- `DIDMNG.GENERAL.TX_BPS`: web/modules/networkMap/mapInternet/models.js@344, web/modules/networkMap/mapInternet/models.js@685
- `DNS.GENERAL.IPV4`: web/modules/advanced/network/lanAdv/script.js@5015
- `DNS.GENERAL.IPV6`: web/modules/advanced/network/lanAdv/script.js@5676
- `INTERFMITIGATION.XDSL.ENABLED`: web/modules/powerLine/compatibilityMode/models.js@103
- `MSPS.THROUGHPUT.ENABLE`: web/modules/powerLine/powerSavingMode/models.js@154
- `NODE.GENERAL.DEVICE_NAME`: web/modules/powerLine/powerLineSetting/models.js@252
- `NODE.GENERAL.DOMAIN_NAME`: web/modules/powerLine/powerLineSetting/models.js@549
- `NTP.GENERAL.HOST`: web/modules/advanced/system/timeSettings/models.js@198
- `NTP.GENERAL.HOST2`: web/modules/advanced/system/timeSettings/models.js@292
- `PHYMNG.GENERAL.RUNNING_PHYMODE_ID`: web/modules/powerLine/compatibilityMode/models.js@334
- `POWERSAVING.GENERAL.MODE`: web/modules/powerLine/powerSavingMode/models.js@97
- `SYSTEM.GENERAL.FW_VERSION`: web/modules/advanced/system/firmware/models.js@164, web/modules/main/models.js@258
- `SYSTEM.GENERAL.HW_RESET`: web/modules/advanced/system/reboot/models.js@2116
- `SYSTEM.PRODUCTION.HW_PRODUCT`: web/modules/main/models.js@141
- `SYSTEM.PRODUCTION.HW_REVISION`: web/modules/advanced/system/firmware/models.js@99, web/modules/main/models.js@199
- `SYSTEM.PRODUCTION.MAC_ADDR`: web/modules/powerLine/powerLineSetting/models.js@98
- `TCPIP.IPV4.GATEWAY`: web/modules/advanced/network/lanAdv/script.js@4913, web/modules/networkMap/mapRepeater/models.js@1325
- `TCPIP.IPV4.IP_ADDRESS`: web/modules/advanced/network/lanAdv/script.js@4763, web/modules/networkMap/mapRepeater/models.js@1162
- `TCPIP.IPV4.IP_NETMASK`: web/modules/advanced/network/lanAdv/script.js@4834, web/modules/networkMap/mapRepeater/models.js@1215
- `TCPIP.IPV6.GATEWAY`: web/modules/advanced/network/lanAdv/script.js@5619
- `TCPIP.IPV6.IP_ADDRESS`: web/modules/advanced/network/lanAdv/script.js@5499
- `TCPIP.IPV6.IP_PREFIX`: web/modules/advanced/network/lanAdv/script.js@5559
- `TCPIP.IPV6.LINK_LOCAL_IP_ADDRESS`: web/modules/networkMap/mapRepeater/models.js@1375
- `TCPIP.IPV6.SLAAC_IP_ADDRESS`: web/modules/networkMap/mapRepeater/models.js@1437
- `TPLINK.GENERAL.LANGUAGE`: web/models/commonModels.js@377, web/modules/main/models.js@87
- `TPLINK.LEDSCHEDULE.LED_ENABLE`: web/modules/advanced/system/led/models.js@102
- `TPLINK.TIME.HOUR24`: web/modules/advanced/system/timeSettings/models.js@356
- `TPLINK.TIME.SET_TYPE`: web/modules/advanced/system/timeSettings/models.js@150

## Literal `COMMAND` instruction strings
- `change password`: `web/modules/advanced/system/changeLoginPassword/models.js`@925
- `get time`: `web/modules/advanced/system/timeSettings/models.js`@1612
- `set time `: `web/modules/advanced/system/timeSettings/models.js`@1659
- `get time`: `web/modules/index/script.js`@7783
- `is factorydefault`: `web/modules/main/main.js`@490
- `logout`: `web/modules/main/main.js`@3222
- `plc remove `: `web/modules/networkMap/mapInternet/controllers.js`@2027
- `lan link speed`: `web/modules/networkMap/mapRepeater/controllers.js`@580
- `get compatibility mode`: `web/modules/powerLine/compatibilityMode/models.js`@865
- `set compatibility mode `: `web/modules/powerLine/compatibilityMode/models.js`@926
- `reset powerline`: `web/modules/powerLine/powerLineSetting/controllers.js`@525
- `plc leave network`: `web/modules/powerLine/softPair/controllers.js`@1307
- `get qos`: `web/modules/qos/models.js`@402
- `set qos `: `web/modules/qos/models.js`@448

[likely] A device with this UI generation accepts the relative-root client contract. Runtime/API evidence is still needed to bind it to a specific live firmware, response coverage, and authorization state.
Action status: NOW only for the named identity and peer-status reads; RUNTIME-NEEDED for server handler callsites and any other mapping.
