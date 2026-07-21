import pdfplumber
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    """Limpia valores tipo '(100)' a '-100'"""
    if valor is None: return 0
    val_str = str(valor).strip()
    val_str = val_str.replace('(', '-').replace(')', '').replace(',', '')
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
                    # Buscamos en las columnas donde están los códigos (usualmente col 1 y 4)
                    # Verifica si el valor de la celda es uno de los códigos de MAPEO
                    for i in range(len(row)):
                        if str(row[i]) in MAPEO_CASILLAS:
                            casilla = str(row[i])
                            valor = row[i+1] # El valor suele estar a la derecha
                            datos_extraidos[casilla] = limpiar_valor(valor)
    return datos_extraidos
