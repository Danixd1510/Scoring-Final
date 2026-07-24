import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Final")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

cliente = st.text_input("Nombre del Cliente")
pdf_2023 = st.file_uploader("Subir PDF 2023 (Opcional)")
pdf_2024 = st.file_uploader("Subir PDF 2024 (Opcional)")
pdf_2025 = st.file_uploader("Subir PDF 2025 (Opcional)")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        ws_final = wb["SCORING_FINAL"]
        ws_final["C2"] = limpiar_nombre(cliente)
        
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    if celda and not str(ws[celda].value).startswith("="):
                        if valor != 0:
                            ws[celda] = valor
                            # Este es el formato contable que da ese estilo:
                            ws[celda].number_format = '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
                        else:
                            # Para que el cero también se vea como "-"
                            ws[celda] = 0
                            ws[celda].number_format = '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
        
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)

if st.button("Limpiar / Nuevo Cliente"):
    st.session_state.clear()
    st.rerun()
