import pandas as pd

def cargar_empresas():
    archivo = "data/empresas.xlsx"
    
    hojas = pd.ExcelFile(archivo).sheet_names
    print(f"Hojas detectadas: {hojas}")

    columnas_necesarias = [
        "NOMBRE DE LA EMPRESA (RAZÓN SOCIAL)", "NOMBRE DE LA ORGANIZACIÓN (RAZÓN SOCIAL)",
        "NOMBRE DE LA ENTIDAD (RAZÓN SOCIAL)", "NOMBRE DEL LABORATORIO (RAZÓN SOCIAL)", 
        "NOMBRE DEL PUESTO O LUGAR", "NOMBRE DE LA GALLERA (RAZÓN SOCIAL)", 
        "NOMBRE DE LA INSTITUCIÓN (RAZÓN SOCIAL)", "DEPARTAMENTO", "MUNICIPIO", "CODIGO MUNICIPIO",
        "LONGITUD", "LATITUD", "DIRECCIÓN"
        
    ]

    datos_por_hoja = {}

    for hoja in hojas:
        try:
            df = pd.read_excel(archivo, sheet_name=hoja, skiprows=2)

            print(f"\n🔍 Primeras filas de {hoja}:")
            print(df.head())

            df.columns = df.columns.str.strip().str.replace("\n", " ").str.replace(r"\s+", " ", regex=True)

            print(f"📌 Nombres detectados por pandas en {hoja}:")
            print(df.columns.tolist())

            columnas_existentes = [col for col in columnas_necesarias if col in df.columns]
            df_filtrado = df[columnas_existentes] if columnas_existentes else pd.DataFrame()

            # 🔍 Convertir columnas de coordenadas a numérico y eliminar filas inválidas
            if "LATITUD" in df_filtrado.columns and "LONGITUD" in df_filtrado.columns:
                df_filtrado["LATITUD"] = pd.to_numeric(df_filtrado["LATITUD"], errors="coerce")
                df_filtrado["LONGITUD"] = pd.to_numeric(df_filtrado["LONGITUD"], errors="coerce")
                df_filtrado = df_filtrado.dropna(subset=["LATITUD", "LONGITUD"])

            datos_por_hoja[hoja] = df_filtrado
           
           
            print(f"✅ Datos correctamente procesados para la hoja: {hoja}")

        except Exception as e:
            print(f"⚠️ Error en la hoja {hoja}: {e}")
            datos_por_hoja[hoja] = pd.DataFrame()

    return datos_por_hoja

# Ejecución de prueba
if __name__ == "__main__":
    empresas_por_hoja = cargar_empresas()
    for hoja, datos in empresas_por_hoja.items():
        print(f"\n📍 Datos filtrados de {hoja}:")
        print(datos.head())
