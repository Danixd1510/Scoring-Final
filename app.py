import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Automático")
st.title("Generador de Scoring Financiero")

# Datos básicos
cliente = st.text_input("Nombre del Cliente")
ruc = st.text_input("RUC")
# Cambiado a text_input para escritura manual
fecha_inicio = st.text_input("Fecha de Inicio (dd/mm/aaaa)", "01/01/2020")

archivos = {
    "2023": st.file_uploader("Subir DJ 2023", type="pdf"),
    "2024": st.file_uploader("Subir DJ 2024", type="pdf"),
    "2025": st.file_uploader("Subir DJ 2025", type="pdf")
}

if st.button("Generar y Descargar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # 1. Escribir Datos de Cabecera
        if "SCORING_FINAL" in wb.sheetnames:
            ws_final = wb["SCORING_FINAL"]
            ws_final["C2"] = cliente
            ws_final["C3"] = ruc
            ws_final["C4"] = fecha_inicio
        
        # 2. Procesar Estados Financieros con Formato
        for anio, archivo in archivos.items():
            if archivo:
                datos = extraer_datos_de_pdf(archivo)
                if anio in wb.sheetnames:
                    ws = wb[anio]
                    for casilla, valor in datos.items():
                        celda = MAPEO_CASILLAS[casilla]
                        ws[celda] = valor
                        ws[celda].number_format = '#,##0.00'
        
        # Guardar y preparar descarga
        nombre_salida = f"Scoring_Final_{cliente.replace(' ', '_')}.xlsx"
        wb.save(nombre_salida)
        
        with open(nombre_salida, "rb") as f:
            st.download_button(
                label="Descargar Scoring",
                data=f,
                file_name=nombre_salida,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
