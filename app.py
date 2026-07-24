import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# Campos de entrada
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
    else:
        # Cargamos el archivo template
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # 1. Escribir nombre en SCORING_FINAL (Solo tocamos C2)
        if "SCORING_FINAL" in wb.sheetnames:
            ws_final = wb["SCORING_FINAL"]
            ws_final["C2"] = limpiar_nombre(cliente)
        
        # 2. Procesar años (2023, 2024, 2025)
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    
                    if celda:
                        # PROTECCIÓN: Si la celda es fórmula, saltar
                        if ws[celda].data_type == 'f' or str(ws[celda].value).startswith("="):
                            continue
                            
                        # Escribir valor con formato contable (sin paréntesis)
                        ws[celda] = valor
                        ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
        
        # Guardar
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)
