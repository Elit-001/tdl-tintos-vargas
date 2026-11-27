"""Módulo de Integración Relacional, Linaje Total y Diccionario de Datos (E1-E3).

Realiza el join/merge limpio en memoria entre precios mayoristas y clima, inyecta
linaje SHA-256 sin copias redundantes, exporta CSV LF + Parquet y genera diccionario.
"""

from pathlib import Path

import pandas as pd

from config import (
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_PARQUET,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PLATA_CLIMA_LIMPIO,
    ARCHIVO_PLATA_PRECIOS_LIMPIO,
    ARCHIVO_PRECIOS_MENSUAL,
    ARCHIVO_PRONOSTICOS_ORO,
    ARCHIVO_PUBLICADO_CSV,
    DATA_ORO,
    MAPEO_CULTIVO_ZONA_ORIGEN,
)
from pipeline.geoespacial import (
    adjuntar_columnas_linaje,
    obtener_metadatos_linaje_bronce,
)
from pipeline.publicacion import optimizar_tipos_parquet

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
    "comprador_ancla_optimo_colima": ("Texto categórico", "Comprador B2B óptimo en Colima"),
    "distancia_vial_optima_km": ("Kilómetros (km)", "Distancia vial UTM 13N óptima"),
    "flete_local_400kg_mxn_kg": ("MXN / kg", "Costo logístico local en pool de 400 kg"),
    "spread_brokerage_colima_mxn_kg": ("MXN / kg", "Margen neto B2B local optimizado"),
    "linaje_id_registro": ("Identificador único", "ID determinista del registro en Oro"),
    "linaje_archivo_bronce": ("Nombre de archivo", "Archivo origen en data/bronce/"),
    "linaje_sha256_bronce": ("Hash SHA-256 (64 hex)", "Firma criptográfica desde .meta.json"),
    "linaje_fecha_ingesta_utc": ("ISO-8601 UTC", "Timestamp de captura en Capa Bronce"),
    "linaje_fuente": ("Texto identificador", "Fuente de extracción verificada"),
}


def preparar_esquema_precios(df_precios: pd.DataFrame) -> pd.DataFrame:
    """Asigna zona agrícola de origen y renombra metadatos para evitar colisión."""
    df_prep = df_precios.rename(
        columns={
            "fecha_captura": "fecha_captura_precios",
            "fuente_origen": "fuente_origen_precios",
            "es_atipico_iqr": "es_atipico_precio",
        }
    )
    df_prep["zona_agricola"] = df_prep["cultivo"].map(MAPEO_CULTIVO_ZONA_ORIGEN)
    return df_prep


def preparar_esquema_clima(df_clima: pd.DataFrame) -> pd.DataFrame:
    """Renombra columnas de linaje climático antes de la unión relacional."""
    return df_clima.rename(
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
    df_oro.sort_values(
        ["periodo_mensual", "cultivo", "central_abasto"], inplace=True
    )
    df_oro.reset_index(drop=True, inplace=True)
    meta_clima = obtener_metadatos_linaje_bronce(ARCHIVO_CLIMA_MENSUAL)
    df_oro["linaje_sha256_clima_bronce"] = str(meta_clima["hash_sha256"])
    return adjuntar_columnas_linaje(df_oro, ARCHIVO_PRECIOS_MENSUAL, "ORO-ANL")


def actualizar_linaje_pronosticos() -> None:
    """Asegura que pronosticos_e1.csv en Capa Oro también tenga las 5 columnas de linaje."""
    if ARCHIVO_PRONOSTICOS_ORO.exists():
        df_pron = pd.read_csv(ARCHIVO_PRONOSTICOS_ORO)
        df_pron = adjuntar_columnas_linaje(df_pron, ARCHIVO_PRECIOS_MENSUAL, "ORO-PRN")
        df_pron.to_csv(
            ARCHIVO_PRONOSTICOS_ORO, index=False, encoding="utf-8", lineterminator="\n"
        )


def formatear_fila_diccionario(columna: str, serie: pd.Series) -> str:
    """Construye una fila Markdown con tipo, unidad, completitud y rango observado."""
    unidad, desc = DESCRIPCIONES_VARIABLES.get(
        columna, ("Escala [0, 1] / Metadato", f"Indicador o atributo ({columna})")
    )
    arr = serie.to_numpy(copy=False)
    completitud = round((1.0 - float(pd.isna(arr).mean())) * 100.0, 2)
    if pd.api.types.is_numeric_dtype(serie) and serie.dtype != bool:
        rango = f"[{float(serie.min()):.2f}, {float(serie.max()):.2f}] (media={float(serie.mean()):.2f})"
    else:
        ejemplos = ", ".join(map(str, pd.unique(serie.dropna())[:3]))
        rango = f"Valores: {ejemplos[:64]}"
    return f"| `{columna}` | `{serie.dtype}` | {unidad} | {completitud}% | {rango} | {desc} |"


def generar_diccionario_datos(
    df_oro: pd.DataFrame,
    ruta_md: Path = ARCHIVO_DICCIONARIO_ORO,
    df_rutas_mem: pd.DataFrame | None = None,
    df_pub_mem: pd.DataFrame | None = None,
) -> None:
    """Genera data/oro/diccionario_datos.md documentando Oro y Dataset Publicado E3."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    filas_anl = [
        formatear_fila_diccionario(col, df_oro[col]) for col in list(df_oro.columns)
    ]
    n_per = df_oro["periodo_mensual"].nunique()
    n_cul = df_oro["cultivo"].nunique()
    n_cen = df_oro["central_abasto"].nunique()
    bloques = [
        "# Diccionario de Datos — Capa Oro y Dataset Publicado (`E1-E3`)\n",
        f"* **Total de registros analíticos:** `{len(df_oro)}` filas (`{n_per}` meses × `{n_cul}` cultivos × `{n_cen}` centrales)",
        f"* **Atributos en `dataset_analitico.csv`:** `{len(df_oro.columns)}` columnas (con linaje SHA-256)",
        "* **Estándar de calidad:** ISO/IEC 25012 + Licencia Abierta `CC BY 4.0` en `data/publicado/`\n",
        "## 1. Tabla Principal: `dataset_analitico.csv`\n",
        "| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |",
        "| :--- | :--- | :--- | :---: | :--- | :--- |",
        *filas_anl,
    ]
    df_rutas = (
        df_rutas_mem
        if df_rutas_mem is not None
        else (
            pd.read_csv(ARCHIVO_ORO_RUTAS_FLETE)
            if ARCHIVO_ORO_RUTAS_FLETE.exists()
            else None
        )
    )
    if df_rutas is not None:
        filas_geo = [
            formatear_fila_diccionario(col, df_rutas[col])
            for col in list(df_rutas.columns)
        ]
        bloques.extend(
            [
                "\n## 2. Tabla Geoespacial y Logística (E2): `rutas_flete_colima.csv`\n",
                "| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |",
                "| :--- | :--- | :--- | :---: | :--- | :--- |",
                *filas_geo,
            ]
        )
    df_pub = (
        df_pub_mem
        if df_pub_mem is not None
        else (
            pd.read_csv(ARCHIVO_PUBLICADO_CSV)
            if ARCHIVO_PUBLICADO_CSV.exists()
            else None
        )
    )
    if df_pub is not None:
        filas_pub = [
            formatear_fila_diccionario(col, df_pub[col])
            for col in list(df_pub.columns)
        ]
        bloques.extend(
            [
                "\n## 3. Dataset Curado Abierto para Terceros (E3): `data/publicado/agropulse_colima_curado.csv`\n",
                "| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |",
                "| :--- | :--- | :--- | :---: | :--- | :--- |",
                *filas_pub,
            ]
        )
    ruta_md.write_text("\n".join(bloques) + "\n", encoding="utf-8", newline="\n")


def integrar_en_memoria(
    df_precios: pd.DataFrame | None = None,
    df_clima: pd.DataFrame | None = None,
    df_rutas: pd.DataFrame | None = None,
    escribir_diccionario: bool = True,
) -> tuple[dict[str, int | float], pd.DataFrame]:
    """Integra Plata a Oro sin relecturas redundantes y exporta CSV LF + Parquet."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    df_pr = (
        df_precios
        if df_precios is not None
        else pd.read_csv(ARCHIVO_PLATA_PRECIOS_LIMPIO)
    )
    df_cl = (
        df_clima
        if df_clima is not None
        else pd.read_csv(ARCHIVO_PLATA_CLIMA_LIMPIO)
    )
    df_oro = integrar_precios_y_clima(df_pr, df_cl)
    df_oro.to_csv(
        ARCHIVO_ORO_ANALITICO, index=False, encoding="utf-8", lineterminator="\n"
    )
    optimizar_tipos_parquet(df_oro).to_parquet(ARCHIVO_ORO_PARQUET, index=False)
    actualizar_linaje_pronosticos()
    if escribir_diccionario:
        generar_diccionario_datos(df_oro, ARCHIVO_DICCIONARIO_ORO, df_rutas_mem=df_rutas)
    completitud = round((1.0 - float(df_oro.isna().to_numpy().mean())) * 100.0, 2)
    resumen = {
        "filas_oro": len(df_oro),
        "columnas_oro": len(df_oro.columns),
        "completitud_pct": completitud,
    }
    return resumen, df_oro


def ejecutar_integracion_oro() -> dict[str, int | float]:
    """Orquesta la unión de Plata a Oro, inyecta linaje SHA-256 y escribe diccionario."""
    resumen, _ = integrar_en_memoria()
    return resumen


if __name__ == "__main__":
    resumen = ejecutar_integracion_oro()
    print(f"Integración y linaje en Capa Oro completados: {resumen}")
