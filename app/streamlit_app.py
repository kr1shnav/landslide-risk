import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
from src.data.preprocessing import demo_features
from src.data.raster import srtm_tiles_for_bounds
from src.risk.risk_engine import assess_risk
from src.models.train import train
from src.visualization.maps import sikkim_map
from streamlit_folium import st_folium

ROOT=Path(__file__).resolve().parents[1]
st.set_page_config(page_title='Landslide Risk | Sikkim',page_icon='⛰️',layout='wide')
st.markdown('''<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
[data-testid="stMetricValue"] {font-size: 1.35rem;}
.risk-note {border-left: 4px solid #2f80ed; padding: .65rem 1rem; background: #f5f9ff;}
</style>''',unsafe_allow_html=True)
st.title('AI-Based Landslide Risk Assessment and Early Warning System')
st.caption('Sikkim, India · transparent MVP with explicit real-data availability')
df=demo_features(); dem=ROOT/'data/processed/sikkim_dem.tif'; inventory=ROOT/'data/raw/landslides.geojson'; rainfall=ROOT/'data/raw/rainfall.csv'
if not inventory.exists(): st.warning('DEMONSTRATION MODE: no genuine historical landslide inventory is present. Synthetic points are for interface/training-pipeline testing only.')
def status(path): return 'AVAILABLE' if path.exists() else 'MISSING'

t1,t2,t3,t4,t5,t6,t7=st.tabs(['Overview','Risk Map','Prediction','Rainfall Analysis','Terrain Analysis','Model Evaluation','Dataset Explorer'])
with t1:
    st.subheader('Static susceptibility is not rainfall-triggered risk')
    st.write('Susceptibility describes static environmental tendency. Rainfall-triggered risk is a configurable heuristic combining susceptibility and recent rainfall. It is not a calibrated probability and does not predict exact timing or occurrence.')
    a,b,c,d=st.columns(4); a.metric('Study area','Sikkim'); b.metric('DEM',status(dem)); c.metric('Inventory',status(inventory)); d.metric('Rainfall',status(rainfall))
    st.info('The app remains usable with missing datasets; genuine model performance is not claimed until a labelled inventory and feature layers are supplied.')
with t2:
    st.subheader('Interactive Sikkim map')
    st_folium(sikkim_map(),width=1100,height=520)
    st.caption('Base map and boundary context are available. Event layers appear after a genuine inventory is imported.')
with t3:
    left,right=st.columns(2)
    with left:
        st.number_input('Latitude',27.1,28.2,27.53); st.number_input('Longitude',88.0,89.0,88.5); sus=st.slider('Static susceptibility score',0.,1.,.5); st.number_input('Elevation (m)',0.,9000.,1800.); st.number_input('Slope (degrees)',0.,90.,25.)
    with right:
        r1=st.number_input('Rainfall 1-day (mm)',0.,1000.,20.); r3=st.number_input('Rainfall 3-day (mm)',0.,2000.,45.); r7=st.number_input('Rainfall 7-day (mm)',0.,4000.,100.)
        res=assess_risk(sus,r1,r3,r7); st.metric('Risk category',res.category); st.metric('Heuristic score',f'{res.score:.2f}'); st.info('Contributors: '+res.explanation)
with t4:
    st.subheader('Rainfall accumulation inputs')
    st.write('Thresholds are configuration values requiring local calibration. No calibrated rainfall anomaly is available unless a historical baseline is supplied.')
    rain_df=pd.DataFrame({'window':['1-day','3-day','7-day'],'accumulation_mm':[r1,r3,r7]}); st.bar_chart(rain_df.set_index('window'))
with t5:
    st.subheader('Terrain data availability')
    st.write('Required SRTM tiles for the validated boundary:', ', '.join(srtm_tiles_for_bounds((88.0134695,27.0794491,88.9201485,28.1289151))))
    if dem.exists(): st.success('Processed DEM available; terrain rasters can be explored here.')
    else: st.warning('Processed DEM missing. Import a GeoTIFF or complete the SRTM download before generating terrain rasters.')
with t6:
    st.subheader('Model evaluation')
    if st.button('Run demonstration training'):
        with st.spinner('Training demonstration models…'): result=train()
        st.session_state['metrics']=result
    result=st.session_state.get('metrics')
    if result:
        st.dataframe(pd.DataFrame(result).T[['accuracy','precision','recall','f1','roc_auc']],width='stretch')
        st.warning('These metrics are demonstration-mode results from synthetic fixtures, not scientific validation.')
    else: st.info('Click the button to exercise the reproducible training pipeline. Real performance is shown only after genuine inventory data is supplied.')
with t7:
    st.subheader('Dataset explorer')
    rows=[('Sikkim boundary','data/processed/sikkim_boundary.geojson',True),('SRTM DEM','data/processed/sikkim_dem.tif',dem.exists()),('Landslide inventory','data/raw/landslides.geojson',inventory.exists()),('Rainfall','data/raw/rainfall.csv',rainfall.exists())]
    st.dataframe(pd.DataFrame(rows,columns=['dataset','expected_path','available']),width='stretch')
    st.dataframe(df.head(20),width='stretch')
