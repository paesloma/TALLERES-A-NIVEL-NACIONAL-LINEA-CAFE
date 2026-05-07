import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Red Nacional TVS - Postventa", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Gestión de Contacto")

# Diccionario de coordenadas para respaldo
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
    # Carga del archivo procesado
    df = pd.read_csv("talleres_streamlit_completo.csv")
    df.columns = df.columns.str.strip()
    
    lats, lons = [], []
    city_counts = {}

    for _, row in df.iterrows():
        city = str(row.get('CUIDAD', '')).strip().upper()
        
        # Intentar usar coordenadas del CSV, si no, usar respaldo por ciudad
        lat_val = row.get('lat')
        lon_val = row.get('lon')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val) and float(lat_val) != -1.8312:
            base_lat, base_lon = float(lat_val), float(lon_val)
        else:
            base_lat, base_lon = CITY_COORDS.get(city, [-1.8312, -78.1834])
        
        # Dispersión circular para evitar solapamiento
        if city in city_counts:
            count = city_counts[city]
            angle = count * (2 * math.pi / 8)
            radius = 0.009
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

    # Filtros
    ciudades_lista = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Seleccionar Ciudad:", ciudades_lista)
    df_filtered = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df_filtered.iterrows():
        nombre = row.get('NOMBRE DEL TALLER', 'Taller')
        ciudad = row.get('CUIDAD', 'N/A')
        # AQUÍ INCLUIMOS EL TELÉFONO DE FORMA EXPLÍCITA
        telefono = row.get('NUMEROS DE CONTACTO (MINIMO 2)', 'Sin teléfono registrado')
        direccion = row.get('DIRECCION', 'N/A')
        
        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 12px; width: 220px;'>
            <b style='color:#E74C3C; font-size:14px;'>{nombre}</b><br>
            <hr style='margin: 5px 0;'>
            <b>📞 Teléfono:</b> {telefono}<br>
            <b>📍 Ciudad:</b> {ciudad}<br>
            <b>🏠 Dirección:</b> {direccion}
        </div>
        """
        folium.Marker(
            location=[row['lat_viz'], row['lon_viz']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{nombre} - {telefono}",
            icon=folium.Icon(color="red", icon="phone", prefix="fa")
        ).add_to(m)

    st_folium(m, width="100%", height=550)

    # Tabla de información con el teléfono visible
    st.markdown(f"### Contactos de Talleres ({len(df_filtered)} registros)")
    cols_ocultar = ['lat_viz', 'lon_viz', 'lat', 'lon']
    cols_mostrar = [c for c in df_filtered.columns if c not in cols_ocultar]
    
    st.dataframe(df_filtered[cols_mostrar], use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
