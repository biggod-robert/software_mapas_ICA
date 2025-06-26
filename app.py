from flask import Flask, render_template, request
import folium
from scripts.load_data import cargar_empresas

app = Flask(__name__)

# Cargar los datos una vez
datos_por_hoja = cargar_empresas()

@app.route("/", methods=["GET"])
def index():
    hoja_seleccionada = request.args.get("hoja", list(datos_por_hoja.keys())[0])
    datos = datos_por_hoja.get(hoja_seleccionada)

    mapa = None
    if datos is not None and not datos.empty:
        try:
            # Centrado automático del mapa
            centro = [
                datos["LATITUD"].mean(),
                datos["LONGITUD"].mean()
            ]
            mapa = folium.Map(location=centro, zoom_start=6)

            # Colores personalizados por hoja
            colores = {
                "FERIAS": "green",
                "GALLERAS": "red",
                "PLANTAS LECHERAS": "purple",
                "PUESTOS DE CONTROL-MOVILIZACION": "orange",
                "SERVICIOS VET. PÚBLICOS": "blue",
                "ORGANIZACIONES DE PRODUCTORES": "darkblue"
            }
            color_icono = colores.get(hoja_seleccionada, "cadetblue")

            for _, fila in datos.iterrows():
                lat = fila["LATITUD"]
                lon = fila["LONGITUD"]
                nombre = fila.get("NOMBRE DE LA EMPRESA (RAZÓN SOCIAL)", 
                                  fila.get("NOMBRE DE LA ORGANIZACIÓN (RAZÓN SOCIAL)", "Sin nombre"))
                direccion = fila.get("DIRECCIÓN", fila.get("DIRECCIÓN ", "Sin dirección"))

                tooltip_text = nombre

                popup_html = f"""
                <div style="font-size:14px; line-height:1.4; max-width:250px;">
                    <strong style="color:#0d6efd;">{nombre}</strong><br>
                    <span style="color:#444;">📍 {direccion}</span><br>
                    <span style="color:#6c757d;">📌 Lat/Lon: {lat:.5f}, {lon:.5f}</span>
                </div>
                """

                folium.Marker(
                    location=[lat, lon],
                    tooltip=tooltip_text,
                    popup=folium.Popup(popup_html, max_width=300),
                    icon=folium.Icon(color=color_icono, icon="info-sign")
                ).add_to(mapa)

        except Exception as e:
            print(f"⚠️ Error al construir el mapa: {e}")
            mapa = None

    return render_template("index.html",
                           hojas=list(datos_por_hoja.keys()),
                           hoja_actual=hoja_seleccionada,
                           tabla=datos.to_html(classes="table table-striped table-bordered", index=False) if datos is not None else None,
                           mapa=mapa._repr_html_() if mapa else None)

if __name__ == "__main__":
    app.run(debug=True)
