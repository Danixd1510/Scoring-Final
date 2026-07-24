import streamlit as st
import pandas as pd
from utils import extraer_datos_de_pdf
from labels import ETIQUETAS

st.set_page_config(page_title="Extractor Financiero", layout="wide")
st.title("📊 Extractor de Datos Financieros SUNAT")

# Pestañas
tab1, tab2, tab3 = st.tabs(["2023", "2024", "2025"])
archivos = {"2023": tab1, "2024": tab2, "2025": tab3}

def procesar_y_mostrar(anio, tab_container):
    archivo = tab_container.file_uploader(f"Subir PDF {anio}", type=["pdf"], key=f"file_{anio}")
    if archivo:
        datos = extraer_datos_de_pdf(archivo)
        # Convertir a DataFrame legible
        data = [{"Casilla": k, "Cuenta": ETIQUETAS.get(k, "Otros"), "Valor": v} for k, v in datos.items()]
        df = pd.DataFrame(data)
        
        tab_container.dataframe(df, use_container_width=True)
        tab_container.success(f"Datos del {anio} cargados con éxito. Puedes copiar la tabla.")

# Procesar cada año
with tab1: procesar_y_mostrar("2023", tab1)
with tab2: procesar_y_mostrar("2024", tab2)
with tab3: procesar_y_mostrar("2025", tab3)

if st.button("Limpiar todo"):
    st.session_state.clear()
    st.rerun()
