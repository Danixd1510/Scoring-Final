import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Automático")

# Inicialización de estado para limpiar campos
if 'cliente' not in st.session_state: st.session_state.cliente = ""
if 'ruc' not in st.session_state: st.session_state.ruc = ""

st.title("Generador de Scoring Financiero")

cliente = st.text_input("Nombre del Cliente", key="cliente")
ruc = st.text_input("RUC", key="ruc")
fecha = st.text_input("Fecha Inicio (dd/mm/aaaa)")
infocorp = st.number_input("Score Infocorp", min_value=0, max_value=999)

# Archivos opcionales
pdf_2023 = st.file_uploader("Subir PDF 2023")
pdf_2024 = st.file_uploader("Subir PDF 2024")
pdf_2025 = st.file_uploader("Subir PDF 2025")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        # Escribir Cabecera
        if "SCORING_FINAL" in wb.sheetnames:
            ws_f = wb["SCORING_FINAL"]
            ws_f["C2"] = limpiar_nombre(cliente)
            ws_f["C3"] = ruc
            ws_f["C4"] = fecha
            ws_f["D4"] = infocorp
        
        # Procesar
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    if celda and not str(ws[celda].value).startswith("="):
                        if valor != 0:
                            ws[celda] = valor
                            ws[celda].number_format = '_("S/"* #,##0.00_);_("S/"* (#,##0.00);_("S/"* "-"??_);_(@_)'
                        else:
                            ws[celda] = ""

        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)

# Botón de Refresh
if st.button("Limpiar / Nuevo Cliente"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()
