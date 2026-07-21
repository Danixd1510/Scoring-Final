import streamlit as st
import openpyxl
import re
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

def limpiar_nombre_archivo(nombre):
    return re.sub(r'[^\w\s]', '', nombre).replace('SA', 'SA').replace('SRL', 'SRL')

st.title("Generador de Scoring Financiero")

# Datos básicos
cliente = st.text_input("Nombre del Cliente")
ruc = st.text_input("RUC")

# Carga de archivos
archivos = {
    "2023": st.file_uploader("Subir DJ 2023", type="pdf"),
    "2024": st.file_uploader("Subir DJ 2024", type="pdf"),
    "2025": st.file_uploader("Subir DJ 2025", type="pdf")
}

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        # Cargar plantilla
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        for anio, archivo in archivos.items():
            if archivo:
                datos = extraer_datos_de_pdf(archivo)
                if anio in wb.sheetnames:
                    ws = wb[anio]
                    for casilla, valor in datos.items():
                        celda = MAPEO_CASILLAS[casilla]
                        ws[celda] = valor
                else:
                    st.warning(f"La hoja {anio} no existe en el Excel")
        
        nombre_salida = f"Scoring Final - {limpiar_nombre_archivo(cliente)}.xlsx"
        wb.save(nombre_salida)
        
        with open(nombre_salida, "rb") as f:
            st.download_button("Descargar Excel Final", f, file_name=nombre_salida)
