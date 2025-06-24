from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Cargar datos desde el archivo .xlsx
def cargar_empresas():
    archivo = "data/empresas.xlsx"  # Asegúrate de que el nombre coincida
    df = pd.read_excel(archivo)  # Ahora podemos leerlo sin necesidad de pyxlsb
    return df.to_dict(orient="records")  # Convertir los datos a una lista de diccionarios

@app.route('/')
def home():
    empresas = cargar_empresas()
    return render_template('index.html', empresas=empresas)

if __name__ == '__main__':
    app.run(debug=True)
