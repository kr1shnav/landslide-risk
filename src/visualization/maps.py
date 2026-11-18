import folium
import json
from pathlib import Path
def sikkim_map(boundary_path=None):
    m=folium.Map(location=[27.53,88.5],zoom_start=8,tiles='OpenStreetMap',control_scale=True)
    if boundary_path and Path(boundary_path).exists():
        data=json.loads(Path(boundary_path).read_text(encoding='utf-8'))
        folium.GeoJson(data,name='Sikkim boundary',style_function=lambda _: {'color':'#38bdf8','weight':3,'fillColor':'#0ea5e9','fillOpacity':0.08},tooltip=folium.GeoJsonTooltip(fields=['shapeName'],aliases=['State'])).add_to(m)
    folium.LayerControl().add_to(m); return m
