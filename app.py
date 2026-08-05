import streamlit as st
import pandas as pd
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Extractor de Datos", layout="wide")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

cliente = st.text_input("Nombre del Cliente")
pdf_2023 = st.file_uploader("Subir PDF 2023", type=["pdf"])
pdf_2024 = st.file_uploader("Subir PDF 2024", type=["pdf"])
pdf_2025 = st.file_uploader("Subir PDF 2025", type=["pdf"])

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

if st.button("Generar Archivo de Datos"):
    if not cliente:
        st.error("Ingresa el nombre del cliente")
    else:
        # Creamos un contenedor de datos (DataFrame)
        # Esto es mucho más seguro que editar el Excel directamente
        data_to_save = {}
        
        for anio, archivo in archivos.items():
            if archivo:
                datos = extraer_datos_de_pdf(archivo)
                for casilla, valor in datos.items():
                    # Guardamos el valor limpio
                    key = f"{anio}_{casilla}"
                    data_to_save[key] = valor
        
        # Convertimos a DataFrame para guardar en Excel fácilmente
        df = pd.DataFrame(list(data_to_save.items()), columns=['ID', 'Valor'])
        
        nombre_final = f"Datos_Exportados_{cliente.replace(' ', '_')}.xlsx"
        
        # Guardamos el archivo limpio (sin macros, sin listas, solo datos)
        df.to_excel(nombre_final, index=False)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Archivo de Datos", f, file_name=nombre_final)

if st.button("Limpiar"):
    st.session_state.clear()
    st.rerun()
