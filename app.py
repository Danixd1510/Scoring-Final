import streamlit as st
import openpyxl
import os # Importante para verificar si el archivo existe
from utils import extraer_datos_de_pdf, extraer_ficha_ruc, extraer_reporte_tributario
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero", layout="wide")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# --- SECCIÓN 1: VISTA EN PANTALLA ---
col1, col2 = st.columns(2)
ficha_file = col1.file_uploader("Subir Ficha RUC", type=["pdf"])
reporte_file = col2.file_uploader("Subir Reporte Tributario", type=["pdf"])

if ficha_file:
    info = extraer_ficha_ruc(ficha_file)
    st.success(f"**Empresa:** {info['Nombre']} | **RUC:** {info['RUC']} | **Inicio:** {info['Inicio']}")

if reporte_file:
    ventas, mes = extraer_reporte_tributario(reporte_file)
    st.info(f"**Ventas Totales:** S/ {ventas:,.2f} | **Mes detectado:** {mes}")

st.divider()

# --- SECCIÓN 2: GENERACIÓN EXCEL ---
st.header("Generar Reporte de Ratios")
cliente = st.text_input("Nombre del Cliente")
pdf_2023 = st.file_uploader("Subir PDF 2023")
pdf_2024 = st.file_uploader("Subir PDF 2024")
pdf_2025 = st.file_uploader("Subir PDF 2025")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        # VERIFICACIÓN DE SEGURIDAD: Comprobar si el archivo existe en el servidor
        if not os.path.exists("Scoring Final.xlsx"):
            st.error("Error crítico: No se encuentra 'Scoring Final.xlsx' en el servidor. Asegúrate de que el archivo esté en la raíz de tu repositorio de GitHub.")
        else:
            try:
                wb = openpyxl.load_workbook("Scoring Final.xlsx")
                
                for anio, archivo in archivos.items():
                    if archivo and anio in wb.sheetnames:
                        ws = wb[anio]
                        datos = extraer_datos_de_pdf(archivo)
                        
                        for casilla, valor in datos.items():
                            celda = MAPEO_CASILLAS.get(casilla)
                            if celda:
                                if str(ws[celda].value).startswith("="):
                                    continue
                                ws[celda] = valor
                                ws[celda].number_format = '_(* #,##0.00_);_(* -#,##0.00_);_(* "-"??_);_(@_)'
                
                nombre_final = f"Scoring Final - {cliente.replace('.', '')}.xlsx"
                wb.save(nombre_final)
                with open(nombre_final, "rb") as f:
                    st.download_button("📥 Descargar Excel", f, file_name=nombre_final)
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

if st.button("Limpiar / Nuevo Cliente"):
    st.session_state.clear()
    st.rerun()
