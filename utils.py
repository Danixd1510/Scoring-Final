import pdfplumber
import re
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpieza: quitamos comas, espacios, paréntesis para negativos
    val_str = str(valor).strip().replace('(', '-').replace(')', '').replace(',', '').replace(' ', '')
    try:
        return float(val_str)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            # Leemos TODO el texto de la página de golpe
            text = page.extract_text()
            if not text: continue
            
            # Buscamos el patrón: 3 dígitos (código), espacio(s), luego números/símbolos
            # Esto ignora si es tabla o no, solo busca el texto
            patrones = re.findall(r'(\d{3})\s+([\d\.\,\(\)\s]+)', text)
            
            for code, value in patrones:
                if code in MAPEO_CASILLAS:
                    # Si ya encontramos un valor para este código, no lo sobrescribimos 
                    # (o si prefieres, se queda el último encontrado)
                    datos_extraidos[code] = limpiar_valor(value)
                    
    return datos_extraidos
