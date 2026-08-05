import streamlit as st
import openpyxl
import os
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# CAMBIO AQUÍ: Ahora busca el archivo con extensión .xlsm
ARCHIVO_TEMPLATE = "Scoring Final.xlsm"

cliente = st.text_input("Nombre del Cliente")
pdf_2023 = st.file_uploader("Subir PDF 2023 (Opcional)")
pdf_2024 = st.file_uploader("Subir PDF 2024 (Opcional)")
pdf_2025 = st.file_uploader("Subir PDF 2025 (Opcional)")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    elif not os.path.exists(ARCHIVO_TEMPLATE):
        st.error(f"Error: El archivo '{ARCHIVO_TEMPLATE}' no se encuentra en la raíz.")
    else:
        # Cargamos manteniendo macros y estructuras (keep_vba=True)
        wb = openpyxl.load_workbook("Scoring Final.xlsm", keep_vba=True, keep_links=True, data_only=False)
        
        # Procesar archivos
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    if celda:
                        # Protección: No tocar celdas con fórmulas
                        if str(ws[celda].value).startswith("="):
                            continue
                        
                        # Escribir valor con formato contable
                        ws[celda] = valor
                        ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
        
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsm"
        wb.save(nombre_final)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)

if st.button("Limpiar / Nuevo Cliente"):
    st.session_state.clear()
    st.rerun()
