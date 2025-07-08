__author__ = "Robert Moor"
__copyright__ = "Copyright © 2025 Robert Moor"
__license__ = "Todos los derechos reservados"

from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import pandas as pd
import folium
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

datos_por_hoja = {}

@app.route("/", methods=["GET"])
def index():
    hoja_seleccionada = request.args.get("hoja")
    columnas_mostradas = request.args.getlist("columnas")

    if not datos_por_hoja:
        return render_template("index.html", hojas=[], tabla=None, mapa=None, columnas=[], columnas_mostradas=[])

    hoja_actual = hoja_seleccionada or list(datos_por_hoja.keys())[0]
    datos = datos_por_hoja[hoja_actual]

    # ✅ Validar columnas seleccionadas contra las disponibles
    columnas_validas = [col for col in columnas_mostradas if col in datos.columns]
    if not columnas_validas:
        columnas_validas = datos.columns[:5].tolist()
        # 🔔 Notificar si hubo ajuste automático
    if set(columnas_mostradas) != set(columnas_validas):    
        flash("⚠ Algunas columnas seleccionadas no están disponibles en esta hoja. Se usaron columnas por defecto.")

    # 🔍 Renderizar tabla solo con columnas válidas
    tabla_html = datos[columnas_validas].to_html(classes="table table-bordered table-striped", index=False)

    def buscar_valor(fila, opciones, por_defecto="Sin dato"):
        for col in opciones:
            if col in fila and pd.notna(fila[col]):
                return fila[col]
        return por_defecto

    # 🌍 Generar mapa
    mapa = None
    if not datos.empty:
        centro = [datos["LATITUD"].mean(), datos["LONGITUD"].mean()]
        mapa = folium.Map(location=centro, zoom_start=6)

        for _, fila in datos.iterrows():
            lat = fila["LATITUD"]
            lon = fila["LONGITUD"]
            nombre = buscar_valor(fila, [
                "NOMBRE DE LA EMPRESA (RAZÓN SOCIAL)",
                "NOMBRE DE LA ORGANIZACIÓN (RAZÓN SOCIAL)",
                "NOMBRE DE LA ENTIDAD (RAZÓN SOCIAL)",
                "NOMBRE DE LA INSTITUCIÓN (RAZÓN SOCIAL)",
                "NOMBRE DEL PUESTO O LUGAR",
                "NOMBRE DE LA GALLERA (RAZÓN SOCIAL)"
                "NOMBRE DEL LABORATORIO (RAZÓN SOCIAL)"
            ])
            direccion = buscar_valor(fila, ["DIRECCIÓN", "DIRECCIÓN "], "Sin dirección")

            popup_html = f"""
                <div style="font-size:14px; max-width:250px;">
                    <strong style="color:#0d6efd;">{nombre}</strong><br>
                    <span style="color:#444;">📍 {direccion}</span><br>
                    <span style="color:#6c757d;">📌 Lat/Lon: {lat:.5f}, {lon:.5f}</span>
                </div>
            """
            folium.Marker(
                location=[lat, lon],
                tooltip=nombre,
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(mapa)

    return render_template("index.html",
                           hojas=list(datos_por_hoja.keys()),
                           hoja_actual=hoja_actual,
                           columnas=datos.columns,
                           columnas_mostradas=columnas_validas,
                           tabla=tabla_html,
                           mapa=mapa._repr_html_() if mapa else None)

@app.route("/subir", methods=["POST"])
def subir():
    archivo = request.files.get("archivo")

    if archivo and archivo.filename.endswith(".xlsx"):
        xl = pd.ExcelFile(archivo)
        global datos_por_hoja
        datos_por_hoja = {}

        for hoja in xl.sheet_names:
            df = pd.read_excel(archivo, sheet_name=hoja, skiprows=2)
            df.columns = df.columns.str.strip()

            if "LATITUD" in df.columns and "LONGITUD" in df.columns:
                df["LATITUD"] = pd.to_numeric(df["LATITUD"], errors="coerce")
                df["LONGITUD"] = pd.to_numeric(df["LONGITUD"], errors="coerce")
                df = df.dropna(subset=["LATITUD", "LONGITUD"])

            datos_por_hoja[hoja] = df

        primera_hoja = xl.sheet_names[0]
        flash("✅ Archivo cargado con éxito")
        return redirect(f"/?hoja={primera_hoja}")

    flash("❌ Solo se permiten archivos .xlsx")
    return redirect("/")



import threading
import webbrowser

def abrir_navegador():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.5, abrir_navegador).start()
    app.run(debug=False)

