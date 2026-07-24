import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")

st.title("SACA TUS RATIOS RAPIDISIMOOOO")

cliente = st.text_input("Nombre del Cliente")

pdf_2023 = st.file_uploader("Subir DDJJ 2023", type=["pdf"])
pdf_2024 = st.file_uploader("Subir DDJJ 2024", type=["pdf"])
pdf_2025 = st.file_uploader("Subir DDJJ 2025", type=["pdf"])

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        al_menos_uno = False

        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                al_menos_uno = True
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    if celda and not str(ws[celda].value).startswith("="):
                        if valor != 0:
                            ws[celda] = valor
                            ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
                        else:
                            ws[celda] = 0
                            ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'

        if not al_menos_uno:
            st.warning("No se subió ningún archivo, se descargará la plantilla vacía.")

        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)

        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)
