import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Vista Individual")

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
        df = pd.read_csv("talleres_streamlit_completo.csv")
    except:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    
    # 1. Limpiamos los nombres de todas las columnas (quita espacios al inicio y al final)
    df.columns = df.columns.str.strip()
    
    lats, lons = [], []
    city_counts = {}

    for _, row in df.iterrows():
        # Usamos .get seguro para la ciudad
        city = str(row.get('CUIDAD', '')).strip().upper()
        
        lat_val = row.get('lat')
        lon_val = row.get('lon')
        
        # Si tiene coordenadas propias y válidas
        if pd.notnull(lat_val) and pd.notnull(lon_val) and lat_val != -1.8312:
            base_lat, base_lon = float(lat_val), float(lon_val)
        else:
            base_lat, base_lon = CITY_COORDS.get(city, [-1.8312, -78.1834])
        
        # Lógica para separar pines en una misma coordenada
        if city in city_counts:
            count = city_counts[city]
            angle = count * (2 * math.pi / 8) # Distribución radial
            radius = 0.008 
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

try:
    df = load_data()

    # Filtros seguros ignorando celdas vacías
    ciudades = sorted(df["CUIDAD"].dropna().unique())
    seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades)
    df_mapa = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df_mapa.iterrows():
        # 2. CORRECCIÓN PRINCIPAL: Accedemos al nombre exacto y limpio de la columna
        nombre = row.get('NOMBRE DEL TALLER', 'Taller')
        direccion = row.get('DIRECCION', 'Sin dirección')
        contacto = row.get('NUMEROS DE CONTACTO (MINIMO 2)', 'N/A')
        
        popup_info = f"<div style='width: 200px;'><b>{nombre}</b><br>{direccion}<br><b>Tel:</b> {contacto}</div>"
        
        folium.Marker(
            location=[row['lat_viz'], row['lon_viz']],
            popup=folium.Popup(popup_info, max_width=250),
            tooltip=nombre,
            icon=folium.Icon(color="red", icon="wrench", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=550)
    
    # 3. Ocultar columnas técnicas para que no salgan en tu tabla
    cols_to_drop = ['lat_viz', 'lon_viz', 'lat', 'lon']
    cols_to_show = [col for col in df_mapa.columns if col not in cols_to_drop]
    
    st.dataframe(df_mapa[cols_to_show], use_container_width=True)

except Exception as e:
    st.error(f"Error detectado: {e}")
