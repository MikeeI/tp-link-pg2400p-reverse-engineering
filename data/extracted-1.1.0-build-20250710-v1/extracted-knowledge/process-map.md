# Static service map
Source: `data/extracted-1.1.0-build-20250710-v1/raw/firmware-payload` SHA-256 `79745b3a349b2d92ff0a6801f4f35fa2e8893725119334260ba7175c05f47716`. Offsets are raw payload bytes.

## Evidence
- [confirmed] Service/function-name strings: `WebserverStart` @2704176 (0x294330); `WebserverInit` @2704192 (0x294340); `FilesystemInit` @2708880 (0x295590); `FilesystemStart` @2708912 (0x2955b0); `webunzipper.c` @2838004 (0x2b4df4); `webserver.c` @2838572 (0x2b502c).
- [confirmed] Configuration/status vocabulary is colocated: `SYSTEM.GENERAL.FW_VERSION` @2838116 (0x2b4e64); `DIDMNG.GENERAL.NUM_DIDS` @2817696 (0x2afea0).
- [likely] A product-owned embedded web server and filesystem service are part of this raw payload. The names are static evidence, but no valid raw-image disassembly/xref proves activation or task boundaries.

## Unresolved
No kernel, init system, process list, ELF load map, or scheduler task table has been parsed. `WebserverStart` and `FilesystemStart` must be mapped to executable calls or observed in isolated runtime before calling them active processes.
Action status: RUNTIME-NEEDED.
