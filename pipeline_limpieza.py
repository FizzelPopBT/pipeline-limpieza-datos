import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    filename='pipeline.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    encoding='utf-8'
)

def ejecutar_pipeline():
    logging.info("=== INICIO DEL PIPELINE DE LIMPIEZA Y TRANSFORMACIÓN ===")

    ruta_raw = "mascotas.csv"
    if not os.path.exists(ruta_raw):
        print(f"Error: No se encontró el archivo '{ruta_raw}' en el directorio actual.")
        logging.error(f"Archivo no encontrado: {ruta_raw}")
        return

    df = pd.read_csv(ruta_raw)
    registros_iniciales = len(df)
    logging.info(f"Dataset cargado correctamente. Registros iniciales: {registros_iniciales}")
    print(f"-> Registros iniciales: {registros_iniciales}")

    df = df.dropna(how='all')
    vacios_eliminados = registros_iniciales - len(df)
    logging.info(f"Registros completamente vacíos eliminados: {vacios_eliminados}")

    antes_dup = len(df)
    df = df.drop_duplicates(subset=['id_mascota'], keep='first')
    duplicados_eliminados = antes_dup - len(df)
    logging.info(f"Registros duplicados eliminados (por id_mascota): {duplicados_eliminados}")

    df['especie'] = df['especie'].astype(str).str.strip().str.lower()
    df['especie'] = df['especie'].replace({'cat': 'gato', 'gata': 'gato', 'perra': 'perro'})
    logging.info("Columna 'especie' homogeneizada a formatos estandarizados ('gato' o 'perro').")

    df.loc[df['edad_años'] < 0, 'edad_años'] = np.nan
    
    medianas_edad = df.groupby('especie')['edad_años'].transform('median')
    nulos_edad_antes = df['edad_años'].isnull().sum()
    df['edad_años'] = df['edad_años'].fillna(medianas_edad)
    logging.info(f"Valores nulos o inválidos de 'edad_años' imputados con la mediana: {nulos_edad_antes}")

    condicion_outlier = ((df['especie'] == 'gato') & (df['peso_kg'] > 15)) | \
                        ((df['especie'] == 'perro') & (df['peso_kg'] > 100))
    
    outliers_peso = df[condicion_outlier].shape[0]
    medianas_peso = df.groupby('especie')['peso_kg'].transform('median')
    df.loc[condicion_outlier, 'peso_kg'] = np.nan
    df['peso_kg'] = df['peso_kg'].fillna(medianas_peso)
    logging.info(f"Outliers extremos de 'peso_kg' corregidos e imputados: {outliers_peso}")

    df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce', format='mixed')
    logging.info("Formatos de 'fecha_consulta' unificados al estándar internacional YYYY-MM-DD.")

    def clasificar_peso(row):
        esp = row['especie']
        peso = row['peso_kg']
        if esp == 'gato':
            if peso < 3.0: return 'Bajo'
            elif peso <= 5.5: return 'Normal'
            else: return 'Alto'
        elif esp == 'perro':
            if peso < 5.0: return 'Bajo'
            elif peso <= 25.0: return 'Normal'
            elif peso <= 45.0: return 'Alto'
            else: return 'Obeso'
        return 'Normal'

    df['rango_peso'] = df.apply(clasificar_peso, axis=1)
    logging.info("Nueva columna derivada 'rango_peso' creada con éxito.")

    df['consulta_año'] = df['fecha_consulta'].dt.year
    df['consulta_mes'] = df['fecha_consulta'].dt.month
    logging.info("Columnas temporales 'consulta_año' y 'consulta_mes' añadidas.")

    df_encoded = pd.get_dummies(df, columns=['especie'], prefix='esp', drop_first=False)
    logging.info("One-Hot Encoding aplicado sobre la variable categórica 'especie'.")

    os.makedirs("data/processed", exist_ok=True)
    
    ruta_salida = "data/processed/mascotas_clean.csv"
    df_encoded.to_csv(ruta_salida, index=False, encoding='utf-8')
    
    registros_finales = len(df_encoded)
    logging.info(f"Dataset procesado guardado con éxito en: {ruta_salida}")
    logging.info(f"Registros finales procesados: {registros_finales}")
    logging.info("=== FIN DEL PIPELINE CON ÉXITO ===")

    print("\n==========================================")
    print("¡Proceso completado con éxito!")
    print(f"-> Archivo guardado en: {ruta_salida}")
    print(f"-> Registros eliminados en total: {registros_iniciales - registros_finales}")
    print(f"-> Revisa el historial técnico generado en: 'pipeline.log'")
    print("==========================================\n")

if __name__ == "__main__":
    ejecutar_pipeline()