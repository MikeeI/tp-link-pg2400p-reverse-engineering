# Firmware Identity

Sources: official TP-Link support page `https://www.tp-link.com/uk/support/download/pg2400p-kit/`; immutable assets and version-scoped evidence under `data/extracted-*-v1/extracted-knowledge/`.

Action status: `NOW` for static evidence; `RUNTIME-NEEDED` to identify the installed release on either live device.

## Evidence

- [confirmed] TP-Link's PG2400P KIT V1 UK support page linked EU V1 firmware `1.1.0 Build 20250710` (published 2025-08-27) and `1.0.3 Build 20221213` (published 2023-02-02). Acquisition used a Chrome browser User-Agent, HTTPS-only curl with TLS verification, and received direct HTTP/2 200 responses—no redirects. Full source URL, HTTP headers, time, size, and trust basis: each release's `asset-metadata.txt` and `acquisition-headers.txt`.
- [confirmed] `1.1.0 Build 20250710 Rel.56841`: `data/assets/PG2400P-EU-V1-1.1.0-build-20250710.zip`, 2,863,018 bytes, SHA-256 `3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13`. Its `.ftp` payload is 2,731,684 bytes, SHA-256 `1bca420934f2073649ae9b0046c1f10c9a19d2b61b331bcedf3b1845c752039a`; decompressed raw payload release string at byte `2693936`: `1.1.0 Build 20250710 Rel.56841`.
- [confirmed] `1.0.3 Build 20221213 Rel.62540`: `data/assets/PG2400P-EU-V1-1.0.3-build-20221213.zip`, 2,970,972 bytes, SHA-256 `1175f14f34b2f85c1dfe2a8bac558d711be27b1177fa0844bda566a3f8f37643`. Its `.ftp` payload is 2,701,736 bytes, SHA-256 `ac22c971a0d5bcc0f88adec20a9010db8e5e5f1beb13f8c291e8e8f0c5155819`; decompressed raw payload release string at byte `2688944`: `1.0.3 Build 20221213 Rel.62540`.
- [confirmed] Both outer ZIPs are unencrypted deflate containers and did not include a detached signature. That limits only acquisition-signature evidence; it does not establish the device-side update-verification policy.
- [confirmed] Normalized FFS-web comparison: 1.1.0 has 142 decoded web files; 1.0.3 has 124. Of common paths, 96 contents differ and 23 are byte-identical. 1.1.0 adds accessibility assets and client mappings `TPLINK.GENERAL.INCREASE_CONTRAST`, `TR064.GENERAL.DETECTED`, and `TR064.GENERAL.ENABLE`. Scope and file-level evidence: `data/extracted-1.1.0-build-20250710-v1/extracted-knowledge/normalized-web-comparison.txt`.

## Interpretation

- [likely] The official release label establishes the firmware artifact as PG2400P KIT EU V1, but it does not prove either owned device's local hardware revision, region, or installed build.
- [unresolved] TP-Link's release note says 1.1.0 enhances security; static inventory alone does not identify the changed security behavior.

## Next Proof

Use only the firmware-derived identity GET fields (`SYSTEM.PRODUCTION.HW_PRODUCT`, `SYSTEM.PRODUCTION.HW_REVISION`, `SYSTEM.GENERAL.FW_VERSION`) in a bounded authenticated read, then bind the response to this artifact table. See version-specific `protocol-map.md`.