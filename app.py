import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

st.set_page_config(page_title="Red Nacional TVS - Postventa", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Ubicaciones Exactas")

CENTROS_CIUDAD = {
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
    # Intenta cargar el CSV, primero busca el de tu formulario, si no, el que yo generé
    try:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    except:
        df = pd.read_csv("talleres_streamlit_completo.csv")
    
    # Limpia los espacios en los nombres de las columnas
    df.columns = df.columns.str.strip()
    
    # FUNCION SEGURA PARA OBTENER COORDENADAS
    def get_coords(row):
        # row.get() evita el "KeyError" si la columna no existe
        lat = row.get('lat')
        lon = row.get('lon')
        
        # Si existen y no están vacías, usa la ubicación exacta
        if pd.notnull(lat) and pd.notnull(lon):
            return float(lat), float(lon)
        
        # Si no existen, usa el centro de la ciudad de forma segura
        ciudad = str(row.get('CUIDAD', '')).strip().upper()
        return CENTROS_CIUDAD.get(ciudad, [-1.8312, -78.1834])

    # Aplicar la función a cada fila
    df['lat_final'], df['lon_final'] = zip(*df.apply(get_coords, axis=1))
    return df

try:
    df = load_data()

    # Panel lateral
    st.sidebar.header("Gestión de Red")
    ciudades = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades)

    df_filtered = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    # Crear Mapa
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for i, row in df_filtered.iterrows():
        # Extracción segura de datos para el popup
        nombre = row.get('NOMBRE DEL TALLER ', 'Taller Sin Nombre')
        direccion = row.get('DIRECCION', 'Sin dirección')
        contacto = row.get('NUMEROS DE CONTACTO (MINIMO 2)', 'N/A')
        responsable = row.get('PERSONA RESPONSABLE', 'N/A')

        popup_content = f"""
        <div style='font-family: Arial; font-size: 12px; width: 180px;'>
            <b style='color:#E67E22;'>{nombre}</b><br>
            <b>Dirección:</b> {direccion}<br>
            <b>Tel:</b> {contacto}<br>
            <b>Resp:</b> {responsable}
        </div>
        """
        
        folium.Marker(
            location=[row['lat_final'], row['lon_final']],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=nombre,
            icon=folium.Icon(color="orange", icon="wrench", prefix="fa")
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=600)

    st.write(f"### Detalle de la Red ({len(df_filtered)} talleres)")
    
    # Ocultar las columnas técnicas en la tabla
    columnas_a_ocultar = ['lat_final', 'lon_final', 'lat', 'lon']
    columnas_mostrar = [col for col in df_filtered.columns if col not in columnas_a_ocultar]
    st.dataframe(df_filtered[columnas_mostrar], use_container_width=True)

except Exception as e:
    st.error(f"Error en la carga de datos: {e}")
