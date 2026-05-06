import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Red Nacional TVS", layout="wide")

st.title("🛠️ Red Nacional de Talleres con Direcciones Exactas")

@st.cache_data
def load_data():
    # Cargamos el CSV que subiste a GitHub
    df = pd.read_csv("talleres_streamlit_completo.csv")
    # Limpiamos espacios invisibles en los nombres de las columnas para evitar errores
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()

    # Filtro lateral usando el nombre exacto de tu columna 'CUIDAD'
    st.sidebar.header("Filtros")
    ciudades = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Seleccionar Ciudad:", ciudades)

    if seleccion:
        df = df[df["CUIDAD"].isin(seleccion)]

    # Crear el mapa (Estilo Oscuro)
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")

    for i, row in df.iterrows():
        # Usamos los nombres exactos detectados en tu archivo
        popup_info = f"""
        <div style='font-family: Arial; font-size: 12px;'>
            <b>Taller:</b> {row['NOMBRE DEL TALLER']}<br>
            <b>Dirección:</b> {row['DIRECCION']}<br>
            <b>Contacto:</b> {row['NUMEROS DE CONTACTO (MINIMO 2)']}
        </div>
        """
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=folium.Popup(popup_info, max_width=250),
            tooltip=row['NOMBRE DEL TALLER']
        ).add_to(m)

    st_folium(m, width="100%", height=550)
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.info("Asegúrate de que el archivo 'talleres_streamlit_completo.csv' esté en la misma carpeta que este script en GitHub.")
