import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Vista Individual")

# Coordenadas exactas/centro de ciudades
CITY_COORDS = {
    "SANTO DOMINGO": [-0.2530, -79.1754], "MANTA": [-0.9513, -80.7139],
    "EL COCA": [-0.4665, -76.9872], "RIOBAMBA": [-1.6708, -78.6534],
    "RIOBAMBA GUANO": [-1.6110, -78.6315], "PORTOVIEJO": [-1.0547, -80.4533],
    "QUITO": [-0.1807, -78.4678], "MACHALA": [-3.2581, -79.9553],
    "MILAGRO": [-2.1278, -79.5919], "PASAJE": [-3.3242, -79.8051],
    "GUAYAQUIL": [-2.1710, -79.9224], "LOJA": [-3.9931, -79.2042],
    "QUEVEDO": [-1.0225, -79.4601], "AMBATO": [-1.2491, -78.6272],
    "IBARRA": [0.3517, -78.1223], "LAGO AGRIO": [0.0847, -76.8828],
    "LATACUNGA": [-0.9314, -78.6148], "CUENCA": [-2.9001, -79.0059]
}

@st.cache_data
def load_data():
    try:
        # Cargamos el archivo que subiste
        df = pd.read_csv("talleres_streamlit_completo.csv")
    except:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    
    df.columns = df.columns.str.strip()
    
    lats, lons = [], []
    city_counts = {}

    for _, row in df.iterrows():
        city = str(row.get('CUIDAD', '')).strip().upper()
        # Intentar usar lat/lon del archivo, si no, usar centro de ciudad
        lat_val = row.get('lat')
        lon_val = row.get('lon')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val) and lat_val != -1.8312:
            base_lat, base_lon = float(lat_val), float(lon_val)
        else:
            base_lat, base_lon = CITY_COORDS.get(city, [-1.8312, -78.1834])
        
        # DISPERSIÓN: Si hay más de uno en la misma coordenada, los separamos
        if city in city_counts:
            count = city_counts[city]
            angle = count * (2 * math.pi / 6) # Distribución en círculo
            radius = 0.008 # Distancia entre pines
            lats.append(base_lat + (radius * math.cos(angle)))
            lons.append(base_lon + (radius * math.sin(angle)))
            city_counts[city] += 1
        else:
            lats.append(base_lat)
            lons.append(base_lon)
            city_counts[city] = 1
            
    df['lat_viz'] = lats
    df['lon_viz'] = lons
    return df

df = load_data()

# Filtros
ciudades = sorted(df["CUIDAD"].unique())
seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades)
df_mapa = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

# Mapa SIN MarkerCluster para ver los pines individuales
m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

for i, row in df_mapa.iterrows():
    popup_info = f"<b>{row['NOMBRE DEL TALLER ']}</b><br>{row['DIRECCION']}"
    folium.Marker(
        location=[row['lat_viz'], row['lon_viz']],
        popup=folium.Popup(popup_info, max_width=250),
        tooltip=row['NOMBRE DEL TALLER '],
        icon=folium.Icon(color="red", icon="wrench", prefix="fa")
    ).add_to(m)

st_folium(m, width="100%", height=550)
st.dataframe(df_mapa.drop(columns=['lat_viz', 'lon_viz']), use_container_width=True)
