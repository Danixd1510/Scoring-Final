import streamlit as st
import pandas as pd
from utils import extraer_datos_de_pdf
from structure import BALANCE_DATA, RESULTADOS_DATA

st.set_page_config(page_title="Scoring Financiero", layout="wide")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

def formato_excel(valor):
    if valor == 0: return "S/ -"
    return f"S/ {valor:,.2f}"

def generar_tabla(datos, estructura):
    tabla_data = []
    for cod, nombre in estructura.items():
        val = datos.get(cod, 0)
        tabla_data.append({"Cuenta": nombre, "Valor": formato_excel(val)})
    return pd.DataFrame(tabla_data)

# Pestañas
tab_2023, tab_2024, tab_2025 = st.tabs(["2023", "2024", "2025"])
pestanas = {"2023": tab_2023, "2024": tab_2024, "2025": tab_2025}

for anio, tab in pestanas.items():
    with tab:
        archivo = st.file_uploader(f"Subir PDF {anio}", type=["pdf"], key=f"up_{anio}")
        if archivo:
            datos = extraer_datos_de_pdf(archivo)
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Balance General")
                st.table(generar_tabla(datos, BALANCE_DATA))
            with c2:
                st.subheader("Estado de Resultados")
                st.table(generar_tabla(datos, RESULTADOS_DATA))
