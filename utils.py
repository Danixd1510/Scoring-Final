import pymupdf4llm
import re
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpieza: quitamos espacios, comas, y paréntesis a negativos
    clean = str(valor).strip().replace(' ', '').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    # Convertimos el PDF a Markdown
    # pymupdf4llm nos da un texto limpio y estructurado
    md_text = pymupdf4llm.to_markdown(archivo_pdf)
    
    datos_extraidos = {}
    
    # Buscamos en el texto Markdown
    for code in MAPEO_CASILLAS.keys():
        # Buscamos patrones típicos de tablas Markdown: | 359 | 214006 |
        # \|\s*{code}\s*\| captura el código entre tuberías
        # \s*([\d\.\,\(\)\-\s]+) captura el número que sigue
        patron = rf"\|\s*{code}\s*\|\s*([\d\.\,\(\)\-\s]+)\s*\|"
        match = re.search(patron, md_text)
        
        if match:
            datos_extraidos[code] = limpiar_valor(match.group(1))
        else:
            # Fallback: si no está en formato tabla, buscamos el código como texto plano
            # Busca: 359 (espacios) número
            patron_plano = rf"\b{code}\b\s+([\d\.\,\(\)\-\s]+)"
            match_plano = re.search(patron_plano, md_text)
            if match_plano:
                datos_extraidos[code] = limpiar_valor(match_plano.group(1))
                
    return datos_extraidos
