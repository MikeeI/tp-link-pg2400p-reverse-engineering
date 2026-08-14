# Update and Signature Flow

Sources: `data/extracted-1.1.0-build-20250710-v1/extracted-knowledge/update-integrity-evidence.txt` and its 1.0.3 counterpart. All offsets below are raw artifact bytes and all code is unexecuted.

Action status: `BLOCKED` for a verified signature/call graph; `RUNTIME-NEEDED` only in a disposable, non-live target.

## Evidence

- [confirmed] Both update `.ftp` containers have a `descriptor.upg` marker at offset 160. Their descriptor manifests name `params_update`, `/web`, `/fw`, `loader`, `firmware`, `factory_settings.bin`, and `FFS.tar.xz.upg`; exact per-release component anchors and carved-stream hashes are in `container-inventory.txt`.
- [confirmed] The 1.1.0 container embeds boot-loader diagnostics: `= G.hn Generic Boot Loader` @39293, `ERROR Loader with encryption key but firmware not encrypted` @39861, `ERROR CHECKING CRC in firmware encrypted image` @40037, and `CHECKING CRC OK in firmware encrypted image` @40089. The 1.0.3 offsets are 38208, 38776, 38952, and 39004 respectively.
- [confirmed] The 1.1.0 raw payload contains update/integrity symbols and diagnostics: `FlUpgradeFLASHCRCValidation` @2710144; `FlUpgradeFileCRCValidation:` @2939668; `FLUPGRADE.GENERAL.START` @2817720; `FLUPGRADE.GENERAL.SECURE` @2840948; `Running: calculating CRC` @2827084; and `Failed: CRC check failed` @2939848. 1.0.3 has matching names at its version-specific offsets.
- [confirmed] Lifecycle strings `Upgrade thread started`, `Upgrade thread finished`, `upgrade success`, `upgrade failed`, and `httpupg` occur in the raw payload (1.1.0: 2838300, 2838324, 2840840, 2840860, 2840976). These are static update-code anchors, not an observed update.
- [confirmed] The decoded UI restricts the local file to `.ftp` then uploads using `COMMAND=firmware upgrade`: `data/extracted-1.1.0-build-20250710-v1/raw/ffs-dec/web/modules/advanced/system/firmware/models.js` byte 279; upload callsite `controllers.js` byte 1325. The UI begins a reboot timer after reported upload success. This endpoint is mutation-risking and was not called.
- [confirmed] The bundled 1.0.3 web update instructions require matching hardware and say the process is followed by reboot: `data/extracted-1.0.3-build-20221213-v1/raw/web-update-guide.txt` lines 20 and 35–43.

## Interpretation

- [confirmed] CRC validation and an encryption-state path are present in the boot/update material.
- [likely] `FLUPGRADE.GENERAL.SECURE` participates in a secure-upgrade policy. A static string does not prove branch semantics, defaults, or whether it enforces encryption, a signature, both, or neither.
- [unresolved] No parsed RSA/ECDSA/public-key/signature-verification callsite or signed-container metadata was recovered. This is not proof that signature verification is absent: the raw Xtensa image does not yet have a valid load map or xrefs.

## Next Proof

Recover the raw Xtensa entry/base and only then trace `httpupg` through `FlUpgradeFileCRCValidation`/`FlUpgradeFLASHCRCValidation`, capturing success/failure branches and the consumer of `FLUPGRADE.GENERAL.SECURE`. Never test this against a live adapter.