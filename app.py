import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuración de la interfaz
st.set_page_config(page_title="Red Nacional TVS 2026", layout="wide")

st.title("🛠️ Red Nacional de Talleres - Postventa")
st.markdown("Visualización geográfica de servicios técnicos autorizados.")

# Cargar los 26 talleres
@st.cache_data
def load_data():
    df = pd.read_csv("talleres_streamlit_completo.csv")
    return df

df = load_data()

# Filtros laterales
st.sidebar.header("Filtros de Búsqueda")
ciudad_filtro = st.sidebar.multiselect("Filtrar por Ciudad:", options=sorted(df["CUIDAD"].unique()))

if ciudad_filtro:
    df = df[df["CUIDAD"].isin(ciudad_filtro)]

# Crear mapa estilo Dark Mode (como tu referencia)
m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

# Agregar los 26 pines
for i, row in df.iterrows():
    # Personalización del globo de información (Popup)
    html = f"""
    <div style="font-family: sans-serif; font-size: 12px;">
        <h4 style="margin-bottom:5px;">{row['NOMBRE DEL TALLER']}</h4>
        <b>Ciudad:</b> {row['CUIDAD']}<br>
        <b>Dirección:</b> {row['DIRECCION']}<br>
        <b>Teléfono:</b> {row['NUMEROS DE CONTACTO']}<br>
        <b>Responsable:</b> {row['PERSONA RESPONSABLE']}
    </div>
    """
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=folium.Popup(html, max_width=300),
        tooltip=row['NOMBRE DEL TALLER'],
        icon=folium.Icon(color="blue", icon="wrench", prefix="fa")
    ).add_to(m)

# Renderizar mapa
st_folium(m, width="100%", height=600)

# Tabla de datos interactiva abajo
st.subheader("Listado Detallado")
st.dataframe(df, use_container_width=True)
