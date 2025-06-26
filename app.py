from flask import Flask, render_template, request, redirect, flash
from werkzeug.utils import secure_filename
import pandas as pd
import folium
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"  # Necesario para flash messages

# Diccionario global para guardar datos por hoja
datos_por_hoja = {}

@app.route("/", methods=["GET"])
def index():
    hoja_seleccionada = request.args.get("hoja")
    columnas_mostradas = request.args.getlist("columnas")

    if not datos_por_hoja:
        return render_template("index.html", hojas=[], tabla=None, mapa=None, columnas=[], columnas_mostradas=[])

    hoja_actual = hoja_seleccionada or list(datos_por_hoja.keys())[0]
    datos = datos_por_hoja[hoja_actual]

    if not columnas_mostradas:
        columnas_mostradas = datos.columns[:5].tolist()

    # Generar tabla HTML con columnas seleccionadas
    tabla_html = datos[columnas_mostradas].to_html(classes="table table-bordered table-striped", index=False)

    # Crear mapa si hay datos
    mapa = None
    if not datos.empty:
        centro = [datos["LATITUD"].mean(), datos["LONGITUD"].mean()]
        mapa = folium.Map(location=centro, zoom_start=6)

        for _, fila in datos.iterrows():
            lat = fila["LATITUD"]
            lon = fila["LONGITUD"]
            nombre = fila.get("NOMBRE DE LA EMPRESA (RAZÓN SOCIAL)",
                              fila.get("NOMBRE DE LA ORGANIZACIÓN (RAZÓN SOCIAL)", "Sin nombre"))
            direccion = fila.get("DIRECCIÓN", fila.get("DIRECCIÓN ", "Sin dirección"))

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
                           columnas_mostradas=columnas_mostradas,
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


if __name__ == "__main__":
    app.run(debug=True)

