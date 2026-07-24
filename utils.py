import pdfplumber
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
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
                    row_limpia = [str(c).strip() for c in row if c is not None]
                    
                    for i, cell in enumerate(row_limpia):
                        if cell in MAPEO_CASILLAS:
                            for j in range(i + 1, len(row_limpia)):
                                val_candidato = row_limpia[j]
                                valor_limpio = limpiar_valor(val_candidato)
                                if val_candidato.replace('-','').replace('.','').replace(',','').isdigit():
                                    datos_extraidos[cell] = valor_limpio
                                    break # Pasamos a la siguiente casilla
    return datos_extraidos
