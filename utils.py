import pdfplumber
import re
from datetime import datetime
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    clean = str(valor).strip().replace(' ', '').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    row_limpia = [str(cell).strip() if cell is not None else "" for cell in row]
                    for i, cell in enumerate(row_limpia):
                        if cell in MAPEO_CASILLAS:
                            if i + 1 < len(row_limpia):
                                valor = row_limpia[i+1]
                                if valor:
                                    datos_extraidos[cell] = limpiar_valor(valor)
    return datos_extraidos

def extraer_ficha_ruc(pdf_path):
    info = {"RUC": "-", "Nombre": "-", "Inicio": "-"}
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        ruc_match = re.search(r'FICHA RUC\s*:\s*(\d{11})', text)
        nombre_match = re.search(r'Apellidos y Nombres ó Razón Social\s*:\s*(.*)', text)
        fecha_match = re.search(r'Fecha de Inicio de Actividades\s*:\s*(\d{2}/\d{2}/\d{4})', text)
        if ruc_match: info["RUC"] = ruc_match.group(1)
        if nombre_match: info["Nombre"] = nombre_match.group(1).strip()
        if fecha_match: info["Inicio"] = fecha_match.group(1)
    return info

def extraer_reporte_tributario(pdf_path):
    meses_map = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5,
        "JUNIO": 6, "JULIO": 7, "AGOSTO": 8, "SETIEMBRE": 9, 
        "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }
    total_ventas = 0
    ultimo_mes = 0
    with pdfplumber.open(pdf_path) as pdf:
        tables = pdf.pages[0].extract_tables()
        for table in tables:
            tabla_texto = " ".join([str(cell) for row in table for cell in row if cell])
            if "2026" in tabla_texto:
                for row in table:
                    if not row or row[0] is None: continue
                    mes_raw = str(row[0]).strip().upper()
                    if mes_raw in meses_map:
                        if row[1] and str(row[1]).replace(',','').replace('.','').isdigit():
                            ultimo_mes = meses_map[mes_raw]
                    elif "TOTAL" in mes_raw:
                        try:
                            total_ventas = float(str(row[1]).replace(',', '').strip())
                        except: pass
    return total_ventas, ultimo_mes
