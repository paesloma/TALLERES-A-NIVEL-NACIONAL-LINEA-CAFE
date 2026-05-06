import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

# Estilo para mejorar la legibilidad
st.markdown("## 🛠️ Red Nacional de Servicios Técnicos TVS")

CITY_COORDS = {
    "SANTO DOMINGO": [-0.2530, -79.1754], "MANTA": [-0.9513, -80.7139],
    "EL COCA": [-0.4665, -76.9872], "RIOBAMBA": [-1.6708, -78.6534],
    "RIOBAMBA GUANO": [-1.6110, -78.6315], "PORTOVIEJO": [-1.0547, -80.4533],
    "QUITO": [-0.1807, -78.4678], "MACHALA": [-3.2581, -79.9553],
    "MILAGRO": [-2.1278, -79.5919], "PASAJE": [-3.3242, -79.8051],
    "GUAYAQUIL": [-2.1710, -79.9224], "LOJA": [-3.9931, -79.2042],
    "QUEVEDO": [-1.0225, -79.4601], "AMBATO": [-1.2491, -78.6272],
    "IBARRA": [0.3517, -78.1223], "LAGO AGRIO": [0.0847, -76.8828],
    "LATACUNGA": [-0.9314, -78.6148], "CUENCA": [-2.9001, -79.0059],
    "CHONE": [-0.6981, -80.0936], "BABAHOYO": [-1.8022, -79.5344]
}

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    except:
        df = pd.read_csv("talleres_streamlit_completo.csv")
    
    df.columns = df.columns.str.strip()
    
    # Asignación de coordenadas base
    df['lat'] = df['CUIDAD'].str.strip().str.upper().map(lambda x: CITY_COORDS.get(x, [-1.8312, -78.1834])[0])
    df['lon'] = df['CUIDAD'].str.strip().str.upper().map(lambda x: CITY_COORDS.get(x, [-1.8312, -78.1834])[1])
    return df

try:
    df = load_data()

    # Filtros laterales
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/600/600258.png", width=100)
    st.sidebar.header("Control de Red")
    
    ciudades = sorted(df["CUIDAD"].unique())
    filtro = st.sidebar.multiselect("Filtrar Ciudades:", ciudades)
    
    df_final = df[df["CUIDAD"].isin(filtro)] if filtro else df

    # Mapa con agrupamiento (Spiderfy)
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")
    
    # El MarkerCluster con 'spiderfy_on_max_zoom' es la clave para ciudades con muchos talleres
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for i, row in df_final.iterrows():
        popup_html = f"""
        <div style='font-family: Arial; font-size: 12px; min-width: 150px;'>
            <b style='color:#3498DB;'>{row['NOMBRE DEL TALLER ']}</b><br>
            <b>Dirección:</b> {row['DIRECCION']}<br>
            <b>Contacto:</b> {row['NUMEROS DE CONTACTO (MINIMO 2)']}
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row['NOMBRE DEL TALLER '],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    # Métricas rápidas
    col1, col2 = st.columns(2)
    col1.metric("Total Talleres", len(df_final))
    col2.metric("Ciudades Cubiertas", len(df_final['CUIDAD'].unique()))

    st.dataframe(df_final, use_container_width=True)

except Exception as e:
    st.error(f"Error cargando el dashboard: {e}")
