import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Población Argentina Pro", layout="wide")

# Estilo CSS para mejorar la apariencia de las métricas
st.markdown("""
    <style>
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4f8bf9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GENERACIÓN DE DATOS (Dataset con coordenadas) ---
@st.cache_data # Esto hace que la app sea más rápida
def crear_dataset():
    años = list(range(1950, 2027))
    provincias_info = {
        "Buenos Aires": {"lat": -34.6037, "lon": -58.3816, "base": 15000000},
        "Córdoba": {"lat": -31.4135, "lon": -64.1811, "base": 3800000},
        "Mendoza": {"lat": -32.8895, "lon": -68.8458, "base": 2000000},
        "Misiones": {"lat": -27.3671, "lon": -55.8961, "base": 1300000},
        "Chubut": {"lat": -43.3002, "lon": -65.1023, "base": 600000}
    }
    lista_datos = []
    for prov, info in provincias_info.items():
        for i, año in enumerate(años):
            # Simulación de crecimiento demográfico
            factor = 1 + (año - 2026) * 0.012 
            poblacion = int(info["base"] * max(0.2, factor))
            lista_datos.append({
                "Año": año, "Provincia": prov, "Población": poblacion,
                "Lat": info["lat"], "Lon": info["lon"]
            })
    return pd.DataFrame(lista_datos)

df = crear_dataset()

# --- 3. BARRA LATERAL (Panel de Control) ---
st.sidebar.title("🎮 Panel de Control")
st.sidebar.markdown("Usa los controles para filtrar la información.")

año_selec = st.sidebar.slider("Seleccioná el Año:", 1950, 2026, 2026)
provincias_selec = st.sidebar.multiselect(
    "Filtrar Provincias:", 
    options=df["Provincia"].unique(), 
    default=df["Provincia"].unique()
)

# Filtramos los datos según la selección
df_filtrado = df[(df["Año"] == año_selec) & (df["Provincia"].isin(provincias_selec))]

# --- 4. TÍTULO Y MÉTRICAS PRINCIPALES ---
st.title("🇦🇷 Dashboard de Población Argentina")
st.subheader(f"Estadísticas Generales - Año {año_selec}")

# Creamos 3 columnas para las métricas
m1, m2, m3 = st.columns(3)
pob_total = df_filtrado["Población"].sum()
m1.metric("Población Total", f"{pob_total:,}")
m2.metric("Provincias Activas", len(provincias_selec))
m3.metric("Fuente de datos", "Simulación INDEC")

st.divider()

# --- 5. SECCIÓN DE MAPA Y TORTA (En dos columnas) ---
col_mapa, col_torta = st.columns([2, 1])

with col_mapa:
    st.markdown("### 🗺️ Ubicación Geográfica")
    fig_mapa = px.scatter_geo(
        df_filtrado, lat="Lat", lon="Lon", size="Población", color="Provincia",
        hover_name="Provincia", scope="south america", template="plotly_dark",
        size_max=40
    )
    # Configuración para que el mapa se vea profesional y centrado en Argentina
    fig_mapa.update_geos(
        fitbounds="locations", visible=True, showcountries=True,
        countrycolor="RebeccaPurple", showland=True, landcolor="#242424",
        showocean=True, oceancolor="#0e1117"
    )
    fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_mapa, use_container_width=True)

with col_torta:
    st.markdown("### 🍰 Distribución %")
    fig_torta = px.pie(
        df_filtrado, values="Población", names="Provincia", 
        hole=0.4, template="plotly_dark"
    )
    st.plotly_chart(fig_torta, use_container_width=True)

# --- 6. GRÁFICO DE LÍNEAS (Evolución histórica) ---
st.divider()
st.markdown("### 📈 Tendencia Histórica (1950 - 2026)")
df_historia = df[df["Provincia"].isin(provincias_selec)]
fig_lineas = px.line(
    df_historia, x="Año", y="Población", color="Provincia",
    template="plotly_dark", markers=True
)
# Agregamos una línea vertical en el año que el usuario eligió en el slider
fig_lineas.add_vline(x=año_selec, line_dash="dash", line_color="yellow")
st.plotly_chart(fig_lineas, use_container_width=True)

# --- 7. BOTÓN DE DESCARGA ---
csv = df_filtrado.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📩 Descargar Datos (CSV)",
    data=csv,
    file_name=f'poblacion_arg_{año_selec}.csv',
    mime='text/csv',
)