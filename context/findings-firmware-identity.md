# Firmware Identity

Sources: official TP-Link support page `https://www.tp-link.com/uk/support/download/pg2400p-kit/`.
Version-scoped evidence: `data/extracted-*-v1/extracted-knowledge/`.

Action status: `NOW`; both live devices are bound to the acquired 1.0.3 release.

## Evidence

- [confirmed] TP-Link lists EU V1 firmware `1.1.0 Build 20250710` and `1.0.3 Build 20221213`.
  Acquisition used a browser User-Agent, HTTPS-only curl, TLS verification, and direct HTTP/2 responses.
  Each release's `asset-metadata.txt` and `acquisition-headers.txt` preserve full provenance.
- [confirmed] `1.1.0 Build 20250710 Rel.56841` ZIP size is 2,863,018 bytes.
  ZIP SHA-256: `3c2db75e1ca16da388bb614a6e7184fe4a863e6bf07bda668573b806b0174d13`.
  Its `.ftp` payload is 2,731,684 bytes with SHA-256 `1bca420934f2073649ae9b0046c1f10c9a19d2b61b331bcedf3b1845c752039a`.
  The raw payload confirms the release string at byte `2693936`.
- [confirmed] `1.0.3 Build 20221213 Rel.62540` ZIP size is 2,970,972 bytes.
  ZIP SHA-256: `1175f14f34b2f85c1dfe2a8bac558d711be27b1177fa0844bda566a3f8f37643`.
  Its `.ftp` payload is 2,701,736 bytes with SHA-256 `ac22c971a0d5bcc0f88adec20a9010db8e5e5f1beb13f8c291e8e8f0c5155819`.
  The raw payload confirms the release string at byte `2688944`.
- [confirmed] Both outer ZIPs are unencrypted deflate containers without detached signatures.
  This does not establish the device-side update-verification policy.
- [confirmed] Version 1.1.0 has 142 decoded web files; version 1.0.3 has 124.
  Of their common paths, 96 differ and 23 are byte-identical.
  Version 1.1.0 adds accessibility assets and three TR-064 or contrast client mappings.
  File-level evidence is in `normalized-web-comparison.txt`.

## Interpretation

- [confirmed] Both owned devices report hardware `1.0` and firmware `1.0.3 Build 20221213 Rel.62540`.
  The live identity matches the immutable official EU V1 1.0.3 artifact.
- [unresolved] TP-Link's release note says 1.1.0 enhances security; static inventory alone does not identify the changed security behavior.

## Next Proof

Establish the raw-image load map and updater xrefs needed to explain the security changes in version 1.1.0.