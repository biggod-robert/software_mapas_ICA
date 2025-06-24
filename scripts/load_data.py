import pandas as pd

def cargar_empresas():
    archivo = "data/empresas.xlsx"
    
    # Leer todas las hojas del archivo Excel
    hojas = pd.ExcelFile(archivo).sheet_names
    print(f"Hojas detectadas: {hojas}")

    # Columnas clave para ubicación
    columnas_necesarias = ["DEPARTAMENTO", "MUNICIPIO", "CODIGO MUNICIPIO", "LONGITUD", "LATITUD", "DIRECCIÓN "]

    # Guardar datos de cada hoja
    datos_por_hoja = {}

    for hoja in hojas:
        
        
        try:
            # Leer la hoja sin redefinir encabezado
            df = pd.read_excel(archivo, sheet_name=hoja, skiprows=2)  # puedes ajustar skiprows si la fila de encabezados no es la 3ra

            # Mostrar primeras filas para verificar la estructura
            print(f"🔍 Primeras filas de {hoja}:")
            print(df.head())

            # Mostrar nombres de columna detectados por pandas
            print(f"📌 Nombres detectados por pandas en {hoja}:")
            print(df.columns.tolist())

            # Limpiar nombres de columnas
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace("\n", " ")
            df.columns = df.columns.str.replace(r"\s+", " ", regex=True)

            # Filtrar solo las columnas esenciales
            columnas_existentes = [col for col in columnas_necesarias if col in df.columns]
            df_filtrado = df[columnas_existentes]


            # Guardar los datos en el diccionario
            datos_por_hoja[hoja] = df

            print(f"✅ Datos correctamente procesados para la hoja: {hoja}")

        except Exception as e:
            print(f"⚠️ Error al procesar la hoja {hoja}: {e}")
            datos_por_hoja[hoja] = pd.DataFrame()  # Guardar un DataFrame vacío en caso de error

    return datos_por_hoja  # Devuelve un diccionario con los datos organizados por hoja

# Prueba la carga
if __name__ == "__main__":
    empresas_por_hoja = cargar_empresas()
    for hoja, datos in empresas_por_hoja.items():
        print(f"📌 Datos de {hoja}:")
        print(datos.head())
