import pdfplumber
import re
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpieza: quitamos espacios, comas, y paréntesis para negativos
    clean = str(valor).strip().replace(' ', '').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Regex: Busca el código de 3 dígitos, espacios, y captura el número
        for code in MAPEO_CASILLAS.keys():
            # Busca el código, espacios, y captura caracteres numéricos/símbolos
            pattern = rf"{code}\s+([\d\.\,\(\)\-\s]+)"
            match = re.search(pattern, full_text)
            if match:
                datos_extraidos[code] = limpiar_valor(match.group(1))
    return datos_extraidos
