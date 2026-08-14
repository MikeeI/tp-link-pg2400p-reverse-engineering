# Static service map
Source: `data/extracted-1.0.3-build-20221213-v1/raw/firmware-payload` SHA-256 `00213d7d32a1d29c654b38570c798ae176ae24f6223e4e0794aa231d59df545d`. Offsets are raw payload bytes.

## Evidence
- [confirmed] Service/function-name strings: `WebserverStart` @2698864 (0x292e70); `WebserverInit` @2698880 (0x292e80); `FilesystemInit` @2703568 (0x2940d0); `FilesystemStart` @2703600 (0x2940f0); `webunzipper.c` @2830044 (0x2b2edc); `webserver.c` @2830536 (0x2b30c8).
- [confirmed] Configuration/status vocabulary is colocated: `SYSTEM.GENERAL.FW_VERSION` @2830156 (0x2b2f4c); `DIDMNG.GENERAL.NUM_DIDS` @2812384 (0x2ae9e0).
- [likely] A product-owned embedded web server and filesystem service are part of this raw payload. The names are static evidence, but no valid raw-image disassembly/xref proves activation or task boundaries.

## Unresolved
No kernel, init system, process list, ELF load map, or scheduler task table has been parsed. `WebserverStart` and `FilesystemStart` must be mapped to executable calls or observed in isolated runtime before calling them active processes.
Action status: RUNTIME-NEEDED.
