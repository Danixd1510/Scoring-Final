import pdfplumber
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpiamos caracteres extraños y paréntesis para negativos
    val_str = str(valor).strip().replace('(', '-').replace(')', '').replace(',', '')
    try:
        return float(val_str)
    except:
        return 0

def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    # Limpiamos la fila de Nones para poder iterar bien
                    row_limpia = [str(cell).strip() if cell is not None else "" for cell in row]
                    
                    # Buscamos la casilla en la fila
                    for i, cell in enumerate(row_limpia):
                        if cell in MAPEO_CASILLAS:
                            # SEGURIDAD: Solo intentamos leer el valor si existe una columna a la derecha
                            if i + 1 < len(row_limpia):
                                valor = row_limpia[i+1]
                                # Solo procesamos si el valor no está vacío
                                if valor:
                                    datos_extraidos[cell] = limpiar_valor(valor)
    return datos_extraidos
