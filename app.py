import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Automático")
st.title("Generador de Scoring Financiero")

cliente = st.text_input("Nombre del Cliente")
ruc = st.text_input("RUC")
fecha_inicio = st.text_input("Fecha Inicio (dd/mm/aaaa)", "01/01/2020")

archivos = {"2023": st.file_uploader("PDF 2023"), "2024": st.file_uploader("PDF 2024"), "2025": st.file_uploader("PDF 2025")}

def limpiar_nombre(nombre):
    # Elimina puntos para S.A.C -> SAC
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # 1. Cabecera (Limpiamos nombre)
        ws_final = wb["SCORING_FINAL"]
        ws_final["B2"] = limpiar_nombre(cliente)
        ws_final["B3"] = ruc
        ws_final["B4"] = fecha_inicio
        
        # 2. Procesar financieros
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    if celda:
                        # Saltar si tiene fórmula
                        if str(ws[celda].value).startswith("="):
                            continue
                        
                        if valor != 0:
                            ws[celda] = valor
                            ws[celda].number_format = '#,##0.00'
                        else:
                            ws[celda] = "" # Blanco si es 0
        
        nombre_final = f"Scoring Final {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)
