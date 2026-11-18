from pathlib import Path
import pandas as pd
import numpy as np
FEATURES=['elevation','slope','aspect','curvature','twi','rainfall_1d','rainfall_3d','rainfall_7d','landcover','soil','distance_river','distance_road','ndvi']

def remove_duplicates(df: pd.DataFrame, subset=None) -> pd.DataFrame:
    """Remove exact duplicate inventory records, retaining the first record.

    The number removed is stored in ``DataFrame.attrs`` for audit/reporting.
    No records are inferred or merged based on proximity.
    """
    # Exact-row deduplication is intentionally date-aware: a date column is
    # part of the row identity when present, so same-coordinate events on
    # different dates are retained.
    before = len(df)
    cleaned = df.drop_duplicates(subset=subset, keep='first').reset_index(drop=True)
    cleaned.attrs['duplicates_removed'] = before - len(cleaned)
    return cleaned

def clean_inventory(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Normalize columns, remove exact duplicates, and report missing values."""
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]
    cleaned = remove_duplicates(df)
    report = {
        'input_records': len(df),
        'output_records': len(cleaned),
        'duplicates_removed': cleaned.attrs.get('duplicates_removed', 0),
        'missing_values': int(cleaned.isna().sum().sum()),
    }
    return cleaned, report

def load_inventory(path: str | Path) -> pd.DataFrame:
    p=Path(path)
    if p.suffix.lower()=='.csv': df=pd.read_csv(p)
    else:
        import geopandas as gpd
        g=gpd.read_file(p).to_crs(4326); df=pd.DataFrame(g.drop(columns='geometry')); df['longitude']=g.geometry.x; df['latitude']=g.geometry.y
    return clean_inventory(df)[0]
def demo_features(n=240,seed=42):
    rng=np.random.default_rng(seed); d={f:rng.uniform(0,1,n) for f in FEATURES}
    d.update(latitude=rng.uniform(27.1,28.2,n),longitude=rng.uniform(88.0,88.9,n),label=(rng.random(n)<.35).astype(int))
    d.update(elevation=rng.uniform(300,5200,n),slope=rng.uniform(0,55,n),aspect=rng.uniform(0,360,n),rainfall_1d=rng.gamma(2,18,n),rainfall_3d=rng.gamma(3,25,n),rainfall_7d=rng.gamma(5,30,n))
    return pd.DataFrame(d)
