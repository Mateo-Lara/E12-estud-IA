#!/usr/bin/env python3
"""Convierte un CSV descargado a mano en un bruto como el que guarda extraer.py.

Uso (en la carpeta de tu repositorio):
    python3 csv_a_bruto.py ARCHIVO.csv CONJUNTO ESPERADAS

  ARCHIVO.csv  el CSV que descargaron (puede estar en la raíz del repo)
  CONJUNTO     un nombre corto, sin espacios y que empiece por letra (por ejemplo cartera):
               será el nombre de la tabla en BigQuery
  ESPERADAS    cuántas filas dice la fuente que hay (con su filtro). Es la cifra de control.

Qué hace:
  1. Lee el CSV (UTF-8 o el de Excel; separado por coma, punto y coma o tabulador).
  2. Cuenta las filas y las compara con ESPERADAS. Si no cuadra, no guarda nada.
  3. Guarda data/raw/<conjunto>_<fecha>.json: todo como texto, los vacíos como nulos,
     y una columna fila_csv con el número de la fila (su identificador en el bruto).
  4. Anota la corrida en conteos.csv, como extraer.py. Después sigue preparar_carga.py.

No cambia ningún valor. Solo usa la biblioteca estándar de Python.
"""
import csv
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

COLOMBIA = timezone(timedelta(hours=-5))


def miles(n):
    return f"{n:,}".replace(",", ".")


def nombre_bq(c):
    n = re.sub(r"[^0-9a-zA-Z_]", "_", c.strip()).lower()
    return "c_" + n if not n or n[0].isdigit() else n


def main():
    if len(sys.argv) != 4:
        sys.exit("Uso: python3 csv_a_bruto.py ARCHIVO.csv CONJUNTO ESPERADAS")
    origen, conjunto, esperadas_txt = sys.argv[1:]
    if not os.path.exists(origen):
        sys.exit(f"ALTO: no existe {origen}. Revisa el nombre con ls.")
    try:
        esperadas = int(re.sub(r"[.,\s]", "", esperadas_txt))
    except ValueError:
        sys.exit("ALTO: ESPERADAS tiene que ser un número (por ejemplo 15019).")
    conjunto = re.sub(r"[^0-9a-zA-Z_-]", "_", conjunto.strip()).lower()
    if not conjunto or not conjunto[0].isalpha():
        conjunto = "f_" + conjunto  # en BigQuery, mejor que la tabla empiece por letra

    datos = open(origen, "rb").read()
    for cod in ("utf-8-sig", "cp1252"):
        try:
            texto = datos.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    primera = texto.splitlines()[0] if texto else ""
    sep = max([",", ";", "\t"], key=primera.count)
    filas_csv = list(csv.reader(io.StringIO(texto, newline=""), delimiter=sep))
    if not filas_csv:
        sys.exit("ALTO: el CSV está vacío.")

    # Encabezados: sin vacíos y sin dos que BigQuery vería con el mismo nombre.
    columnas, vistos = [], set()
    for i, h in enumerate(filas_csv[0], 1):
        h = h.strip() or f"columna_{i}"
        base, k = h, 2
        while nombre_bq(h) in vistos or nombre_bq(h) == "fila_csv":
            h, k = f"{base}_{k}", k + 1
        vistos.add(nombre_bq(h))
        columnas.append(h)

    filas, vacias = [], 0
    for n, r in enumerate(filas_csv[1:], 2):
        if not any(v.strip() for v in r):
            vacias += 1
            continue
        if len(r) > len(columnas):
            if any(v.strip() for v in r[len(columnas):]):
                sys.exit(f"ALTO: la línea {n} trae más valores que encabezados. "
                         f"¿Hay un separador ({sep!r}) dentro de un valor sin comillas?")
            r = r[:len(columnas)]
        r = r + [""] * (len(columnas) - len(r))
        fila = {c: v for c, v in zip(columnas, r) if v != ""}
        fila["fila_csv"] = str(n)
        filas.append(fila)

    print(f"CSV: {origen} · separador {sep!r} · {len(columnas)} columnas")
    if vacias:
        print(f"Líneas vacías que no cuento: {vacias}")
    copias = len(filas) - len({json.dumps({k: v for k, v in f.items() if k != 'fila_csv'}, sort_keys=True) for f in filas})
    print(f"Traídas: {miles(len(filas))} · esperadas: {miles(esperadas)} · copias exactas: {miles(copias)}")

    ahora = datetime.now(COLOMBIA)
    nuevo = not os.path.exists("conteos.csv")
    estado = "completa" if len(filas) == esperadas else "incompleta"
    archivo = ""
    if estado == "completa":
        os.makedirs(os.path.join("data", "raw"), exist_ok=True)
        archivo = os.path.join("data", "raw", f"{conjunto}_{ahora.strftime('%Y-%m-%d_%H%M%S')}.json")
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(filas, f, ensure_ascii=False)
    with open("conteos.csv", "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["fecha", "conjunto", "filtro", "esperadas", "traidas", "ids_unicos",
                        "paginas", "estado", "archivo", "detalle"])
        w.writerow([ahora.strftime("%Y-%m-%d %H:%M"), conjunto, "", esperadas, len(filas), len(filas),
                    "", estado, archivo, f"CSV descargado a mano: {os.path.basename(origen)}"])

    if estado == "completa":
        print(f"COMPLETA. Bruto guardado en {archivo}. Registro agregado a conteos.csv.")
        print("Sigue con: python3 preparar_carga.py")
    else:
        print("ALTO: no cuadra. No guardo el bruto. Revisen el filtro o vuelvan a descargar.")
        sys.exit(1)


if __name__ == "__main__":
    main()
