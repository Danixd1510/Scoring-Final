import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# Campos de entrada
cliente = st.text_input("Nombre del Cliente")

# Archivos opcionales
pdf_2023 = st.file_uploader("Subir PDF 2023 (Opcional)")
pdf_2024 = st.file_uploader("Subir PDF 2024 (Opcional)")
pdf_2025 = st.file_uploader("Subir PDF 2025 (Opcional)")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        # Cargamos el template original
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # Procesar solo las pestañas de años
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    
                    if celda:
                        # Protección: No tocar celdas con fórmulas
                        celda_val = ws[celda].value
                        if celda_val is not None and str(celda_val).startswith("="):
                            continue
                            
                        # Escribir valor con formato contable (con guion, sin paréntesis)
                        ws[celda] = valor
                        ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
        
        # Guardar archivo
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        
        # Botón de descarga
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)

if st.button("Limpiar / Nuevo Cliente"):
    st.session_state.clear()
    st.rerun()
