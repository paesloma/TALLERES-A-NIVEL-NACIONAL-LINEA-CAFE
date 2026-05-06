import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.title("🛠️ Red Nacional de Talleres por Ciudad")

# Coordenadas base por ciudad
CITY_COORDS = {
    "SANTO DOMINGO": [-0.2530, -79.1754],
    "MANTA": [-0.9513, -80.7139],
    "EL COCA": [-0.4665, -76.9872],
    "RIOBAMBA": [-1.6708, -78.6534],
    "RIOBAMBA GUANO": [-1.6110, -78.6315],
    "PORTOVIEJO": [-1.0547, -80.4533],
    "QUITO": [-0.1807, -78.4678],
    "MACHALA": [-3.2581, -79.9553],
    "MILAGRO": [-2.1278, -79.5919],
    "PASAJE": [-3.3242, -79.8051],
    "GUAYAQUIL": [-2.1710, -79.9224],
    "LOJA": [-3.9931, -79.2042],
    "QUEVEDO": [-1.0225, -79.4601],
    "AMBATO": [-1.2491, -78.6272],
    "IBARRA": [0.3517, -78.1223],
    "LAGO AGRIO": [0.0847, -76.8828],
    "LATACUNGA": [-0.9314, -78.6148],
    "CUENCA": [-2.9001, -79.0059]
}

@st.cache_data
def load_data():
    # Intenta cargar el archivo
    try:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    except:
        df = pd.read_csv("talleres_streamlit_completo.csv")
    
    df.columns = df.columns.str.strip()
    
    # Asignar coordenadas y aplicar un pequeño desplazamiento si se repite la ciudad
    lats, lons = [], []
    counts = {}
    
    for city in df['CUIDAD'].str.strip().str.upper():
        base_lat, base_lon = CITY_COORDS.get(city, [-1.8312, -78.1834])
        
        # Si la ciudad ya apareció, movemos el pin un poquito (0.005 grados)
        if city in counts:
            counts[city] += 1
            offset = counts[city] * 0.005 
            lats.append(base_lat + offset)
            lons.append(base_lon + offset)
        else:
            counts[city] = 0
            lats.append(base_lat)
            lons.append(base_lon)
            
    df['lat'] = lats
    df['lon'] = lons
    return df

try:
    df = load_data()

    # Filtro lateral
    st.sidebar.header("Filtros")
    todas_ciudades = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", todas_ciudades)

    df_filtered = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    # Mapa con estilo oscuro
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df_filtered.iterrows():
        popup_text = f"<b>{row['NOMBRE DEL TALLER ']}</b><br>Ciudad: {row['CUIDAD']}<br>Dirección: {row['DIRECCION']}"
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_text, max_width=250),
            tooltip=row['NOMBRE DEL TALLER '],
            icon=folium.Icon(color="blue", icon="wrench", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=550)
    st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
