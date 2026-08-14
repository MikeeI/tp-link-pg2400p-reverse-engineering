# Architecture and Processes

Sources: version-scoped `raw-image-map-evidence.txt`, `container-inventory.txt`, `binary-inventory.txt`, and `process-map.md`.

Action status: `NOW` for the static raw-image map and `RUNTIME-NEEDED` for execution mapping and process activation.

`BLOCKED` remains the status for a conventional ELF/process inventory.

## Evidence

- [confirmed] Both `.ftp` packages contain two independently decoded XZ streams: a raw firmware payload and an `FFS.tar.xz.upg` POSIX TAR. The 1.1.0 FFS TAR has 201 members (143 regular files, 58 directories); 1.0.3 has 181 (125 regular files, 56 directories). Preflight found no symlinks, devices, absolute paths, or traversal paths.
- [confirmed] The FFS TAR supplies `logfile/logfile.cfg` and compressed web assets. Every web asset decompressed with liblzma: 142 files in 1.1.0 and 124 in 1.0.3, zero parser failures. Deterministic file/hash inventories are `web-asset-inventory.tsv` per release.
- [confirmed] The raw 1.1.0 payload is 3,837,292 bytes, SHA-256 `79745b3a349b2d92ff0a6801f4f35fa2e8893725119334260ba7175c05f47716`; 1.0.3 is 3,828,620 bytes, SHA-256 `00213d7d32a1d29c654b38570c798ae176ae24f6223e4e0794aa231d59df545d`. Neither has a parseable ELF header or a recognized Linux filesystem. `file` mislabels both from leading bytes; Binwalk likewise found no ELF or standard filesystem in the raw payload.
- [confirmed] Independent artifact anchors name Xtensa: the container has `loader.5152_v3_uartdw.xtensa8` at `.ftp` offset 37960 in 1.1.0 / 36875 in 1.0.3; raw payload has `coreversion.standard.xtensa8` at 2705744 / 2700432. Ghidra 12.1.2 Raw Binary imports with `Xtensa:LE:32:default`, compiler `default`, and base `0x63000000` decode pointer-table targets as valid functions; the same 1.1.0 seeds do not decode under `Xtensa:BE:32:default`.
- [confirmed] The raw 1.1.0 payload includes static service-name/source anchors `WebserverStart` @2704176, `WebserverInit` @2704192, `FilesystemInit` @2708880, `FilesystemStart` @2708912, `webunzipper.c` @2838004, and `webserver.c` @2838572. Corresponding 1.0.3 anchors are in its `process-map.md`.
- [confirmed] The working static map is `0x63000000 + raw offset`: 39,356 aligned in-range LE pointers in 1.1.0 and 39,186 in 1.0.3, corroborated by the raw `0xd4` table whose targets begin LE `entry` prologues. The 1.1.0 code edge at raw `0x2c2f` (`8126f5`) resolves by `l32r` to in-image literal `0x630000c8`.

## Interpretation

- [likely] These artifacts target a 32-bit little-endian Tensilica Xtensa family ISA and use a firmware/RTOS-like service model rather than embedded Linux. The exact `xtensa8` core option, ABI, tasking model, runtime load address, and OS remain unresolved.
- [likely] `0x63000000` is a usable static raw-image base, not a proven physical flash or runtime load address. The `0xd4` table is a candidate dispatch table, not a reset-vector claim.
- [likely] An embedded web server and filesystem service are product-owned parts of the raw firmware payload. The current anchors are strings/source-name evidence; no xref, activation path, or runtime task proves they execute.
- [unresolved] No kernel, init system, ELF process, scheduler task table, flash partition map, reset entry, or complete code/data segmentation was recovered. Do not convert static service names into a process list.

## Next Proof

Decode `descriptor.upg` fields after `firmware B:/fw` at raw `.ftp` offset `0x178`, validate them against the XZ component boundary, and use its loader-to-firmware handoff to establish reset ownership. Then recover web/update xrefs from only that validated transfer map without executing firmware on the workstation or owned live adapters.