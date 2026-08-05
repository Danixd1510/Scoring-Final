import pdfplumber
import re
from datetime import datetime
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpia: espacios, comas, paréntesis a guion
    # Ejemplo: "(1,234.00)" -> "-1234.00"
    clean = str(valor).strip().replace(' ', '').replace(',', '')
    if '(' in clean or ')' in clean:
        clean = '-' + clean.replace('(', '').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            # layout=True es vital: mantiene la estructura visual
            text = page.extract_text(layout=True)
            if not text: continue
            
            lineas = text.split('\n')
            for linea in lineas:
                # Buscamos cada código en la línea
                for code in MAPEO_CASILLAS.keys():
                    # Buscamos el código seguido de cualquier espacio y luego un número
                    # El regex busca: código, espacios, y cualquier secuencia de dígitos, puntos, menos o paréntesis
                    patron = rf"\b{code}\b\s+([-\d\.\,\(\)\s]+)"
                    match = re.search(patron, linea)
                    
                    if match:
                        valor_encontrado = match.group(1).strip()
                        # Solo asignamos si es un número real (que contenga al menos un dígito)
                        if any(c.isdigit() for c in valor_encontrado):
                            datos_extraidos[code] = limpiar_valor(valor_encontrado)
                            
    return datos_extraidos

def extraer_ficha_ruc(pdf_path):
    info = {"RUC": "-", "Nombre": "-", "Inicio": "-"}
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        # Regex para buscar datos
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
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                # Convertimos toda la tabla a texto para buscar el encabezado
                tabla_texto = " ".join([str(cell) for row in table for cell in row if cell])
                
                # FILTRO MÁGICO: Solo procesamos si la tabla menciona 2026
                if "2026" in tabla_texto:
                    total_ventas = 0
                    mes_detectado = 0
                    
                    for row in table:
                        # Saltar filas vacías
                        if not row or not row[0]: continue
                        
                        mes_raw = str(row[0]).strip().upper()
                        
                        # Si es un mes y tiene ventas, actualizamos el último mes detectado
                        if mes_raw in meses_map:
                            if row[1] and row[1].strip() != "":
                                mes_detectado = meses_map[mes_raw]
                        
                        # Si encontramos la fila de TOTAL, esa es la que queremos
                        if "TOTAL EJERCICIO" in mes_raw:
                            try:
                                total_ventas = float(str(row[1]).replace(',', '').strip())
                            except:
                                pass
                    
                    # Retornamos solo si encontramos datos en la tabla del 2026
                    return total_ventas, mes_detectado
    return 0, 0
