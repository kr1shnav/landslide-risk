import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from src.data.preprocessing import demo_features
from src.risk.risk_engine import assess_risk
from src.visualization.maps import sikkim_map
from streamlit_folium import st_folium
st.set_page_config(page_title='Landslide Risk | Sikkim',page_icon='⛰️',layout='wide')
st.title('AI-Based Landslide Risk Assessment and Early Warning System')
st.caption('Sikkim, India · Demonstration mode unless real labelled data is supplied')
st.warning('Demo mode uses deterministic synthetic feature points for interface testing only. They are not historical observations and are not scientific validation.')
df=demo_features(); t1,t2,t3,t4=st.tabs(['Overview','Interactive Risk Map','Prediction','Model Status'])
with t1:
    st.subheader('Susceptibility vs rainfall-triggered risk')
    st.write('Susceptibility estimates static environmental tendency. Risk is a configurable heuristic combining susceptibility with recent rainfall; it is not a calibrated probability or exact event forecast.')
    a,b,c=st.columns(3); a.metric('Study area','Sikkim'); b.metric('Demo points',len(df)); c.metric('External datasets','0 acquired')
with t2:
    st_folium(sikkim_map(),width=1100,height=520)
    st.dataframe(df[['latitude','longitude','elevation','slope','rainfall_1d','rainfall_3d','rainfall_7d']].head(25),use_container_width=True)
with t3:
    left,right=st.columns(2)
    with left:
        st.number_input('Latitude',27.1,28.2,27.53); st.number_input('Longitude',88.0,89.0,88.5); sus=st.slider('Static susceptibility',0.,1.,.5); st.number_input('Elevation (m)',0.,9000.,1800.); st.number_input('Slope (degrees)',0.,90.,25.)
    with right:
        r1=st.number_input('Rainfall 1-day (mm)',0.,1000.,20.); r3=st.number_input('Rainfall 3-day (mm)',0.,2000.,45.); r7=st.number_input('Rainfall 7-day (mm)',0.,4000.,100.)
        res=assess_risk(sus,r1,r3,r7); st.metric('Risk category',res.category); st.metric('Heuristic score',f'{res.score:.2f}'); st.info('Main contributors: '+res.explanation)
with t4:
    st.info('No validated model is claimed until a real inventory and feature layers are supplied. Run `python -m src.models.train` to create Logistic Regression, Random Forest, and XGBoost reports in demonstration mode.')
