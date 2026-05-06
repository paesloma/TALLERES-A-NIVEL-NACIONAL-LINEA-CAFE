import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Configuración de la página (Ancho completo)
st.set_page_config(page_title="Red Nacional de Talleres", layout="wide", page_icon="🛠️")

# Estilo personalizado para el título (similar a tu captura)
st.markdown("<h2 style='text-align: left;'>🛠️ Red Nacional de Talleres con Direcciones Exactas</h2>", unsafe_allow_index=True)

# 2. Cargar base de datos
@st.cache_data
def load_data():
    # Asegúrate de que el nombre coincida con el archivo que subas
    df = pd.read_csv("talleres_streamlit_completo.csv")
    return df

df = load_data()

# 3. Barra lateral para filtros
st.sidebar.header("Panel de Control")
ciudades = sorted(df["CUIDAD"].unique())
seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades)

if seleccion:
    df = df[df["CUIDAD"].isin(seleccion)]

# 4. Creación del Mapa (Estilo Oscuro como en tu imagen)
# Coordenadas iniciales centradas en Ecuador
m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

for i, row in df.iterrows():
    # Contenido del globo de información
    popup_info = f"""
    <div style='font-family: Arial; font-size: 12px; width: 200px;'>
        <h4 style='color: #2E86C1; margin-bottom: 5px;'>{row['NOMBRE DEL TALLER']}</h4>
        <b>Ciudad:</b> {row['CUIDAD']}<br>
        <b>Dirección:</b> {row['DIRECCION']}<br>
        <b>Contacto:</b> {row['NUMEROS DE CONTACTO']}<br>
        <b>Responsable:</b> {row['PERSONA RESPONSABLE']}
    </div>
    """
    
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(popup_info, max_width=250),
        tooltip=f"{row['NOMBRE DEL TALLER']} ({row['CUIDAD']})",
        icon=folium.Icon(color="info", icon="wrench", prefix="fa")
    ).add_to(m)

# 5. Desplegar el mapa
st_folium(m, width="100%", height=550)

# 6. Tabla de datos inferior
with st.expander("Ver base de datos completa"):
    st.dataframe(df, use_container_width=True)
