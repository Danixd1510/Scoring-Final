import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# --- Inputs ---
cliente = st.text_input("Nombre del Cliente")

# --- Archivos ---
pdf_2023 = st.file_uploader("Subir PDF 2023 (Opcional)")
pdf_2024 = st.file_uploader("Subir PDF 2024 (Opcional)")
pdf_2025 = st.file_uploader("Subir PDF 2025 (Opcional)")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    return nombre.replace(".", "")

# --- Lógica ---
if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        # Cargamos el template
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # Escribimos el nombre del cliente en la hoja SCORING_FINAL
        if "SCORING_FINAL" in wb.sheetnames:
            ws_final = wb["SCORING_FINAL"]
            ws_final["C2"] = limpiar_nombre(cliente)
        
        # Procesamos los años
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                ws = wb[anio]
                datos = extraer_datos_de_pdf(archivo)
                
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                    
                    if celda:
                        # PROTECCIÓN:
                        # 1. No escribir si tiene fórmula
                        # 2. No escribir si tiene validación (listas)
                        if ws[celda].data_type == 'f' or ws[celda].data_validation:
                            continue
                            
                        # Si es un número válido, escribimos
                        if valor != 0:
                            ws[celda] = valor
                            ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
                        else:
                            ws[celda] = 0
                            ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
        
        # Guardar
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)
