"""Módulo de Integración Relacional, Linaje Total y Diccionario de Datos (E1-E2).

Realiza el join/merge limpio entre precios mayoristas y variables hidroclimáticas,
inyecta las 5 columnas obligatorias de linaje rastreables hasta data/bronce/*.meta.json
en todos los artefactos de data/oro/, y actualiza data/oro/diccionario_datos.md.
"""

from pathlib import Path

import pandas as pd

from config import (
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PLATA_CLIMA_LIMPIO,
    ARCHIVO_PLATA_PRECIOS_LIMPIO,
    ARCHIVO_PRECIOS_MENSUAL,
    ARCHIVO_PRONOSTICOS_ORO,
    DATA_ORO,
    MAPEO_CULTIVO_ZONA_ORIGEN,
)
from pipeline.geoespacial import (
    adjuntar_columnas_linaje,
    obtener_metadatos_linaje_bronce,
)

DESCRIPCIONES_VARIABLES: dict[str, tuple[str, str]] = {
    "periodo_mensual": ("Año-Mes ISO (YYYY-MM)", "Clave temporal de integración"),
    "cultivo": ("Texto categórico", "Cultivo agrocomercial de Colima"),
    "zona_agricola": ("Texto categórico", "Región agroproductora de origen en Colima"),
    "central_abasto": ("Texto categórico", "Mercado mayorista nacional de destino"),
    "variedad_sniim": ("Texto", "Denominación comercial oficial en catálogo SNIIM"),
    "precio_mayorista_mxn_kg": ("MXN / kg", "Precio mayorista mensual limpio"),
    "volatilidad_mensual_pct": ("Porcentaje (%)", "Coeficiente de variación mensual"),
    "costo_logistico_mxn_kg": ("MXN / kg", "Flete refrigerado/ventilado estimado"),
    "margen_comercial_mxn_kg": ("MXN / kg", "Margen neto descontando origen y flete"),
    "margen_comercial_pct": ("Porcentaje (%)", "Margen comercial neto relativo"),
    "categoria_precio": ("Ordinal (Bajo/Medio/Alto)", "Discretización por terciles"),
    "nivel_volatilidad": ("Ordinal (Estable/Moderada/Alta)", "Riesgo de cotización"),
    "temperatura_max_c": ("Grados Celsius (°C)", "Temperatura máxima media mensual"),
    "temperatura_media_c": ("Grados Celsius (°C)", "Temperatura promedio mensual"),
    "precipitacion_acumulada_mm": ("Milímetros (mm)", "Lluvia acumulada mensual"),
    "evapotranspiracion_mm": ("Milímetros (mm)", "Evapotranspiración FAO ET0 acumulada"),
    "humedad_relativa_pct": ("Porcentaje (%)", "Humedad relativa media mensual"),
    "linaje_id_registro": ("Identificador único", "ID determinista del registro en Oro"),
    "linaje_archivo_bronce": ("Nombre de archivo", "Archivo origen en data/bronce/"),
    "linaje_sha256_bronce": ("Hash SHA-256 (64 hex)", "Firma criptográfica desde .meta.json"),
    "linaje_fecha_ingesta_utc": ("ISO-8601 UTC", "Timestamp de captura en Capa Bronce"),
    "linaje_fuente": ("Texto identificador", "Fuente de extracción verificada"),
}


def preparar_esquema_precios(df_precios: pd.DataFrame) -> pd.DataFrame:
    """Asigna zona agrícola de origen y renombra metadatos para evitar colisión."""
    df_prep = df_precios.copy()
    df_prep["zona_agricola"] = df_prep["cultivo"].map(MAPEO_CULTIVO_ZONA_ORIGEN)
    return df_prep.rename(
        columns={
            "fecha_captura": "fecha_captura_precios",
            "fuente_origen": "fuente_origen_precios",
            "es_atipico_iqr": "es_atipico_precio",
        }
    )


def preparar_esquema_clima(df_clima: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas de linaje climático antes de la unión relacional."""
    return df_clima.copy().rename(
        columns={
            "fecha_captura": "fecha_captura_clima",
            "fuente_origen": "fuente_origen_clima",
            "es_atipico_iqr": "es_atipico_clima",
        }
    )


def integrar_precios_y_clima(
    df_precios: pd.DataFrame, df_clima: pd.DataFrame
) -> pd.DataFrame:
    """Ejecuta el merge relacional limpio e inyecta trazabilidad completa Bronce-Oro."""
    df_p = preparar_esquema_precios(df_precios)
    df_c = preparar_esquema_clima(df_clima)
    df_oro = pd.merge(
        df_p,
        df_c,
        on=["periodo_mensual", "zona_agricola"],
        how="inner",
        validate="many_to_one",
    )
    df_oro = df_oro.sort_values(
        ["periodo_mensual", "cultivo", "central_abasto"]
    ).reset_index(drop=True)
    meta_clima = obtener_metadatos_linaje_bronce(ARCHIVO_CLIMA_MENSUAL)
    df_oro["linaje_sha256_clima_bronce"] = str(meta_clima["hash_sha256"])
    return adjuntar_columnas_linaje(df_oro, ARCHIVO_PRECIOS_MENSUAL, "ORO-ANL")


def actualizar_linaje_pronosticos() -> None:
    """Asegura que pronosticos_e1.csv en Capa Oro también tenga las 5 columnas de linaje."""
    if ARCHIVO_PRONOSTICOS_ORO.exists():
        df_pron = pd.read_csv(ARCHIVO_PRONOSTICOS_ORO)
        df_pron = adjuntar_columnas_linaje(df_pron, ARCHIVO_PRECIOS_MENSUAL, "ORO-PRN")
        df_pron.to_csv(ARCHIVO_PRONOSTICOS_ORO, index=False, encoding="utf-8")


def formatear_fila_diccionario(columna: str, serie: pd.Series) -> str:
    """Construye una fila Markdown con tipo, unidad, completitud y rango observado."""
    unidad, desc = DESCRIPCIONES_VARIABLES.get(
        columna, ("Escala [0, 1] / Metadato", f"Indicador o atributo ({columna})")
    )
    completitud = round((1.0 - float(serie.isna().mean())) * 100.0, 2)
    if pd.api.types.is_numeric_dtype(serie) and serie.dtype != bool:
        rango = f"[{serie.min():.2f}, {serie.max():.2f}] (media={serie.mean():.2f})"
    else:
        ejemplos = ", ".join(map(str, serie.dropna().unique()[:3]))
        rango = f"Valores: {ejemplos[:64]}"
    return f"| `{columna}` | `{serie.dtype}` | {unidad} | {completitud}% | {rango} | {desc} |"


def generar_diccionario_datos(
    df_oro: pd.DataFrame, ruta_md: Path = ARCHIVO_DICCIONARIO_ORO
) -> None:
    """Genera automáticamente data/oro/diccionario_datos.md con tablas E1 y E2."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    filas_anl = [
        formatear_fila_diccionario(col, df_oro[col]) for col in list(df_oro.columns)
    ]
    bloques = [
        "# Diccionario de Datos — Capa Oro (`dataset_analitico.csv` y `rutas_flete_colima.csv`)\n",
        f"* **Total de registros analíticos (E1-E2):** `{len(df_oro)}` filas (`48` meses × `4` cultivos × `4` centrales)",
        f"* **Total de atributos en `dataset_analitico.csv`:** `{len(df_oro.columns)}` columnas (incluye 5 columnas de linaje SHA-256)",
        "* **Estándar de calidad aplicado:** ISO/IEC 25012 (Completitud, Exactitud, Consistencia y Trazabilidad)\n",
        "## 1. Tabla Principal: `dataset_analitico.csv`\n",
        "| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |",
        "| :--- | :--- | :--- | :---: | :--- | :--- |",
        *filas_anl,
    ]
    if ARCHIVO_ORO_RUTAS_FLETE.exists():
        df_rutas = pd.read_csv(ARCHIVO_ORO_RUTAS_FLETE)
        filas_geo = [
            formatear_fila_diccionario(col, df_rutas[col])
            for col in list(df_rutas.columns)
        ]
        bloques.extend(
            [
                "\n## 2. Tabla Geoespacial y Logística (E2): `rutas_flete_colima.csv`\n",
                f"* **Total de rutas productor-comprador ancla:** `{len(df_rutas)}` rutas (`4` productores × `4` compradores en Colima, reproyección `EPSG:4326` -> `EPSG:32613` UTM Zona 13N)\n",
                "| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |",
                "| :--- | :--- | :--- | :---: | :--- | :--- |",
                *filas_geo,
            ]
        )
    ruta_md.write_text("\n".join(bloques) + "\n", encoding="utf-8")


def ejecutar_integracion_oro() -> dict[str, int | float]:
    """Orquesta la unión de Plata a Oro, inyecta linaje SHA-256 y escribe diccionario."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    df_precios = pd.read_csv(ARCHIVO_PLATA_PRECIOS_LIMPIO)
    df_clima = pd.read_csv(ARCHIVO_PLATA_CLIMA_LIMPIO)
    df_oro = integrar_precios_y_clima(df_precios, df_clima)
    df_oro.to_csv(ARCHIVO_ORO_ANALITICO, index=False, encoding="utf-8")
    actualizar_linaje_pronosticos()
    generar_diccionario_datos(df_oro, ARCHIVO_DICCIONARIO_ORO)
    completitud = round((1.0 - float(df_oro.isna().mean().mean())) * 100.0, 2)
    return {
        "filas_oro": len(df_oro),
        "columnas_oro": len(df_oro.columns),
        "completitud_pct": completitud,
    }


if __name__ == "__main__":
    resumen = ejecutar_integracion_oro()
    print(f"Integración y linaje en Capa Oro completados: {resumen}")
