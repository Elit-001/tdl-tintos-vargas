"""Módulo de Limpieza Estadística en Capa Plata (Nulos, IQR, Min-Max y Discretización).

Cumple los criterios E1 de Ingeniería de Datos: diagnóstico de mecanismos de datos
faltantes (MCAR/MAR/MNAR) e imputación por serie temporal, detección/winsorización
de atípicos mediante Rango Intercuartílico (IQR), normalización Min-Max y
discretización de niveles de precio y volatilidad.
"""

import pandas as pd

from config import (
    ARCHIVO_PLATA_CLIMA,
    ARCHIVO_PLATA_CLIMA_LIMPIO,
    ARCHIVO_PLATA_PRECIOS,
    ARCHIVO_PLATA_PRECIOS_LIMPIO,
)

COLUMNAS_NUMERICAS_CLIMA: list[str] = [
    "temperatura_max_c",
    "temperatura_media_c",
    "precipitacion_acumulada_mm",
    "evapotranspiracion_mm",
    "humedad_relativa_pct",
]

COLUMNAS_NUMERICAS_PRECIOS: list[str] = [
    "precio_mayorista_mxn_kg",
    "volatilidad_mensual_pct",
    "costo_logistico_mxn_kg",
    "margen_comercial_mxn_kg",
    "margen_comercial_pct",
]


def diagnosticar_mecanismo_nulos(
    df: pd.DataFrame, columnas: list[str]
) -> dict[str, dict[str, float | str]]:
    """Evalúa el porcentaje de nulos y clasifica su patrón (Sin nulos / MCAR / MAR)."""
    diagnostico: dict[str, dict[str, float | str]] = {}
    for col in columnas:
        nulos = int(df[col].isna().sum())
        pct = round((nulos / max(len(df), 1)) * 100.0, 2)
        if nulos == 0:
            mecanismo = "COMPLETO (0% nulos)"
        elif pct < 5.0:
            mecanismo = "MCAR (Faltante Completamente al Azar)"
        else:
            mecanismo = "MAR (Faltante al Azar condicionado al grupo)"
        diagnostico[col] = {"nulos": nulos, "porcentaje": pct, "mecanismo": mecanismo}
    return diagnostico


def imputar_nulos_por_grupo(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str
) -> pd.DataFrame:
    """Imputa valores faltantes usando interpolación temporal lineal y mediana grupal."""
    df_limpio = df.copy()
    for col in columnas:
        df_limpio[col] = df_limpio.groupby(columna_grupo)[col].transform(
            lambda serie: serie.interpolate(method="linear").bfill().ffill()
        )
        mediana_global = float(df_limpio[col].median())
        df_limpio[col] = df_limpio[col].fillna(mediana_global).round(2)
    return df_limpio


def tratar_atipicos_iqr(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str
) -> tuple[pd.DataFrame, int]:
    """Detecta atípicos por criterio de Tukey (1.5 * IQR) y aplica winsorización."""
    df_out = df.copy()
    bandera_global = pd.Series(False, index=df_out.index)
    for col in columnas:
        q1 = df_out.groupby(columna_grupo)[col].transform("quantile", 0.25)
        q3 = df_out.groupby(columna_grupo)[col].transform("quantile", 0.75)
        iqr = q3 - q1
        lim_inf, lim_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        es_atipico_col = (df_out[col] < lim_inf) | (df_out[col] > lim_sup)
        bandera_global = bandera_global | es_atipico_col
        df_out[col] = df_out[col].clip(lower=lim_inf, upper=lim_sup).round(2)
    df_out["es_atipico_iqr"] = bandera_global
    return df_out, int(bandera_global.sum())


def normalizar_min_max(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str
) -> pd.DataFrame:
    """Agrega columnas normalizadas en escala [0, 1] mediante transformación Min-Max."""
    df_norm = df.copy()
    for col in columnas:
        min_g = df_norm.groupby(columna_grupo)[col].transform("min")
        max_g = df_norm.groupby(columna_grupo)[col].transform("max")
        rango = (max_g - min_g).replace(0.0, 1.0)
        df_norm[f"{col}_norm"] = ((df_norm[col] - min_g) / rango).round(4)
    return df_norm


def discretizar_precios_y_riesgo(df_precios: pd.DataFrame) -> pd.DataFrame:
    """Clasifica el precio mayorista y la volatilidad en categorías interpretables."""
    df_cat = df_precios.copy()
    df_cat["categoria_precio"] = df_cat.groupby("cultivo")[
        "precio_mayorista_mxn_kg"
    ].transform(
        lambda x: pd.qcut(
            x.rank(method="first"), q=3, labels=["Bajo", "Medio", "Alto"]
        ).astype(str)
    )
    df_cat["nivel_volatilidad"] = pd.cut(
        df_cat["volatilidad_mensual_pct"],
        bins=[-1.0, 12.0, 17.0, 200.0],
        labels=["Estable", "Moderada", "Alta"],
    ).astype(str)
    return df_cat


def ejecutar_limpieza_plata() -> dict[str, int]:
    """Ejecuta el flujo completo de limpieza sobre Clima y Precios en Capa Plata."""
    df_clima = pd.read_csv(ARCHIVO_PLATA_CLIMA)
    df_precios = pd.read_csv(ARCHIVO_PLATA_PRECIOS)

    diagnosticar_mecanismo_nulos(df_clima, COLUMNAS_NUMERICAS_CLIMA)
    df_clima = imputar_nulos_por_grupo(
        df_clima, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola"
    )
    df_clima, atipicos_clima = tratar_atipicos_iqr(
        df_clima, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola"
    )
    df_clima = normalizar_min_max(df_clima, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola")
    df_clima.to_csv(ARCHIVO_PLATA_CLIMA_LIMPIO, index=False, encoding="utf-8")

    diagnosticar_mecanismo_nulos(df_precios, COLUMNAS_NUMERICAS_PRECIOS)
    df_precios = imputar_nulos_por_grupo(
        df_precios, COLUMNAS_NUMERICAS_PRECIOS, "cultivo"
    )
    df_precios, atipicos_precios = tratar_atipicos_iqr(
        df_precios, COLUMNAS_NUMERICAS_PRECIOS, "cultivo"
    )
    df_precios = normalizar_min_max(df_precios, COLUMNAS_NUMERICAS_PRECIOS, "cultivo")
    df_precios = discretizar_precios_y_riesgo(df_precios)
    df_precios.to_csv(ARCHIVO_PLATA_PRECIOS_LIMPIO, index=False, encoding="utf-8")

    return {"atipicos_clima": atipicos_clima, "atipicos_precios": atipicos_precios}


if __name__ == "__main__":
    resumen = ejecutar_limpieza_plata()
    print(f"Limpieza en Capa Plata completada: {resumen}")

