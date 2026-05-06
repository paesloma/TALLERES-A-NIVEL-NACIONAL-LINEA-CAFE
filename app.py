import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster # <--- Nueva librería para agrupar

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.title("🛠️ Red Nacional de Talleres con Direcciones Exactas")

@st.cache_data
def load_data():
    df = pd.read_csv("talleres_streamlit_completo.csv")
    # Limpiamos espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # Filtro lateral
    st.sidebar.header("Filtros")
    ciudades = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Seleccionar Ciudad:", ciudades)

    if seleccion:
        df = df[df["CUIDAD"].isin(seleccion)]

    # Crear el mapa (Estilo Oscuro)
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    # CREAR EL CLUSTER: Agrupa los talleres y los despliega si están en la misma coordenada
    mc = MarkerCluster(spiderfy_on_click=True).add_to(m)

    for i, row in df.iterrows():
        popup_info = f"""
        <div style='font-family: Arial; font-size: 12px; min-width: 200px;'>
            <b style='color: #1F77B4;'>{row['NOMBRE DEL TALLER']}</b><br>
            <b>Dirección:</b> {row['DIRECCION']}<br>
            <b>Contacto:</b> {row['NUMEROS DE CONTACTO (MINIMO 2)']}
        </div>
        """
        
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_info, max_width=300),
            tooltip=row['NOMBRE DEL TALLER'],
            icon=folium.Icon(color="blue", icon="wrench", prefix="fa")
        ).add_to(mc) # <--- IMPORTANTE: Se agrega al cluster (mc), no al mapa directo

    # Renderizar el mapa en la app
    st_folium(m, width="100%", height=550)
    
    # Mostrar la tabla debajo
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
