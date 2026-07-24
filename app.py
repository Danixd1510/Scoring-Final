import streamlit as st
import pandas as pd
from utils import extraer_datos_de_pdf

st.set_page_config(page_title="Scoring Financiero", layout="wide")
st.title("📊 SACA TUS RATIOS RAPIDISIMOOOO")

# Definimos las estructuras directamente aquí para evitar errores de importación
BALANCE_DATA = {
    "359": "Efectivo y equivalentes", "361": "Ctas. por cobrar comerciales - terc.",
    "364": "Ctas. por cobrar diversas - terceros", "366": "Serv. contratados por anticipado",
    "368": "Mercaderías", "373": "Materias aux, suministros y repuestos",
    "381": "Activos por derecho de uso (2)", "382": "Propiedades, planta y equipo",
    "383": "Depreciación de 1,2 y PPE acumulados", "388": "Activo diferido",
    "401": "Sobregiros bancarios", "402": "Trib. y aport. por pagar",
    "404": "Ctas. por pagar comerciales - terceros", "409": "Obligaciones financieras",
    "410": "Provisiones", "414": "Capital", "421": "Resultados acumulados positivos",
    "423": "Utilidad del ejercicio"
}

RESULTADOS_DATA = {
    "461": "Ventas netas o ing por servicios", "462": "Desc , rebajas y bonif concedidas",
    "464": "Costo de ventas", "466": "Resultado bruto Utilidad",
    "468": "Gastos de ventas", "469": "Gastos de administración",
    "470": "Resultado de operación utilidad", "472": "Gastos financieros",
    "473": "Ingresos financieros gravados", "475": "Otros ingresos gravados",
    "490": "Impuesto a la renta", "492": "Resultado del ejercicio"
}

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
