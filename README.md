# AI-Based Landslide Risk Assessment and Early Warning System

MVP for Sikkim, India. The app separates static susceptibility from rainfall-triggered risk. It does not predict exact time or occurrence.

## Quick start
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

The dashboard starts in clearly labelled demonstration mode using deterministic synthetic feature points for UI smoke testing only. These are not historical records. Supply a real CSV/GeoJSON/Shapefile inventory with `latitude,longitude,label` and feature columns, then run `python -m src.models.train --inventory data/raw/landslides.geojson`.

No external datasets are bundled or claimed acquired. See `reports/dataset_documentation.md`. Add SRTM/WorldCover/SoilGrids/rainfall/OSM and the NRSC/Bhuvan inventory through the documented workflow.

This workspace had no configured Git remote. Add yours and push without force: `git remote add origin https://github.com/<user>/<repo>.git; git push -u origin main`.
