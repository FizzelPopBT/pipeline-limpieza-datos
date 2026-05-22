# Pipeline de Datos - Limpieza y Transformación (Mascotas de Clínica Veterinaria)

Este proyecto automatiza las labores de limpieza y procesamiento del set de datos `mascotas.csv` bajo principios fundamentales de **DataOps** (reproducibilidad, modularidad y trazabilidad).

## Problemas Detectados y Soluciones Aplicadas

1. ****Registros Vacíos**: Se detectó una fila completamente nula (Fila 6) que fue eliminada para evitar distorsiones en las sumatorias globales.
2. **Duplicidad**: Se eliminaron registros duplicados basándose en la unicidad de la llave primaria `id_mascota`.
3. **Inconsistencia Categórica**: La columna `especie` poseía valores mezclados en mayúsculas, minúsculas e inglés (`gato`, `GATO`, `Cat`, `gata`). Se normalizó todo a minúsculas y términos estándar (`gato` y `perro`).
4. **Nulos Críticos y Errores en Edad**: Registros con edades faltantes o valores erróneos negativos se imputaron dinámicamente utilizando la **mediana** calculada según la especie del animal.
5. **Outliers en Peso**: Valores fuera de rango biológico lógico (ej. perro de 350kg o el gato Garfield con 9999kg) fueron detectados mediante umbrales específicos por especie e imputados usando las medianas del grupo correspondiente.
6. **Inconsistencia de Fechas**: Se unificaron tres formatos de fecha diferentes bajo la norma internacional ISO 8601 (`YYYY-MM-DD`).

## Transformaciones Realizadas (Feature Engineering)

- **Columna Derivada (`rango_peso`)**: Clasificación categórica de la masa del animal (Bajo, Normal, Alto, Obeso) adaptada al tipo de mascota.
- **Componentes Temporales**: Extracción de campos numéricos individuales para el `consulta_año` y `consulta_mes`.
- **One-Hot Encoding**: Conversión de la columna `especie` en variables binarias booleanas numéricas (`esp_gato`, `esp_perro`), preparando el set para su uso directo en algoritmos de Inteligencia Artificial.

## Instrucciones de Ejecución

1. Coloca el archivo original `mascotas.csv` en el mismo directorio que el script.
2. Ejecuta el script utilizando Python:
   ```bash
   python pipeline_limpieza.py