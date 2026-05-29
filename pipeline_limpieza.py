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

def validar_estructura(df):

    logging.info("=== VALIDACIONES ESTRUCTURALES ===")

    df['val_id'] = df['id_mascota'].notna()

    especies_validas = ['perro', 'gato', 'conejo', 'pez', 'loro']

    df['especie'] = (
        df['especie']
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df['especie'] = df['especie'].replace({
        'cat': 'gato',
        'gata': 'gato',
        'perra': 'perro'
    })

    df['val_especie'] = df['especie'].isin(especies_validas)

    df['val_peso'] = df['peso_kg'].between(0.05, 120)

    df['fecha_consulta'] = pd.to_datetime(
        df['fecha_consulta'],
        errors='coerce',
        format='mixed'
    )

    df['val_fecha'] = df['fecha_consulta'].notna()

    logging.info(
        f"Validación estructura completada | "
        f"id válidos={df['val_id'].sum()} | "
        f"especie válidas={df['val_especie'].sum()} | "
        f"peso válidos={df['val_peso'].sum()} | "
        f"fecha válidas={df['val_fecha'].sum()}"
    )

    return df

def clasificar_peso(row):

    esp = row['especie']
    peso = row['peso_kg']

    if esp == 'gato':
        if peso < 3:
            return 'Bajo'
        elif peso <= 5.5:
            return 'Normal'
        elif peso <= 6:
            return 'Alto'
        else:
            return 'Obeso'

    elif esp == 'perro':
        if peso < 5:
            return 'Bajo'
        elif peso <= 25:
            return 'Normal'
        elif peso <= 30:
            return 'Alto'
        else:
            return 'Obeso'

    return 'Normal'


def validar_semantica(df):

    logging.info("=== VALIDACIONES SEMÁNTICAS ===")

    df['rango_peso'] = df.apply(clasificar_peso, axis=1)

    df['val_semantica'] = True

    df.loc[
        (df['rango_peso'] == 'Obeso') &
        (df['especie'] == 'perro') &
        (df['peso_kg'] <= 30),
        'val_semantica'
    ] = False

    df.loc[
        (df['rango_peso'] == 'Obeso') &
        (df['especie'] == 'gato') &
        (df['peso_kg'] <= 6),
        'val_semantica'
    ] = False


    df['val_fecha_futura'] = (
        df['fecha_consulta'] <= pd.Timestamp.today()
    )

    logging.info(
        f"Validación semántica completada | "
        f"semántica válidas={df['val_semantica'].sum()} | "
        f"fechas válidas={df['val_fecha_futura'].sum()}"
    )

    return df


def limpiar_datos(df):

    logging.info("=== LIMPIEZA DE DATOS ===")

    registros_antes = len(df)

    df = df.dropna(how='all')

    logging.info(
        f"Filas vacías eliminadas: "
        f"{registros_antes - len(df)}"
    )

    antes_dup = len(df)

    df = df.drop_duplicates(
        subset=['id_mascota'],
        keep='first'
    )

    logging.info(
        f"Duplicados eliminados: "
        f"{antes_dup - len(df)}"
    )

    df.loc[df['edad_años'] < 0, 'edad_años'] = np.nan

    medianas_edad = (
        df.groupby('especie')['edad_años']
        .transform('median')
    )

    df['edad_años'] = df['edad_años'].fillna(medianas_edad)

    logging.info("Edad imputada con medianas.")

    condicion_outlier = (
        ((df['especie'] == 'gato') & (df['peso_kg'] > 15)) |
        ((df['especie'] == 'perro') & (df['peso_kg'] > 100))
    )

    outliers = df[condicion_outlier].shape[0]

    medianas_peso = (
        df.groupby('especie')['peso_kg']
        .transform('median')
    )

    df.loc[condicion_outlier, 'peso_kg'] = np.nan

    df['peso_kg'] = df['peso_kg'].fillna(medianas_peso)

    logging.info(f"Outliers corregidos: {outliers}")

    return df


def exportar_resultados(validos, invalidos):

    os.makedirs("data/processed", exist_ok=True)

    ruta_validos = "data/processed/mascotas_validas.csv"
    ruta_invalidos = "data/processed/mascotas_invalidas.csv"

    validos.to_csv(
        ruta_validos,
        index=False,
        encoding='utf-8'
    )

    invalidos.to_csv(
        ruta_invalidos,
        index=False,
        encoding='utf-8'
    )

    logging.info(f"Archivo válidos guardado: {ruta_validos}")
    logging.info(f"Archivo inválidos guardado: {ruta_invalidos}")

def ejecutar_pipeline():

    logging.info("=== INICIO PIPELINE ===")

    ruta_raw = "mascotas.csv"

    if not os.path.exists(ruta_raw):

        print(f"Error: No se encontró '{ruta_raw}'")

        logging.error(f"Archivo no encontrado: {ruta_raw}")

        return

    df = pd.read_csv(ruta_raw)

    registros_iniciales = len(df)

    print(f"Registros iniciales: {registros_iniciales}")

    logging.info(
        f"Dataset cargado correctamente | "
        f"registros={registros_iniciales}"
    )

    df = limpiar_datos(df)

    df = validar_estructura(df)

    df = validar_semantica(df)

    df['registro_valido'] = (

        df['val_id'] &
        df['val_especie'] &
        df['val_peso'] &
        df['val_fecha'] &
        df['val_semantica'] &
        df['val_fecha_futura']
    )

    validos = df[df['registro_valido']]

    invalidos = df[~df['registro_valido']]

    validos['consulta_año'] = (
        validos['fecha_consulta'].dt.year
    )

    validos['consulta_mes'] = (
        validos['fecha_consulta'].dt.month
    )

    validos = pd.get_dummies(
        validos,
        columns=['especie'],
        prefix='esp',
        drop_first=False
    )

    exportar_resultados(validos, invalidos)

    porcentaje_validos = (
        len(validos) / len(df)
    ) * 100

    logging.info(
        f"Registros válidos: {len(validos)}"
    )

    logging.info(
        f"Registros inválidos: {len(invalidos)}"
    )

    logging.info(
        f"Porcentaje válidos: {porcentaje_validos:.2f}%"
    )

    logging.info("=== FIN PIPELINE ===")

    print("\n====================================")
    print("PIPELINE COMPLETADO")
    print("====================================")
    print(f"Registros totales: {len(df)}")
    print(f"Registros válidos: {len(validos)}")
    print(f"Registros inválidos: {len(invalidos)}")
    print(f"% válidos: {porcentaje_validos:.2f}%")
    print("Archivo válidos:")
    print("data/processed/mascotas_validas.csv")
    print("Archivo inválidos:")
    print("data/processed/mascotas_invalidas.csv")
    print("Logs:")
    print("pipeline.log")
    print("====================================\n")


if __name__ == "__main__":
    ejecutar_pipeline()