import pdfplumber
import re
import unicodedata
from mapping import MAPEO_CASILLAS

def normalize_text(s):
    if s is None:
        return ""
    s = str(s)
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.upper()
    s = re.sub(r"\s+", " ", s)
    return s

def limpiar_valor(valor):
    if valor is None:
        return 0.0
    s = str(valor).strip()
    if s == "":
        return 0.0

    negative = False
    if "(" in s and ")" in s:
        negative = True
        s = s.replace("(", "").replace(")", "")

    s = s.replace("\xa0", "").replace(" ", "")
    s = re.sub(r"[^0-9\.,\-]", "", s)

    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        if "," in s and s.count(",") == 1 and "." not in s:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "").replace(".", "")

    try:
        val = float(s)
    except:
        m = re.search(r"-?\d+(\.\d+)?", s)
        if m:
            try:
                val = float(m.group(0))
            except:
                return 0.0
        else:
            return 0.0

    if negative:
        val = -abs(val)
    return val

# -- extraer_datos_de_pdf y otras funciones que uses (mantenlas si ya las tienes) --
def extraer_datos_de_pdf(archivo_pdf):
    datos_extraidos = {}
    norm_to_key = {}
    for k in MAPEO_CASILLAS.keys():
        norm = normalize_text(k)
        norm_to_key[norm] = k

    with pdfplumber.open(archivo_pdf) as pdf:
        for page in pdf.pages:
            tables = []
            t = page.extract_table()
            if t:
                tables.append(t)
            try:
                ts = page.extract_tables()
                if ts:
                    tables.extend(ts)
            except:
                pass

            page_text = page.extract_text() or ""

            for table in tables:
                for row in table:
                    row_limpia = ["" if cell is None else str(cell).strip() for cell in row]
                    for i, cell in enumerate(row_limpia):
                        if not cell:
                            continue
                        if ":" in cell:
                            left, right = cell.split(":", 1)
                            norm_left = normalize_text(left)
                            if norm_left in norm_to_key:
                                key = norm_to_key[norm_left]
                                val = limpiar_valor(right)
                                datos_extraidos[key] = val
                                continue

                        norm = normalize_text(cell)
                        if norm in norm_to_key:
                            key = norm_to_key[norm]
                            valor_encontrado = None
                            for j in range(i + 1, min(len(row_limpia), i + 4)):
                                cand = row_limpia[j]
                                if cand and normalize_text(cand) not in norm_to_key:
                                    valor_encontrado = cand
                                    break
                            if valor_encontrado is None and re.search(r":\s*\S", cell):
                                parts = re.split(r":\s*", cell, maxsplit=1)
                                if len(parts) > 1:
                                    valor_encontrado = parts[1]
                            if valor_encontrado is not None:
                                datos_extraidos[key] = limpiar_valor(valor_encontrado)

            if not datos_extraidos and page_text:
                for k in MAPEO_CASILLAS.keys():
                    pattern = re.escape(k) + r"\s*[:\-]?\s*([^\n\r]+)"
                    m = re.search(pattern, page_text, flags=re.IGNORECASE)
                    if m:
                        val_raw = m.group(1).split("\n")[0].strip()
                        datos_extraidos[k] = limpiar_valor(val_raw)

    return datos_extraidos

# ---- nueva versión robusta de extraer_ficha_ruc con limpieza de nombre ----
def extraer_ficha_ruc(pdf_path):
    info = {"RUC": "-", "Nombre": "-", "Inicio": "-"}
    with pdfplumber.open(pdf_path) as pdf:
        texts = []
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texts.append(t)
        text = "\n".join(texts)

        # RUC: búsqueda tolerante
        ruc_match = re.search(r"\bRUC\b[\s:\-]*([0-9]{11})", text, flags=re.IGNORECASE)
        if not ruc_match:
            ruc_match = re.search(r"FICHA\s+RUC[\s:\-]*([0-9]{11})", text, flags=re.IGNORECASE)
        if ruc_match:
            info["RUC"] = ruc_match.group(1)

        # Nombre / Razón social: buscar varias etiquetas posibles
        nombre_match = re.search(r"(RAZON SOCIAL|APELLIDOS Y NOMBRES|NOMBRE O RAZON SOCIAL|EMPRESA|NOMBRE)[\s:\-]*([^\n\r]+)", text, flags=re.IGNORECASE)
        if nombre_match:
            raw_name = nombre_match.group(2).strip()
        else:
            # fallback: intentar capturar la línea que sigue a 'Razón Social' o 'Nombre'
            m = re.search(r"(Raz[oó]n Social|Apellidos y Nombres|Nombre)[\s:\-]*\n?\s*([^\n\r]+)", text, flags=re.IGNORECASE)
            raw_name = m.group(2).strip() if m else "-"

        # Normalizamos y limpiamos el nombre para quitar etiquetas sobrantes
        name = raw_name.strip()
        # Si hay dos puntos ':' en la cadena, tomar lo que esté después del último, porque a veces se captura la etiqueta
        if ":" in name:
            after_colon = name.split(":")[-1].strip()
            # si lo que queda parece un nombre razonable, lo usamos
            if len(after_colon) > 0 and len(after_colon) < len(name):
                name = after_colon

        # remover prefijos comunes que hayan quedado
        name = re.sub(r'^(EMPRESA|EMPRESA[:\s\-]*|RAZON SOCIAL[:\s\-]*|APELLIDOS Y NOMBRES[:\s\-]*|NOMBRE O RAZON SOCIAL[:\s\-]*|NOMBRE[:\s\-]*|O RAZON SOCIAL[:\s\-]*|Ó RAZON SOCIAL[:\s\-]*)', '', name, flags=re.IGNORECASE)
        # quitar comillas o caracteres raros iniciales
        name = re.sub(r'^[\s\-\:\"]+', '', name).strip()

        info["Nombre"] = name if name else "-"

        # Fecha de inicio: soportar varios formatos
        fecha_match = re.search(r"(FECHA DE INICIO DE ACTIVIDADES|FECHA DE INICIO)[\s:\-]*([0-3]?\d[\/\-][0-1]?\d[\/\-][12]\d{3})", text, flags=re.IGNORECASE)
        if fecha_match:
            info["Inicio"] = fecha_match.group(2).strip()
        else:
            fecha_match2 = re.search(r"([12]\d{3}[\/\-][0-1]?\d[\/\-][0-3]?\d)", text)
            if fecha_match2:
                info["Inicio"] = fecha_match2.group(1)

    return info
