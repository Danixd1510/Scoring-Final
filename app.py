import streamlit as st
import openpyxl
from utils import extraer_datos_de_pdf
from mapping import MAPEO_CASILLAS

st.set_page_config(page_title="Scoring Financiero")
st.title("SACA TUS RATIOS RAPIDISIMOOOO")

# Solo nombre del cliente
cliente = st.text_input("Nombre del Cliente")

# Archivos opcionales
pdf_2023 = st.file_uploader("Subir DDJJ 2023")
pdf_2024 = st.file_uploader("Subir DDJJ 2024")
pdf_2025 = st.file_uploader("Subir DDJJ 2025")

archivos = {"2023": pdf_2023, "2024": pdf_2024, "2025": pdf_2025}

def limpiar_nombre(nombre):
    # Elimina puntos para dejar S.A.C -> SAC
    return nombre.replace(".", "")

if st.button("Generar Excel"):
    if not cliente:
        st.error("Por favor ingresa el nombre del cliente")
    else:
        wb = openpyxl.load_workbook("Scoring Final.xlsx")
        
        # Procesar archivos
        al_menos_uno = False
        for anio, archivo in archivos.items():
            if archivo and anio in wb.sheetnames:
                al_menos_uno = True
                ws = wb[anio]
                st.write(f"Datos extraídos del año {anio}:")
                st.write(datos)
                datos = extraer_datos_de_pdf(archivo)
                for casilla, valor in datos.items():
                    celda = MAPEO_CASILLAS.get(casilla)
                        st.write(
                            f"Año: {anio} | "
                            f"Código: {casilla} | "
                            f"Valor: {valor} | "
                            f"Celda destino: {celda}")
                    if celda and not str(ws[celda].value).startswith("="):
                        if valor != 0:
                            ws[celda] = valor
                            # Este es el formato contable que da ese estilo:
                            ws[celda].number_format = '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
                        else:
                            # Para que el cero también se vea como "-"
                            ws[celda] = 0
                            ws[celda].number_format = '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)'
        
        if not al_menos_uno:
            st.warning("No se subió ningún archivo, se descargará la plantilla vacía.")
            
        nombre_final = f"Scoring Final - {limpiar_nombre(cliente)}.xlsx"
        wb.save(nombre_final)
        
        with open(nombre_final, "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name=nombre_final)

# Botón de Refresh
if st.button("Limpiar"):
    st.session_state.clear()
    st.rerun()
