# Earthquake Catalog Source Survey

| Source | Region | Coverage (Space, Time, Min Mag) | Access Method | Output Formats | Auth Needed? | Result Caps | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **USGS ComCat** | Global (CA-strong) | Global, Historical to Real-time, All Mags | FDSN | GeoJSON / CSV / QuakeML | No | 20,000 events | Clean API |
| **ISC / ISC-GEM** | Global (authoritative) | Global, 1900-Present, All Mags | FDSN / Bulk | CSV / QuakeML | No | None | Clean API |
| **EMSC-CSEM** | Global / Euro-Med | Euro-Med focused + Global, Historical to Real-time | FDSN + WebSocket | QuakeML / JSON / CSV | No | 20,000 events | Clean API |
| **IRIS EarthScope** | Global | Global, Historical to Real-time | FDSN | QuakeML / Text | No | None | Clean API |
| **GEOFON/GFZ** | Global | Global, Aug 2007-Present, All Mags | FDSN | QuakeML / Text | No | None | Clean API |
| **Global CMT** | Global | Global, 1976-Present, Mw >= 5 | Bulk file download | NDK | No | None | Clean |
| **SCEDC** | California | Southern California, Historical to Real-time | FDSN | QuakeML / Text | No | None | Clean API |
| **NCEDC** | California | Northern California, Historical to Real-time | FDSN | QuakeML / Text | No | None | Clean API |
| **INGV (ISIDE)** | Italy | Italy, Historical to Real-time | FDSN | QuakeML / Text | No | None | Clean API |
| **INGV HORUS** | Italy | Italy, 1960-Present, Mw | Bulk file download | Text (Needs parsing) | No | None | Needs Parsing |
| **NOA** | Greece | Greece, Historical to Real-time | FDSN | QuakeML / Text | No | None | Clean API |
| **AFAD** | Türkiye | Türkiye, Historical to Real-time | Custom REST | JSON | No | None | Clean API |
| **GeoNet** | New Zealand | New Zealand, Historical to Real-time | FDSN / QuakeSearch / WFS | CSV / QuakeML | No | None | Clean API |
| **JMA / NIED** | Japan | Japan, Historical to Real-time | Scrape | Fixed-width deck | Yes (Registration) | None | Needs Scraping |
| **CSN** | Chile | Chile, Historical to Real-time | Scrape / Zenodo static | HTML / CSV | No | None | Needs Scraping |
| **CWA GDMS** | Taiwan | Taiwan, Historical to Real-time | Scrape | Text / CSV | Yes (Login) | None | Needs Scraping |
| **KOERI / AUTH** | Türkiye / Greece | Regional, Historical to Real-time | Scrape | HTML / `<pre>` text | No | None | Needs Scraping |
