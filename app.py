import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.title("🛠️ Red Nacional de Talleres - Gestión Postventa")

# Coordenadas maestras por ciudad
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
    "CUENCA": [-2.9001, -79.0059],
    "CHONE": [-0.6981, -80.0936],
    "BABAHOYO": [-1.8022, -79.5344]
}

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    except:
        df = pd.read_csv("talleres_streamlit_completo.csv")
    
    df.columns = df.columns.str.strip()
    
    lats, lons = [], []
    city_counts = {}

    for _, row in df.iterrows():
        city = str(row['CUIDAD']).strip().upper()
        base_lat, base_lon = CITY_COORDS.get(city, [-1.8312, -78.1834])
        
        # Lógica de dispersión: si la ciudad se repite, movemos el pin en un círculo
        if city in city_counts:
            count = city_counts[city]
            # Radio de dispersión (aprox 1.5km para que se vean separados pero en la misma ciudad)
            angle = count * (2 * math.pi / 8) # Distribuye hasta 8 talleres en círculo
            radius = 0.012 
            
            new_lat = base_lat + (radius * math.cos(angle))
            new_lon = base_lon + (radius * math.sin(angle))
            lats.append(new_lat)
            lons.append(new_lon)
            city_counts[city] += 1
        else:
            lats.append(base_lat)
            lons.append(base_lon)
            city_counts[city] = 1
            
    df['lat'] = lats
    df['lon'] = lons
    return df

try:
    df = load_data()

    # Filtros
    st.sidebar.header("Filtros de Red")
    ciudades_disponibles = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades_disponibles)

    df_mapa = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    # Mapa
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df_mapa.iterrows():
        # Popups limpios
        info = f"""
        <div style='font-family: sans-serif; font-size: 12px;'>
            <b style='color:#E74C3C;'>{row['NOMBRE DEL TALLER ']}</b><br>
            <b>Resp:</b> {row['PERSONA RESPONSABLE']}<br>
            <b>Tel:</b> {row['NUMEROS DE CONTACTO (MINIMO 2)']}
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(info, max_width=250),
            tooltip=f"{row['NOMBRE DEL TALLER ']} - {row['CUIDAD']}",
            icon=folium.Icon(color="red", icon="wrench", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=550)
    st.dataframe(df_mapa, use_container_width=True)

except Exception as e:
    st.error(f"Error de visualización: {e}")
