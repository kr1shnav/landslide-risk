import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from src.data.raster import srtm_tiles_for_bounds
from src.models.predict import feature_row, predict, validate_prediction_inputs
from src.models.train import train
from src.risk.risk_engine import assess_risk
from src.visualization.maps import sikkim_map

ROOT=Path(__file__).resolve().parents[1]
BOUNDARY=ROOT/'data/processed/sikkim_boundary.geojson'
DEM=ROOT/'data/processed/sikkim_dem.tif'
INVENTORY=ROOT/'data/raw/landslides.geojson'
RAIN=ROOT/'data/raw/rainfall.csv'
st.set_page_config(page_title='Landslide Intelligence | Sikkim',page_icon='⛰️',layout='wide')
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;letter-spacing:-.02em;}
.block-container {max-width:1500px;padding:1.3rem 2.2rem 2rem;}
.hero {background:linear-gradient(135deg,#0b1324,#12243d 55%,#0e7490);border:1px solid #1e3a5f;border-radius:18px;padding:1.5rem 1.8rem;margin-bottom:1.1rem;color:#e6f6ff;}
.hero h1 {font-size:2.25rem;margin:.1rem 0 .35rem;color:#fff}.hero p {color:#b9d7e8;margin:0}
.eyebrow {font-size:.76rem;text-transform:uppercase;letter-spacing:.14em;color:#67e8f9;font-weight:700}
.card {background:#101b2d;border:1px solid #263c58;border-radius:13px;padding:1rem 1.1rem;min-height:92px}.label {font-size:.74rem;text-transform:uppercase;letter-spacing:.08em;color:#93a9bf}.value {font-family:'Space Grotesk';font-size:1.35rem;font-weight:700;color:#f8fafc;margin-top:.35rem}.ok {color:#67e8a5}.missing {color:#fbbf74}
.risk-low {color:#67e8a5}.risk-moderate {color:#facc15}.risk-high {color:#fb923c}.risk-very-high {color:#fb7185}
[data-testid="stMetricValue"] {font-family:'Space Grotesk'}.stButton>button {border-radius:10px;font-weight:700;min-height:2.7rem}
</style>""",unsafe_allow_html=True)

def available(path): return path.exists()
def badge(label,path):
    state='AVAILABLE' if available(path) else 'MISSING'
    css='ok' if state=='AVAILABLE' else 'missing'
    return f"<div class='card'><div class='label'>{label}</div><div class='value {css}'>{state}</div></div>"
def risk_class(category): return category.lower().replace(' ','-')

with st.sidebar:
    st.markdown('## ⛰️ Landslide Intelligence')
    st.caption('Sikkim monitoring workspace')
    st.divider()
    st.markdown('**Navigation**')
    st.markdown('Prediction is the primary workspace. Use the tabs for supporting analysis.')
    st.divider()
    st.caption('MVP status')
    st.caption('Boundary: available')
    st.caption(f'DEM: {"available" if DEM.exists() else "missing"}')
    st.caption(f'Inventory: {"available" if INVENTORY.exists() else "missing"}')

st.markdown("<div class='hero'><div class='eyebrow'>AI-BASED GEOHAZARD MONITORING · SIKKIM, INDIA</div><h1>Landslide Intelligence</h1><p>Assess static susceptibility and rainfall-triggered risk from one focused workspace.</p></div>",unsafe_allow_html=True)
st.warning('DEMONSTRATION MODE: no genuine historical inventory or trained real-world model is currently present. Susceptibility results use the existing synthetic training pipeline for interface demonstration only; risk scores are heuristic, not calibrated probabilities.')

st.markdown('### Data availability')
k1,k2,k3,k4=st.columns(4)
k1.markdown(badge('Sikkim boundary',BOUNDARY),unsafe_allow_html=True)
k2.markdown(badge('Elevation / DEM',DEM),unsafe_allow_html=True)
k3.markdown(badge('Landslide inventory',INVENTORY),unsafe_allow_html=True)
k4.markdown(badge('Rainfall series',RAIN),unsafe_allow_html=True)

st.markdown('## Landslide risk prediction')
st.caption('Enter a location and recent rainfall. Optional land-cover and soil fields default to unavailable/neutral values when no layers are loaded.')
with st.form('prediction_form'):
    geo,env,opt=st.columns([1,1,1])
    with geo:
        st.markdown('**Location & terrain**')
        latitude=st.number_input('Latitude',27.1,28.2,27.53,step=.001,format='%.4f')
        longitude=st.number_input('Longitude',88.0,89.0,88.50,step=.001,format='%.4f')
        elevation=st.number_input('Elevation (m)',0.,9000.,1800.,step=50.)
        slope=st.number_input('Slope (degrees)',0.,90.,25.,step=1.)
        aspect=st.number_input('Aspect (degrees)',0.,360.,180.,step=5.)
    with env:
        st.markdown('**Rainfall trigger**')
        rainfall_1d=st.number_input('Rainfall · last 1 day (mm)',0.,1000.,20.,step=1.)
        rainfall_3d=st.number_input('Rainfall · last 3 days (mm)',0.,2000.,45.,step=1.)
        rainfall_7d=st.number_input('Rainfall · last 7 days (mm)',0.,4000.,100.,step=1.)
        st.caption('Thresholds are configurable demonstration thresholds requiring local calibration.')
    with opt:
        st.markdown('**Optional environmental inputs**')
        soil=st.number_input('Soil index (if available)',0.,1.,0.,step=.05)
        landcover=st.number_input('Land-cover index (if available)',0.,1.,0.,step=.05)
        st.info('No soil or land-cover layers are currently loaded. These values remain neutral placeholders.')
    analyze=st.form_submit_button('ANALYZE LANDSLIDE RISK',type='primary',width='stretch')

if analyze:
    values={'latitude':latitude,'longitude':longitude,'elevation':elevation,'slope':slope,'aspect':aspect,'rainfall_1d':rainfall_1d,'rainfall_3d':rainfall_3d,'rainfall_7d':rainfall_7d,'soil':soil,'landcover':landcover}
    try:
        validate_prediction_inputs(values)
        with st.spinner('Running susceptibility model and rainfall risk engine…'):
            train()
            susceptibility=predict(feature_row(values))
        risk=assess_risk(susceptibility,rainfall_1d,rainfall_3d,rainfall_7d)
        st.session_state['assessment']={'values':values,'susceptibility':susceptibility,'risk':risk}
    except Exception as exc:
        st.error(f'Unable to analyze inputs: {exc}')

assessment=st.session_state.get('assessment')
if assessment:
    risk=assessment['risk']; v=assessment['values']
    st.markdown('## Landslide risk assessment')
    st.success(f"Analysis complete for {v['latitude']:.4f}°N, {v['longitude']:.4f}°E")
    r1,r2,r3=st.columns(3)
    r1.metric('Risk category',risk.category)
    r2.metric('Susceptibility score',f"{assessment['susceptibility']:.2f}")
    r3.metric('Rainfall-triggered score',f"{risk.score:.2f}")
    st.markdown(f"<div class='card'><div class='label'>Assessment status</div><div class='value risk-{risk_class(risk.category)}'>{risk.category}</div><p><b>Susceptibility:</b> Demonstration model trained on synthetic fixtures. <b>Rainfall:</b> transparent heuristic, not calibrated probability.</p><p><b>Why:</b> {risk.explanation}.</p></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    c1.markdown('**Contributing factors**')
    c1.markdown(f"- Slope: {v['slope']:.1f}°\n- Elevation: {v['elevation']:.0f} m\n- Rainfall 1/3/7-day: {v['rainfall_1d']:.0f} / {v['rainfall_3d']:.0f} / {v['rainfall_7d']:.0f} mm")
    c2.markdown('**Classification legend**')
    c2.markdown('<span class="risk-low">● LOW</span> · <span class="risk-moderate">● MODERATE</span> · <span class="risk-high">● HIGH</span> · <span class="risk-very-high">● VERY HIGH</span>',unsafe_allow_html=True)

tabs=st.tabs(['Sikkim map','Rainfall analysis','Terrain analysis','Model evaluation','Dataset explorer'])
with tabs[0]:
    st.markdown('### Interactive Sikkim map')
    st_folium(sikkim_map(BOUNDARY),width='stretch',height=460)
    st.caption('The validated boundary is shown. Susceptibility heatmaps and historical event layers are intentionally withheld until genuine raster/inventory data are available.')
with tabs[1]:
    st.markdown('### Rainfall trigger analysis')
    rr=assessment['values'] if assessment else {'rainfall_1d':20,'rainfall_3d':45,'rainfall_7d':100}
    chart=pd.DataFrame({'window':['1-day','3-day','7-day'],'rainfall_mm':[rr['rainfall_1d'],rr['rainfall_3d'],rr['rainfall_7d']]}).set_index('window')
    st.bar_chart(chart)
    st.info('Historical anomaly unavailable: no baseline rainfall series is loaded.')
with tabs[2]:
    st.markdown('### Terrain analysis')
    st.write('Required SRTM tiles:', ', '.join(srtm_tiles_for_bounds((88.0134695,27.0794491,88.9201485,28.1289151))))
    if DEM.exists(): st.success('Processed DEM available.')
    else: st.info('No DEM loaded. Import a validated GeoTIFF or complete the SRTM workflow to generate elevation, slope, aspect, curvature, and TRI rasters.')
with tabs[3]:
    st.markdown('### Model evaluation')
    st.info('Run python -m src.models.train for the demonstration report. Any metrics from synthetic fixtures are not validated real-world performance.')
    st.code('python -m src.models.train',language='powershell')
with tabs[4]:
    st.markdown('### Dataset explorer')
    st.dataframe(pd.DataFrame([('Sikkim boundary',available(BOUNDARY)),('DEM',available(DEM)),('Landslide inventory',available(INVENTORY)),('Rainfall',available(RAIN))],columns=['dataset','available']),width='stretch')

