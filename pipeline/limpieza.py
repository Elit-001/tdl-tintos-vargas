"""Módulo de Limpieza Estadística Vectorizada en Capa Plata (Entregas E1 y E3).

Cumple los criterios E1 y E3 de Ingeniería de Datos: diagnóstico MCAR/MAR,
imputación condicional sin bucles innecesarios, winsorización IQR matricial
vectorizada, escalado Min-Max en bloque y reducción de copias en memoria RAM.
"""

import numpy as np
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
    """Evalúa vectorizadamente el porcentaje de nulos y clasifica MCAR / MAR."""
    conteo_nulos = df[columnas].isna().sum()
    total = max(len(df), 1)
    diagnostico: dict[str, dict[str, float | str]] = {}
    for col in columnas:
        nulos = int(conteo_nulos[col])
        pct = round((nulos / total) * 100.0, 2)
        if nulos == 0:
            mecanismo = "COMPLETO (0% nulos)"
        elif pct < 5.0:
            mecanismo = "MCAR (Faltante Completamente al Azar)"
        else:
            mecanismo = "MAR (Faltante al Azar condicionado al grupo)"
        diagnostico[col] = {"nulos": nulos, "porcentaje": pct, "mecanismo": mecanismo}
    return diagnostico


def imputar_nulos_por_grupo(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str, en_sitio: bool = False
) -> pd.DataFrame:
    """Imputa nulos por interpolación grupal solo cuando existen celdas vacías."""
    df_limpio = df if en_sitio else df.copy()
    matriz = df_limpio[columnas].to_numpy(dtype=float, copy=False)
    if not bool(np.isnan(matriz).any()):
        df_limpio[columnas] = np.round(matriz, 2)
        return df_limpio
    for col in columnas:
        if df_limpio[col].isna().any():
            df_limpio[col] = df_limpio.groupby(columna_grupo, observed=True)[
                col
            ].transform(lambda s: s.interpolate(method="linear").bfill().ffill())
            df_limpio[col] = df_limpio[col].fillna(float(df_limpio[col].median()))
    df_limpio[columnas] = df_limpio[columnas].round(2)
    return df_limpio


def tratar_atipicos_iqr(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str, en_sitio: bool = False
) -> tuple[pd.DataFrame, int]:
    """Detecta atípicos por Tukey (1.5 * IQR) y winsoriza con NumPy sin copias extra."""
    df_out = df if en_sitio else df.copy()
    codigos, _ = pd.factorize(df_out[columna_grupo], sort=False)
    mat = df_out[columnas].to_numpy(dtype=float, copy=True)
    lim_inf = np.empty_like(mat)
    lim_sup = np.empty_like(mat)
    for g in range(int(codigos.max()) + 1):
        idx = codigos == g
        q1, q3 = np.quantile(mat[idx], [0.25, 0.75], axis=0)
        iqr = q3 - q1
        lim_inf[idx] = q1 - 1.5 * iqr
        lim_sup[idx] = q3 + 1.5 * iqr
    mascara = (mat < lim_inf) | (mat > lim_sup)
    bandera = mascara.any(axis=1)
    df_out[columnas] = np.round(np.clip(mat, lim_inf, lim_sup), 2)
    df_out["es_atipico_iqr"] = bandera
    return df_out, int(bandera.sum())


def normalizar_min_max(
    df: pd.DataFrame, columnas: list[str], columna_grupo: str, en_sitio: bool = False
) -> pd.DataFrame:
    """Agrega columnas normalizadas [0, 1] mediante cálculo matricial en NumPy."""
    df_norm = df if en_sitio else df.copy()
    codigos, _ = pd.factorize(df_norm[columna_grupo], sort=False)
    mat = df_norm[columnas].to_numpy(dtype=float, copy=False)
    res = np.empty_like(mat)
    for g in range(int(codigos.max()) + 1):
        idx = codigos == g
        mn = mat[idx].min(axis=0)
        mx = mat[idx].max(axis=0)
        rango = np.where((mx - mn) == 0.0, 1.0, mx - mn)
        res[idx] = np.round((mat[idx] - mn) / rango, 4)
    for i, col in enumerate(columnas):
        df_norm[f"{col}_norm"] = res[:, i]
    return df_norm


def discretizar_precios_y_riesgo(
    df_precios: pd.DataFrame, en_sitio: bool = False
) -> pd.DataFrame:
    """Clasifica vectorizadamente precio mayorista y volatilidad en categorías."""
    df_cat = df_precios if en_sitio else df_precios.copy()
    rangos_pct = df_cat.groupby("cultivo", observed=True)[
        "precio_mayorista_mxn_kg"
    ].rank(method="first", pct=True)
    df_cat["categoria_precio"] = np.select(
        [rangos_pct <= (1.0 / 3.0), rangos_pct <= (2.0 / 3.0)],
        ["Bajo", "Medio"],
        default="Alto",
    )
    vol = df_cat["volatilidad_mensual_pct"].to_numpy()
    df_cat["nivel_volatilidad"] = np.select(
        [vol <= 12.0, vol <= 17.0],
        ["Estable", "Moderada"],
        default="Alta",
    )
    return df_cat


def limpiar_marcos_en_memoria(
    df_clima: pd.DataFrame, df_precios: pd.DataFrame
) -> tuple[dict[str, int], pd.DataFrame, pd.DataFrame]:
    """Limpia Clima y Precios con una sola copia de trabajo y persiste CSV LF."""
    df_cl = df_clima.copy()
    diagnosticar_mecanismo_nulos(df_cl, COLUMNAS_NUMERICAS_CLIMA)
    imputar_nulos_por_grupo(df_cl, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola", True)
    _, at_cl = tratar_atipicos_iqr(
        df_cl, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola", True
    )
    normalizar_min_max(df_cl, COLUMNAS_NUMERICAS_CLIMA, "zona_agricola", True)
    df_cl.to_csv(
        ARCHIVO_PLATA_CLIMA_LIMPIO, index=False, encoding="utf-8", lineterminator="\n"
    )

    df_pr = df_precios.copy()
    diagnosticar_mecanismo_nulos(df_pr, COLUMNAS_NUMERICAS_PRECIOS)
    imputar_nulos_por_grupo(df_pr, COLUMNAS_NUMERICAS_PRECIOS, "cultivo", True)
    _, at_pr = tratar_atipicos_iqr(df_pr, COLUMNAS_NUMERICAS_PRECIOS, "cultivo", True)
    normalizar_min_max(df_pr, COLUMNAS_NUMERICAS_PRECIOS, "cultivo", True)
    discretizar_precios_y_riesgo(df_pr, True)
    df_pr.to_csv(
        ARCHIVO_PLATA_PRECIOS_LIMPIO, index=False, encoding="utf-8", lineterminator="\n"
    )
    return {"atipicos_clima": at_cl, "atipicos_precios": at_pr}, df_cl, df_pr


def ejecutar_limpieza_plata() -> dict[str, int]:
    """Ejecuta el flujo completo de limpieza sobre Clima y Precios en Capa Plata."""
    df_clima = pd.read_csv(ARCHIVO_PLATA_CLIMA)
    df_precios = pd.read_csv(ARCHIVO_PLATA_PRECIOS)
    resumen, _, _ = limpiar_marcos_en_memoria(df_clima, df_precios)
    return resumen


if __name__ == "__main__":
    resumen = ejecutar_limpieza_plata()
    print(f"Limpieza en Capa Plata completada: {resumen}")

