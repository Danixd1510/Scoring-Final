import pdfplumber
from mapping import MAPEO_CASILLAS

def limpiar_valor(valor):
    if valor is None: return 0
    # Limpiamos paréntesis (negativos) y comas
    val_str = str(valor).strip().replace('(', '-').replace(')', '').replace(',', '')
    try:
        # Intentamos convertir a número
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
                    # Convertimos toda la fila a texto limpio
                    row_data = [str(c).strip() if c is not None else "" for c in row]
                    
                    # Verificamos si en esta fila existe alguno de nuestros códigos
                    casilla_encontrada = None
                    for cell in row_data:
                        if cell in MAPEO_CASILLAS:
                            casilla_encontrada = cell
                            break
                    
                    # Si encontramos la casilla, buscamos el valor numérico en la MISMA FILA
                    if casilla_encontrada:
                        for item in row_data:
                            # Filtramos para asegurarnos que es un número (o valor contable)
                            if item and item != casilla_encontrada:
                                # Quitamos símbolos para verificar si es número
                                test_val = item.replace("-", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "")
                                if test_val.isdigit():
                                    datos_extraidos[casilla_encontrada] = limpiar_valor(item)
                                    break
    return datos_extraidos
