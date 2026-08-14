# Architecture and Processes

Sources: `data/extracted-1.1.0-build-20250710-v1/extracted-knowledge/{container-inventory,binary-inventory,process-map}.txt`; matching 1.0.3 evidence under its version-scoped extraction.

Action status: `RUNTIME-NEEDED` for raw-image execution mapping and process activation; `BLOCKED` for a conventional ELF/process inventory.

## Evidence

- [confirmed] Both `.ftp` packages contain two independently decoded XZ streams: a raw firmware payload and an `FFS.tar.xz.upg` POSIX TAR. The 1.1.0 FFS TAR has 201 members (143 regular files, 58 directories); 1.0.3 has 181 (125 regular files, 56 directories). Preflight found no symlinks, devices, absolute paths, or traversal paths.
- [confirmed] The FFS TAR supplies `logfile/logfile.cfg` and compressed web assets. Every web asset decompressed with liblzma: 142 files in 1.1.0 and 124 in 1.0.3, zero parser failures. Deterministic file/hash inventories are `web-asset-inventory.tsv` per release.
- [confirmed] The raw 1.1.0 payload is 3,837,292 bytes, SHA-256 `79745b3a349b2d92ff0a6801f4f35fa2e8893725119334260ba7175c05f47716`; 1.0.3 is 3,828,620 bytes, SHA-256 `00213d7d32a1d29c654b38570c798ae176ae24f6223e4e0794aa231d59df545d`. Neither has a parseable ELF header or a recognized Linux filesystem. `file` mislabels both from leading bytes; Binwalk likewise found no ELF or standard filesystem in the raw payload.
- [confirmed] Independent artifact anchors name Xtensa: the container has `loader.5152_v3_uartdw.xtensa8` at `.ftp` offset 37960 in 1.1.0 / 36875 in 1.0.3; raw payload has `coreversion.standard.xtensa8` at 2705744 / 2700432. Radare2 6.2.0 includes an Xtensa 32-bit decoder, but no raw code was disassembled as fact because image base, entry point, endianness, and exact core are unresolved.
- [confirmed] The raw 1.1.0 payload includes static service-name/source anchors `WebserverStart` @2704176, `WebserverInit` @2704192, `FilesystemInit` @2708880, `FilesystemStart` @2708912, `webunzipper.c` @2838004, and `webserver.c` @2838572. Corresponding 1.0.3 anchors are in its `process-map.md`.

## Interpretation

- [likely] These artifacts target Tensilica Xtensa and use a firmware/RTOS-like service model rather than embedded Linux. The evidence is strong for the target family, but raw-image metadata is insufficient to declare ABI, CPU variant, tasking model, or OS.
- [likely] An embedded web server and filesystem service are product-owned parts of the raw firmware payload. The current anchors are strings/source-name evidence; no xref, activation path, or runtime task proves they execute.
- [unresolved] No kernel, init system, ELF process, scheduler task table, flash partition map, load base, or boot entry was recovered. Do not convert the static service names into a process list.

## Next Proof

Use an isolated raw-image load with independently established Xtensa variant/base/entry, then recover xrefs from web/update symbols. Prefer a disposable emulator or non-live hardware trace; do not execute the firmware on the workstation or owned live adapters.