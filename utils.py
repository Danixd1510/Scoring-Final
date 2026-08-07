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

def extraer_ficha_ruc(pdf_path):
    info = {"RUC": "-", "Nombre": "-", "Inicio": "-"}
    with pdfplumber.open(pdf_path) as pdf:
        texts = []
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texts.append(t)
        text = "\n".join(texts)

        ruc_match = re.search(r"\bRUC\b[\s:\-]*([0-9]{11})", text, flags=re.IGNORECASE)
        if not ruc_match:
            ruc_match = re.search(r"FICHA\s+RUC[\s:\-]*([0-9]{11})", text, flags=re.IGNORECASE)
        if ruc_match:
            info["RUC"] = ruc_match.group(1)

        nombre_match = re.search(r"(RAZON SOCIAL|APELLIDOS Y NOMBRES|NOMBRE O RAZON SOCIAL)[\s:\-]*([^\n\r]+)", text, flags=re.IGNORECASE)
        if nombre_match:
            info["Nombre"] = nombre_match.group(2).strip()

        fecha_match = re.search(r"(FECHA DE INICIO DE ACTIVIDADES|FECHA DE INICIO)[\s:\-]*([0-3]?\d[\/\-][0-1]?\d[\/\-][12]\d{3})", text, flags=re.IGNORECASE)
        if fecha_match:
            info["Inicio"] = fecha_match.group(2).strip()
        else:
            fecha_match2 = re.search(r"([12]\d{3}[\/\-][0-1]?\d[\/\-][0-3]?\d)", text)
            if fecha_match2:
                info["Inicio"] = fecha_match2.group(1)

    return info

def extraer_reporte_tributario(pdf_path, debug=False):
    """
    Extrae el total de ventas acumulado hasta el último mes con actividad
    y el número del último mes (1-12).
    Si debug=True, devuelve (total_ventas, ultimo_mes, trace) donde trace es info de diagnóstico.
    """
    meses_map = {
        "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4, "MAYO": 5,
        "JUNIO": 6, "JULIO": 7, "AGOSTO": 8, "SETIEMBRE": 9, "SEPTIEMBRE": 9,
        "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
    }

    total_ventas = 0.0
    ultimo_mes = 0
    trace = {"candidatas": [], "meses_encontrados": []}

    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        page_text = (page.extract_text() or "").upper()

        tables = []
        try:
            ts = page.extract_tables()
            if ts:
                tables.extend(ts)
        except:
            pass
        try:
            t = page.extract_table()
            if t:
                tables.append(t)
        except:
            pass

        def norm(s):
            return "" if s is None else re.sub(r"\s+", " ", str(s).strip()).upper()

        candidates = []
        for ti, table in enumerate(tables):
            table_text = " ".join([norm(cell) for row in table for cell in (row or []) if cell])
            has_month = any(m in table_text for m in meses_map.keys())
            has_ventas = "VENTAS" in table_text
            has_corriente = "CORRIENTE" in table_text or "EJERCICIO CORRIENTE" in table_text or "EJERCICIO" in table_text

            if has_month and (has_ventas or has_corriente or ("2026" in table_text) or ("2025" in table_text)):
                candidates.append((ti, table, table_text, has_month, has_ventas, has_corriente))

        if not candidates:
            for ti, table in enumerate(tables):
                table_text = " ".join([norm(cell) for row in table for cell in (row or []) if cell])
                if any(m in table_text for m in meses_map.keys()):
                    candidates.append((ti, table, table_text, True, "VENTAS" in table_text, False))

        procesada = False
        for ti, table, table_text, has_month, has_ventas, has_corriente in candidates:
            if debug:
                trace["candidatas"].append({"index": ti, "table_text": table_text[:400], "has_ventas": has_ventas, "has_corriente": has_corriente})

            ventas_col = None
            header_candidates = table[:3] if len(table) >= 3 else table
            for row in header_candidates:
                for idx, cell in enumerate(row):
                    if cell and "VENTAS" in norm(cell):
                        ventas_col = idx
                        break
                if ventas_col is not None:
                    break
            if ventas_col is None:
                ventas_col = 1 if any(len(r) > 1 for r in table) else 0

            suma = 0.0
            local_ultimo = 0
            meses_encontrados = []
            for row in table:
                if not row:
                    continue
                mes_nombre = None
                for idx_check in range(0, min(3, len(row))):
                    c = row[idx_check]
                    if c:
                        cn = norm(c)
                        for mn in meses_map.keys():
                            # coincidencia flexible
                            if mn in cn.split() or cn.startswith(mn + " ") or cn == mn:
                                mes_nombre = mn
                                mes_col_idx = idx_check
                                break
                    if mes_nombre:
                        break

                if mes_nombre:
                    ventas_val_raw = None
                    if ventas_col < len(row) and row[ventas_col]:
                        ventas_val_raw = row[ventas_col]
                    else:
                        for j in range(mes_col_idx + 1, min(len(row), mes_col_idx + 5)):
                            if row[j] and not any(mn in norm(row[j]) for mn in meses_map.keys()):
                                ventas_val_raw = row[j]
                                break

                    if ventas_val_raw:
                        val = limpiar_valor(ventas_val_raw)
                        meses_encontrados.append((mes_nombre, val))
                        if val != 0.0:
                            suma += val
                            local_ultimo = max(local_ultimo, meses_map[mes_nombre])

            if meses_encontrados:
                total_ventas = suma
                ultimo_mes = local_ultimo
                trace["meses_encontrados"] = meses_encontrados
                procesada = True
                break

        if not procesada:
            m = re.search(r"TOTAL[^\d\-]*([0-9\.,\-\s]+)", page_text, flags=re.IGNORECASE)
            if m:
                total_ventas = limpiar_valor(m.group(1))
            ultimo = 0
            for mes_name, num in meses_map.items():
                if mes_name in page_text:
                    ultimo = max(ultimo, num)
            ultimo_mes = ultimo
            trace["fallback_total"] = total_ventas
            trace["fallback_ultimo_mes"] = ultimo_mes

    if debug:
        return total_ventas, ultimo_mes, trace
    return total_ventas, ultimo_mes
    
