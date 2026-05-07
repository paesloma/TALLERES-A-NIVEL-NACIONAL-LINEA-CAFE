import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Gestión por Ciudad")

# Diccionario maestro de coordenadas (Asegúrate de que los nombres coincidan con tu Excel)
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
        # Carga el archivo generado o el del formulario
        df = pd.read_csv("talleres_streamlit_completo.csv")
    except:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    
    # Limpiamos los nombres de las columnas para evitar errores de espacios
    df.columns = df.columns.str.strip()
    
    lats, lons = [], []
    city_counts = {}

    for _, row in df.iterrows():
        # Obtenemos el nombre de la ciudad (usando el nombre de columna de tu archivo: CUIDAD)
        city_raw = str(row.get('CUIDAD', '')).strip().upper()
        
        # Priorizar coordenadas individuales si existen en el CSV
        lat_val = row.get('lat')
        lon_val = row.get('lon')
        
        if pd.notnull(lat_val) and pd.notnull(lon_val) and float(lat_val) != -1.8312:
            base_lat, base_lon = float(lat_val), float(lon_val)
        else:
            base_lat, base_lon = CITY_COORDS.get(city_raw, [-1.8312, -78.1834])
        
        # Dispersión circular para que no se encimen los pines de la misma ciudad
        if city_raw in city_counts:
            count = city_counts[city_raw]
            angle = count * (2 * math.pi / 8)
            radius = 0.009 # Ajuste de distancia entre pines
            lats.append(base_lat + (radius * math.cos(angle)))
            lons.append(base_lon + (radius * math.sin(angle)))
            city_counts[city_raw] += 1
        else:
            lats.append(base_lat)
            lons.append(base_lon)
            city_counts[city_raw] = 1
            
    df['lat_viz'] = lats
    df['lon_viz'] = lons
    return df

try:
    df = load_data()

    # Barra lateral de filtros
    st.sidebar.header("Filtros de Red")
    ciudades_lista = sorted(df["CUIDAD"].dropna().unique())
    seleccion = st.sidebar.multiselect("Seleccionar Ciudad:", ciudades_lista)

    df_filtered = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    # Mapa con estilo oscuro
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df_filtered.iterrows():
        nombre = row.get('NOMBRE DEL TALLER', 'Taller')
        ciudad = row.get('CUIDAD', 'N/A')
        direccion = row.get('DIRECCION', 'N/A')
        
        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 12px; width: 200px;'>
            <b style='color:#E74C3C;'>{nombre}</b><br>
            <b>Ciudad:</b> {ciudad}<br>
            <b>Dirección:</b> {direccion}
        </div>
        """
        folium.Marker(
            location=[row['lat_viz'], row['lon_viz']],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{nombre} - {ciudad}",
            icon=folium.Icon(color="red", icon="wrench", prefix="fa")
        ).add_to(m)

    # Mostrar mapa
    st_folium(m, width="100%", height=550)

    # Mostrar la tabla de información (Asegurando que CUIDAD sea visible)
    st.markdown(f"### Detalle de Talleres ({len(df_filtered)} registros)")
    
    # Definimos qué columnas técnicas queremos ocultar (lat/lon de cálculo)
    # PERO mantenemos 'CUIDAD'
    cols_tecnicas = ['lat_viz', 'lon_viz', 'lat', 'lon']
    columnas_finales = [c for c in df_filtered.columns if c not in cols_tecnicas]
    
    st.dataframe(df_filtered[columnas_finales], use_container_width=True)

except Exception as e:
    st.error(f"Error en la aplicación: {e}")
