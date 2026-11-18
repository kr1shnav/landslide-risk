# Dataset documentation

| Dataset | Source | Resolution | CRS | Status/limitations |
|---|---|---|---|---|
| Landslide inventory | NRSC Atlas / Bhuvan | Product-dependent | Confirm from file | Manual import; unrecorded locations are not confirmed negatives |
| DEM | NASA SRTM / Earthdata | ~30 m | Usually WGS84 | Registration/terms may apply |
| Rainfall | NASA GPM IMERG | 0.1 degree | Geographic | Registration/product terms may apply |
| Land cover | ESA WorldCover | 10 m | Product-dependent | Attribution required |
| Soil | ISRIC SoilGrids | Product-dependent | Product-dependent | Uncertainty and terms apply |
| Roads/rivers | OpenStreetMap | Vector/current | Product-dependent | ODbL attribution |

No real-world records are fabricated. Demo features are deterministic test fixtures only. The app records actual file metadata during validation.

## Validation and ingestion report

Inventory ingestion normalizes column names, validates latitude/longitude presence for CSV files, requires a CRS for spatial files, counts missing values, and removes only exact duplicate rows. Same coordinates with different dates remain separate records. The boundary workflow downloads India ADM1 GeoJSON from geoBoundaries, extracts Sikkim, reprojects to EPSG:4326, and clips point inventories using a spatial join. Downloaded/raw files remain gitignored.

## Current acquisition report (2026-11-18)

- Sikkim boundary: acquired from geoBoundaries India ADM1 and validated as genuine GeoJSON, not an LFS pointer. India source contains 36 features; extracted Sikkim contains 1 valid polygon feature. CRS: EPSG:4326. Bounds: longitude 88.0134695–88.9201485, latitude 27.0794491–28.1289151. Local processed file: `data/processed/sikkim_boundary.geojson` (160,660 bytes).
- Landslide inventory: no NRSC/Bhuvan records were acquired in this run. Real-data-only CSV, GeoJSON, and Shapefile ingestion plus Sikkim clipping are implemented. No historical event count is claimed.
- SRTM DEM: no raster was acquired in this run. `src/data/raster.py` supports public AWS SRTM HGT tile download and manual GeoTIFF validation; coverage, CRS, resolution, and nodata are reported only after a file is supplied.
- Visualization: `reports/figures/sikkim_boundary.png` was generated from the validated boundary.
