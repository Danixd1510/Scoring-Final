import pdfplumber
import re
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    # Esto elimina puntos de miles, comas, y convierte paréntesis a negativo
    # También limpia espacios extraños
    if valor is None: return 0
    clean = valor.replace(' ', '').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        # Unimos todo el texto de todas las páginas
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        
        # Regex: busca código de 3 dígitos, luego busca el número a la derecha
        # Busca códigos como 359, 409, 490... y captura el valor numérico (incluyendo negativos)
        # Esto es muy flexible: encuentra el código y el primer número después de él.
        for code in MAPEO_CASILLAS.keys():
            # Patrón: el código, espacios, y un valor (posiblemente con paréntesis o guiones)
            # Ejemplo: "409 (espacios) 1951909"
            regex_pat = rf"{code}\s+([\d\.\,\(\)\-\s]+)"
            match = re.search(regex_pat, full_text)
            
            if match:
                valor_crudo = match.group(1)
                datos_extraidos[code] = limpiar_valor(valor_crudo)
                
    return datos_extraidos
