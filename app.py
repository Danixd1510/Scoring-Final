import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.title("Generador de Scoring Financiero")

# Datos básicos
cliente = st.text_input("Nombre del Cliente")
ruc = st.text_input("RUC")
fecha_inicio = st.date_input("Fecha de Inicio de Actividad")
infocorp = st.number_input("Score Infocorp", min_value=0, max_value=999)

archivos = {
    "2023": st.file_uploader("Subir DJ 2023", type="pdf"),
    "2024": st.file_uploader("Subir DJ 2024", type="pdf"),
    "2025": st.file_uploader("Subir DJ 2025", type="pdf")
}

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # 1. Escribir Datos de Cabecera en SCORING_FINAL
        if "SCORING_FINAL" in wb.sheetnames:
            ws_final = wb["SCORING_FINAL"]
            ws_final["C2"] = cliente
            ws_final["C3"] = ruc
            ws_final["C4"] = str(fecha_inicio)
        
        # 2. Procesar los estados financieros
        for anio, archivo in archivos.items():
            if archivo:
                datos = extraer_datos_de_pdf(archivo)
                if anio in wb.sheetnames:
                    ws = wb[anio]
                    for casilla, valor in datos.items():
                        celda = MAPEO_CASILLAS[casilla]
                        ws[celda] = valor
        
        nombre_salida = f"Scoring Final - {cliente.replace(' ', '_')}.xlsx"
        wb.save(nombre_salida)
        
        with open(nombre_salida, "rb") as f:
            st.download_button("Descargar Excel Final", f, file_name=nombre_salida)
