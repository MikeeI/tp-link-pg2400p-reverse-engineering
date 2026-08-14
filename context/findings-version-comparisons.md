# Version Comparisons

Sources: version-scoped `raw-image-map-evidence.txt` and immutable raw payloads.
Action status: `BLOCKED` for semantic updater comparison because no updater code path or reset transfer is proven.

## Constant comparison configuration

Both payloads were imported as Ghidra Raw Binary with `Xtensa:LE:32:default`, compiler spec `default`, and base `0x63000000`.
Both runs used `-noanalysis -readOnly -deleteProject -analysisTimeoutPerFile 120 -max-cpu 1`.
1.0.3 SHA-256 is `00213d7d32a1d29c654b38570c798ae176ae24f6223e4e0794aa231d59df545d` and size is `0x3a6b8c`.
1.1.0 SHA-256 is `79745b3a349b2d92ff0a6801f4f35fa2e8893725119334260ba7175c05f47716` and size is `0x3a8d6c`.
The newer raw payload is 8,672 bytes larger.

## Raw map and early native code

[confirmed] Both images map consistently as `static address = 0x63000000 + raw offset`.
1.0.3 header-table bytes at raw `0xd4` are `782c00632c2b0063882f0063f85a0063c05a0063845a0063485a0063`.
1.1.0 header-table bytes at raw `0xd4` are `182c0063cc2a0063282f0063985a0063605a0063245a0063e8590063`.
The first table target moves from raw `0x2c78` / `0x63002c78` to `0x2c18` / `0x63002c18`.
Both target byte sequences are exactly `3661008c2288e2ac78929306`.
Under the constant LE configuration those bytes decode as a valid Xtensa function prologue and control-flow sequence.
This is a structural relocation, not a semantic change claim.

## Update and integrity anchor comparison

| Anchor | 1.0.3 raw offset / static address | 1.1.0 raw offset / static address | Offset delta |
| --- | --- | --- | --- |
| `FlUpgradeFLASHCRCValidation` | `0x2945c0` / `0x632945c0` | `0x295a80` / `0x63295a80` | `+0x14c0` |
| `FLUPGRADE.GENERAL.START` | `0x2ae9f8` / `0x632ae9f8` | `0x2afeb8` / `0x632afeb8` | `+0x14c0` |
| `Running: calculating CRC` | `0x2b0e8c` / `0x632b0e8c` | `0x2b234c` / `0x632b234c` | `+0x14c0` |
| `Upgrade thread started` | `0x2b2fe0` / `0x632b2fe0` | `0x2b4f1c` / `0x632b4f1c` | `+0x1f3c` |
| `FLUPGRADE.GENERAL.SECURE` | `0x2b3930` / `0x632b3930` | `0x2b5974` / `0x632b5974` | `+0x2044` |
| `httpupg` | `0x2b394c` / `0x632b394c` | `0x2b5990` / `0x632b5990` | `+0x2044` |
| `FlUpgradeFileCRCValidation:` | `0x2cbadc` / `0x632cbadc` | `0x2cdb14` / `0x632cdb14` | `+0x2038` |

[confirmed] Every listed anchor string exists in both exact raw artifacts.
[confirmed] The fixed 256-byte contexts at START, Running, SECURE, httpupg, and FileCRC have identical SHA-256 values across versions.
The START context SHA-256 is `af567b36fe47e8c653e8c73d67b2bfcdbbcd5a1b6075025219a443590de1a6cf`.
The Running context SHA-256 is `dbe1071bc8a6150200da58a1fa0f09ebc08c7c64486dbf02c3176da6356a6fc1`.
The SECURE context SHA-256 is `4d29ee3e124dc5c2e0a3911dc31f1dc45161894756a4b53378393541cda0bb67`.
The httpupg context SHA-256 is `28065500f14662a48032b87c851aac64a5ff1d2e62ee55c7d40b31b1c7bc4ef8`.
The FileCRC context SHA-256 is `5d55bb1ed444aa23f63e2c9a97b75788acd0571476ab821949bd0ec7b65fbcd4`.
The FLASHCRC contexts differ at four bytes only: relative `0x40` `9cd6`→`d4f6` and relative `0x4c` `a4d6`→`dcf6`.
[likely] The delta transitions `+0x14c0` to `+0x1f3c` to `+0x2044` localize intervening layout changes in raw data/string regions.
[unresolved] No matched updater function, xref, control-flow edge, or acceptance/failure branch supports attributing those layout changes to security behavior.

## Next proof

Decode `descriptor.upg` fields following `firmware B:/fw` at raw `.ftp` offset `0x178` for both releases.
Use the recovered loader-to-firmware handoff to seed matched updater functions under this same LE/base configuration.
Compare only validated function bytes, literal references, calls, and success/failure control flow before assigning a security semantic difference.
