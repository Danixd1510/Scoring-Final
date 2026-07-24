import streamlit as st
from utils import extraer_datos_de_pdf
from structure import CUENTAS

st.set_page_config(page_title="Scoring Financiero", layout="wide")
st.title("📊 Vista de Datos Financieros")

# Subida de archivos
col_up1, col_up2, col_up3 = st.columns(3)
pdf_2023 = col_up1.file_uploader("PDF 2023")
pdf_2024 = col_up2.file_uploader("PDF 2024")
pdf_2025 = col_up3.file_uploader("PDF 2025")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def formato_contable(valor):
    if valor == 0: return "-"
    return f"{valor:,.2f}"

for anio, archivo in archivos.items():
    if archivo:
        st.subheader(f"Datos: {anio}")
        datos = extraer_datos_de_pdf(archivo)
        
        # Dividimos en dos columnas para el Activo y Pasivo/Patrimonio
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Activo")
            for cod, label, sec in CUENTAS:
                if sec == "Activo":
                    val = datos.get(cod, 0)
                    st.text(f"{label:<45} {formato_contable(val):>20}")
        
        with col2:
            st.markdown("### Pasivo y Patrimonio")
            for cod, label, sec in CUENTAS:
                if sec in ["Pasivo", "Patrimonio"]:
                    val = datos.get(cod, 0)
                    st.text(f"{label:<45} {formato_contable(val):>20}")
        st.divider()
