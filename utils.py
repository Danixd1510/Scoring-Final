import pymupdf4llm
import re
import tempfile
import os
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpiamos: espacios, comas, y paréntesis a negativos
    clean = str(valor).strip().replace(' ', '').replace(',', '').replace('(', '-').replace(')', '')
    try:
        return float(clean)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    # 1. Creamos un archivo temporal para que pymupdf4llm pueda leerlo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(archivo_pdf.read())
        tmp_path = tmp_file.name

    datos_extraidos = {}
    try:
        # 2. Convertimos el archivo temporal a Markdown
        md_text = pymupdf4llm.to_markdown(tmp_path)
        
        # 3. Buscamos en el texto Markdown
        for code in MAPEO_CASILLAS.keys():
            # Patrón para buscar | 359 | 214006 | o solo "359 214006"
            # Buscamos el código, separadores, y el valor
            patron = rf"\|\s*{code}\s*\|\s*([\d\.\,\(\)\-\s]+)\s*\|"
            match = re.search(patron, md_text)
            
            if match:
                datos_extraidos[code] = limpiar_valor(match.group(1))
            else:
                # Fallback por si el PDF no generó tabla Markdown bien
                patron_plano = rf"\b{code}\b\s+([\d\.\,\(\)\-\s]+)"
                match_plano = re.search(patron_plano, md_text)
                if match_plano:
                    datos_extraidos[code] = limpiar_valor(match_plano.group(1))
    finally:
        # 4. Borramos el archivo temporal para no llenar el servidor
        os.remove(tmp_path)
                    
    return datos_extraidos
