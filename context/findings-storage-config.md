# Storage and configuration

## Confirmed live configuration snapshots

### `10.0.1.184`

- [confirmed] Powerline MAC: `8c:90:2d:10:49:e2`.
- [confirmed] Device name: `Device_49E2`.
- [confirmed] Powerline domain/network name: `HomeGrid`.
- [confirmed] IPv4 DHCP: enabled; address `10.0.1.184`; netmask `255.255.255.0`; gateway `10.0.1.1`.
- [confirmed] IPv6 DHCP: disabled; link-local `fe80:0000:0000:0000:8e90:2dff:fe10:49e2`; SLAAC value all zeroes.

### `10.0.1.185`

- [confirmed] Powerline MAC: `3c:64:cf:59:d4:88`.
- [confirmed] Device name: `Device_D488`.
- [confirmed] Powerline domain/network name: `HomeGrid`.
- [confirmed] IPv4 DHCP: enabled; address `10.0.1.185`; netmask `255.255.255.0`; gateway `10.0.1.1`.
- [confirmed] IPv6 DHCP: disabled; link-local `fe80:0000:0000:0000:3e64:cfff:fe59:d488`; SLAAC value all zeroes.

## Read-only configuration schema

- [confirmed] Local identity/name/domain fields are `SYSTEM.PRODUCTION.MAC_ADDR`, `NODE.GENERAL.DEVICE_NAME`, and `NODE.GENERAL.DOMAIN_NAME`.
- [confirmed] LAN status fields are `DHCP.GENERAL.ENABLED_IPV4`, `TCPIP.IPV4.IP_ADDRESS`, `TCPIP.IPV4.IP_NETMASK`, `DHCP.GENERAL.ENABLED_IPV6`, `TCPIP.IPV4.GATEWAY`, `TCPIP.IPV6.LINK_LOCAL_IP_ADDRESS`, and `TCPIP.IPV6.SLAAC_IP_ADDRESS`.
- [confirmed] An unauthenticated `.184` identity query reported product `PG2400P`, hardware `1.0`, and firmware `1.0.3 Build 20221213 Rel.62540`.
- [confirmed] Both devices return `RESULT=0` for the read-only `COMMAND=is+factorydefault` check.
- [likely] `RESULT=0` means the adapters are not in their factory-default state because the static client uses this result to select local-login rather than recovery; server-side meaning needs handler evidence.

## Configuration write boundary

- [confirmed] Static controllers submit changes to the powerline device/domain model, LAN IPv4/IPv6 and DNS mappings, QoS, LED, power-saving, compatibility, time/NTP/DST, scheduled reboot, password, firmware, and reset models.
- [confirmed] The named direct mutation operations recovered from the static client are `COMMAND=change password`, `COMMAND=set compatibility mode <value>`, `COMMAND=set qos <value>`, `COMMAND=firmware upgrade`, `COMMAND=reset powerline`, and writes to `SYSTEM.GENERAL.HW_RESET`.
- [confirmed] The time-settings controller invokes `checkPowerProxy.check` and, after a power prompt, `checkPowerProxy.powerdown`; their HTTP construction and state effects are unresolved, so neither was called.
- [confirmed] None of those fields or commands was called during this live lane.

## Storage ownership limits

- [confirmed] The browser client stores the session token and MD5 login digest in browser `localStorage` only.
- `RUNTIME-NEEDED`: persistent device configuration file, NVRAM, flash partition, serialization, validation, and rollback ownership are not evidenced by web responses.
- `BLOCKED`: no storage write, config export endpoint, password modification, factory reset, or firmware upload may be inferred safe from this read-only snapshot.

## Action status

- `NOW`: expose the captured model keys as read-only configuration fields.
- `RUNTIME-NEEDED`: obtain a versioned filesystem or controlled runtime trace to identify persistence and configuration transactions.
- `BLOCKED`: device configuration writes remain out of scope.

## Provenance

Authenticated `.184` response bodies are in parent browser trace `artifact://155`; authenticated `.185` values came from the isolated browser session's tokenized model-key requests.
Hashes and local raw-capture provenance are in `data/extracted-live/extracted-knowledge/live-web-evidence.txt`.
