# Web interface and API

## Scope and evidence

- [confirmed] `10.0.1.184` and `10.0.1.185` answer plain HTTP/1.1 on port 80 with `200 OK`, `Content-Type: text/html`, and a 12,321-byte root document.
- [confirmed] The root response headers and body are byte-identical across both devices; SHA-256 values are in `data/extracted-live/extracted-knowledge/live-web-evidence.txt`.
- [confirmed] The root document declares the TP-Link SPA loader, jQuery 1.10.0, `js/app/url.js`, `js/su/{language,su.fun,widget.form,widget.other,frame}.js`, language assets, and default CSS.
- [confirmed] The root-declared static assets recover `config/{classes,models,modules}.json` and the module controllers/models used below.
- [confirmed] `config/modules.json` registers `networkMap`, `powerLineSetting`, `softPair`, `powerSavingMode`, `compatibilityMode`, `lanAdv`, `QoS`, `timeSettings`, `reboot`, `led`, `firmware`, `restore`, and `changeLoginPassword`; these are module identifiers, not a claim that each is a direct hash route.
- [confirmed] The live browser reaches `#networkMap`; its visible navigation labels are Status, Device Settings, and System.

## Transport and grammar

- [confirmed] The primary API path is `/`.
- [confirmed] Read models issue `GET /?KEY1=&KEY2=`.
- [confirmed] The authenticated client appends `_t=<URL-encoded token>` to that query.
- [confirmed] Instruction calls issue `POST /?_t=<token>` with `application/x-www-form-urlencoded` bodies such as `COMMAND=is+factorydefault` and `COMMAND=lan+link+speed`.
- [confirmed] The parser treats the first `ERROR=<numeric code>` line as status and remaining CRLF-separated `KEY=VALUE` lines as response fields.
- [confirmed] `ERROR=000` is the successful application response code.
- [confirmed] `ERROR=004` was returned by a direct unauthenticated `.185` identity-key query; static client constants name code 4 `ETOKEN`.

## Safely called live routes

| Request | Evidence | Result |
| --- | --- | --- |
| `GET /` | both devices | `200`, identical SPA root |
| `GET /?TPLINK.GENERAL.LANGUAGE=&SYSTEM.PRODUCTION.HW_PRODUCT=&SYSTEM.PRODUCTION.HW_REVISION=&SYSTEM.GENERAL.FW_VERSION=` | `.184` pre-auth; both after browser auth | model and firmware identity in storage findings |
| `POST /` body `COMMAND=is+factorydefault` | both devices, pre-auth | `ERROR=000`, `RESULT=0` |
| tokenized GET identity, local powerline, LAN, and `DIDMNG.GENERAL.*` model keys | both devices | `200`, `ERROR=000`; values in network/storage findings |
| tokenized `POST /` body `COMMAND=lan+link+speed` | both devices | `200`, `ERROR=000`; values in network findings |
| tokenized `POST /` body `COMMAND=logout` | `.185` browser session | `200`, `ERROR=000`; local and session storage cleared |

## Live identity

- [confirmed] Both devices report `PG2400P`, hardware revision `1.0`, firmware `1.0.3 Build 20221213 Rel.62540`, and locale `en_US` through the authenticated model route.
- [confirmed] `.184` returned the same hardware and firmware fields before authentication.
- [confirmed] No `Server`, authentication challenge, cookie, or TLS identity was present in the root capture; HTTPS port 443 was closed in the bounded TCP inventory.

## Uncalled mutation-risk routes

- [confirmed] The static firmware proxy targets `?COMMAND=firmware upgrade` for upload; uncalled.
- [confirmed] The network-map delete handler constructs `COMMAND=plc remove <MAC>`; uncalled.
- [confirmed] The soft-pair handler constructs `COMMAND=plc leave network`; uncalled.
- [confirmed] The powerline reset handler constructs `COMMAND=reset powerline`; uncalled.
- [confirmed] The reboot model writes `SYSTEM.GENERAL.HW_RESET`; uncalled.
- [confirmed] The password model constructs `COMMAND=change password`; uncalled.
- [confirmed] Static controllers submit LAN, domain/name, QoS, LED, power-saving, compatibility, time, DST, and reboot-schedule model values; uncalled.
- [confirmed] Static compatibility and QoS controllers construct `set compatibility mode <value>` and `set qos <value>`; uncalled.

## Action status

- `NOW`: use the proven root/form response grammar and tokenized model-key requests for the read-only client.
- `RUNTIME-NEEDED`: capture a versioned firmware/filesystem image to bind the HTTP handler implementation and all write semantics.
- `BLOCKED`: no mutation route is eligible for live use.

## Provenance

Raw captures are ignored under `data/captures/`.
Compact hashes, tools, parent browser-trace hash, and direct-curl discrepancies are in `data/extracted-live/extracted-knowledge/live-web-evidence.txt`.

## Firmware-static evidence

- [confirmed] Official PG2400P EU V1 `1.1.0 Build 20250710 Rel.56841` contains a decoded FFS web tree whose inventory is bound to the immutable ZIP SHA-256 `3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13`: `data/extracted-1.1.0-build-20250710-v1/extracted-knowledge/{asset-metadata,web-asset-inventory,protocol-map}.txt`.
- [confirmed] The client proxy source independently implements relative-root model reads with `GET` (`raw/ffs-dec/web/js/su/frame.js` byte 42905), writes with `POST` (byte 52231), `_t` session-key assembly (`js/app/url.js` byte 579), and `ERROR=<decimal>` plus CRLF `KEY=VALUE` response parsing (`frame.js` byte 48352).
- [confirmed] Firmware source maps identity fields at `web/modules/main/models.js` byte 141: `SYSTEM.PRODUCTION.HW_PRODUCT`, `SYSTEM.PRODUCTION.HW_REVISION`, and `SYSTEM.GENERAL.FW_VERSION`. It maps peer count/MAC/rates at `web/modules/networkMap/mapInternet/models.js` bytes 102–685: `DIDMNG.GENERAL.NUM_DIDS`, `.MACS`, `.RX_BPS`, `.TX_BPS`; the UI divides rate values by 32 at byte 648 for displayed Mbps.
- [confirmed] Firmware login source applies `md5()` before writing `TPLINK.GENERAL.LOGIN_PASSWORD` (`web/modules/login/localLogin/controllers.js` byte 826; `models.js` byte 276). This is source-local client behavior, not an inference about server password storage.
- [confirmed] The 1.1.0 static UI's firmware route checks `.ftp`, calls Ajax upload, and declares `COMMAND=firmware upgrade` (`web/modules/advanced/system/firmware/{models,controllers}.js` bytes 279 and 1325). This corroborates the live mutation ledger; it was not exercised here.
- [likely] The 1.1.0 static client and observed 1.0.3 live handler share the described contract, but only live evidence proves the installed devices' behavior. Static-to-live equivalence beyond these matching artifacts requires versioned handler evidence.
