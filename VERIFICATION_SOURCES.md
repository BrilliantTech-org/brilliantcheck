# Official Verification Sources

Reference list of **official** (manufacturer/vendor) warranty, authenticity, and IMEI verification portals that brilliantcheck can cross-check against. Prefer these over third-party IMEI sites.

## Apple
- Coverage / warranty by serial or IMEI: https://checkcoverage.apple.com/
- (Requires Apple ID sign-in for some lookups.)

## Samsung
- Product registration + warranty: https://www.samsung.com/us/support/register/ (and regional variants)
- Samsung Members app (in-device) for IMEI/authenticity
- Samsung support warranty: https://www.samsung.com/us/support/warranty/

## Xiaomi
- Device verification (region-specific; site often geo-blocked): https://www.mi.com/ (verify section)
- Mi Account device list for registered devices

## OPPO
- Authenticity & warranty status check: https://support.oppo.com/en/warranty-check/

## Tecno (Transsion)
- Warranty check (IMEI): https://www.tecno-mobile.com/warranty/

## Itel (Transsion)
- Support portal: https://www.itel-life.com/ (warranty via Carlcare)
- Carlcare warranty check (covers itel/Tecno/Infinix): https://www.carlcare.com/global/warranty-check/

## Infinix (Transsion)
- Support: https://www.infinixmobility.com/
- Carlcare warranty check: https://www.carlcare.com/global/warranty-check/

## Nokia / HMD
- IMEI / warranty checker: https://www.hmd.com/en_int/support/topics/imei-checker

## General / third-party (fallback only)
- IMEI.info, IMEI24 — community databases, not authoritative; use only as fallback.

## Notes
- Always treat IMEI/serial as sensitive; redact in logs and bug reports.
- Online lookups may be rate-limited or geo-blocked; cache results in SQLite.
- Offline bundled fingerprint DB takes precedence; online is fallback.