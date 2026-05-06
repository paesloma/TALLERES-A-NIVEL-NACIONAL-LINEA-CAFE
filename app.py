import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Configuración profesional del dashboard
st.set_page_config(page_title="Red Nacional TVS - Postventa", layout="wide")

st.markdown("## 🛠️ Red Nacional de Servicios Técnicos - Ubicaciones Exactas")

# Coordenadas de respaldo (solo si el taller no tiene coordenadas propias)
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
    # Intentar cargar el archivo principal
    try:
        df = pd.read_csv("SERVICIOS TECNICOS TVS 2026.xlsx - Respuestas de formulario 1.csv")
    except:
        df = pd.read_csv("talleres_streamlit_completo.csv")
    
    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()
    
    # Lógica de Ubicación Exacta
    # Si las columnas 'lat' y 'lon' existen en tu archivo, las usará.
    # Si no existen o están vacías, usará el centro de la ciudad.
    def get_coords(row):
        if 'lat' in row and pd.notnull(row['lat']) and 'lon' in row and pd.notnull(row['lon']):
            return row['lat'], row['lon']
        
        ciudad = str(row['CUIDAD']).strip().upper()
        return CENTROS_CIUDAD.get(ciudad, [-1.8312, -78.1834])

    df['lat_final'], df['lon_final'] = zip(*df.apply(get_coords, axis=1))
    return df

try:
    df = load_data()

    # Panel lateral de control
    st.sidebar.header("Gestión de Red")
    ciudades = sorted(df["CUIDAD"].unique())
    seleccion = st.sidebar.multiselect("Filtrar por Ciudad:", ciudades)

    df_filtered = df[df["CUIDAD"].isin(seleccion)] if seleccion else df

    # Mapa con estilo industrial (CartoDB Dark)
    m = folium.Map(location=[-1.8312, -78.1834], zoom_start=7, tiles="CartoDB dark_matter")
    
    # MarkerCluster permite que, al hacer zoom, los talleres se separen físicamente
    marker_cluster = MarkerCluster(spiderfy_on_max_zoom=True).add_to(m)

    for i, row in df_filtered.iterrows():
        # Personalización del Popup con los datos de tu formulario
        popup_content = f"""
        <div style='font-family: Arial; font-size: 12px; width: 180px;'>
            <b style='color:#E67E22;'>{row['NOMBRE DEL TALLER ']}</b><br>
            <b>Dirección:</b> {row['DIRECCION']}<br>
            <b>Tel:</b> {row.get('NUMEROS DE CONTACTO (MINIMO 2)', 'N/A')}<br>
            <b>Resp:</b> {row['PERSONA RESPONSABLE']}
        </div>
        """
        
        folium.Marker(
            location=[row['lat_final'], row['lon_final']],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=row['NOMBRE DEL TALLER '],
            icon=folium.Icon(color="orange", icon="wrench", prefix="fa")
        ).add_to(marker_cluster)

    # Renderizar el mapa en la app
    st_folium(m, width="100%", height=600)

    # Mostrar la tabla de datos sincronizada
    st.write(f"### Detalle de la Red ({len(df_filtered)} talleres)")
    st.dataframe(df_filtered.drop(columns=['lat_final', 'lon_final']), use_container_width=True)

except Exception as e:
    st.error(f"Error en la carga: {e}")
