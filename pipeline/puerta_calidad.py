"""Puerta de Calidad Automatizada con Pandera (Transición Bronce -> Plata / Cuarentena).

Cumple los criterios E1-E3 de Ingeniería de Datos y Calidad en SI (ISO/IEC 25012):
valida esquemas cacheados en memoria sin borrado silencioso, enviando anomalías a
data/cuarentena/ con motivo_rechazo y entregando DataFrames en memoria para E3.
"""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from config import (
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_CUARENTENA_CLIMA,
    ARCHIVO_CUARENTENA_GEOESPACIAL,
    ARCHIVO_CUARENTENA_PRECIOS,
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_PLATA_CLIMA,
    ARCHIVO_PLATA_GEOESPACIAL,
    ARCHIVO_PLATA_PRECIOS,
    ARCHIVO_PRECIOS_MENSUAL,
    CENTRALES_ABASTO,
    CULTIVOS_OBJETIVO,
    DATA_CUARENTENA,
    DATA_PLATA,
    ZONAS_AGRICOLAS_COLIMA,
)


def _col_rango(min_val: float, max_val: float, nulo: bool = True) -> pa.Column:
    """Crea una columna numérica Pandera con validación de rango físico o económico."""
    return pa.Column(
        float, pa.Check.in_range(min_val, max_val), nullable=nulo, coerce=True
    )


def crear_esquema_clima() -> pa.DataFrameSchema:
    """Define el contrato estricto de validación Pandera para datos hidroclimáticos."""
    zonas = list(ZONAS_AGRICOLAS_COLIMA.keys())
    return pa.DataFrameSchema(
        {
            "periodo_mensual": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}$")),
            "zona_agricola": pa.Column(str, pa.Check.isin(zonas)),
            "latitud": _col_rango(18.0, 20.0, nulo=False),
            "longitud": _col_rango(-105.0, -103.0, nulo=False),
            "temperatura_max_c": _col_rango(15.0, 48.0),
            "temperatura_media_c": _col_rango(10.0, 42.0),
            "precipitacion_acumulada_mm": _col_rango(0.0, 1500.0),
            "evapotranspiracion_mm": _col_rango(0.0, 400.0),
            "humedad_relativa_pct": _col_rango(10.0, 100.0),
            "fecha_captura": pa.Column(str, nullable=False),
            "fuente_origen": pa.Column(str, nullable=False),
        },
        strict=False,
    )


def crear_esquema_precios() -> pa.DataFrameSchema:
    """Define el contrato estricto de validación Pandera para precios mayoristas."""
    return pa.DataFrameSchema(
        {
            "periodo_mensual": pa.Column(str, pa.Check.str_matches(r"^\d{4}-\d{2}$")),
            "cultivo": pa.Column(str, pa.Check.isin(CULTIVOS_OBJETIVO)),
            "central_abasto": pa.Column(str, pa.Check.isin(CENTRALES_ABASTO)),
            "variedad_sniim": pa.Column(str, nullable=False),
            "precio_mayorista_mxn_kg": _col_rango(1.0, 250.0),
            "volatilidad_mensual_pct": _col_rango(0.0, 100.0),
            "costo_logistico_mxn_kg": _col_rango(0.1, 50.0),
            "margen_comercial_mxn_kg": _col_rango(-50.0, 200.0),
            "margen_comercial_pct": _col_rango(-100.0, 100.0),
            "fecha_captura": pa.Column(str, nullable=False),
            "fuente_origen": pa.Column(str, nullable=False),
        },
        strict=False,
    )


def crear_esquema_geoespacial() -> pa.DataFrameSchema:
    """Define el contrato Pandera para nodos productores y compradores en Colima."""
    tipos_validos = ["PRODUCTOR_ORIGEN", "COMPRADOR_ANCLA"]
    return pa.DataFrameSchema(
        {
            "id_nodo": pa.Column(str, nullable=False),
            "nombre_nodo": pa.Column(str, nullable=False),
            "tipo_nodo": pa.Column(str, pa.Check.isin(tipos_validos)),
            "municipio": pa.Column(str, nullable=False),
            "latitud": _col_rango(18.7, 19.5, nulo=False),
            "longitud": _col_rango(-104.6, -103.4, nulo=False),
            "capacidad_lote_kg": _col_rango(50.0, 5000.0, nulo=False),
            "prima_comercial_pct": _col_rango(0.0, 35.0, nulo=False),
            "fecha_captura": pa.Column(str, nullable=False),
            "fuente_origen": pa.Column(str, nullable=False),
        },
        strict=False,
    )


ESQUEMA_CLIMA_CACHE: pa.DataFrameSchema = crear_esquema_clima()
ESQUEMA_PRECIOS_CACHE: pa.DataFrameSchema = crear_esquema_precios()
ESQUEMA_GEO_CACHE: pa.DataFrameSchema = crear_esquema_geoespacial()


def construir_motivos_rechazo(tabla_fallos: pd.DataFrame) -> pd.Series:
    """Agrupa los fallos detectados por Pandera por índice de fila en texto claro."""
    fallos_fila = tabla_fallos.dropna(subset=["index"]).copy()
    fallos_fila["index"] = fallos_fila["index"].astype(int)
    fallos_fila["detalle"] = (
        fallos_fila["column"].astype(str) + ": " + fallos_fila["check"].astype(str)
    )
    return fallos_fila.groupby("index")["detalle"].apply(
        lambda items: " | ".join(sorted(set(items)))
    )


def validar_lote_bronce(
    df_bronce: pd.DataFrame, esquema: pa.DataFrameSchema
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa registros válidos (Plata) y rechazados (Cuarentena) sin borrado silencioso."""
    try:
        esquema.validate(df_bronce, lazy=True)
        df_cuarentena_vacio = pd.DataFrame(
            columns=[*list(df_bronce.columns), "motivo_rechazo"]
        )
        return df_bronce, df_cuarentena_vacio
    except pa.errors.SchemaErrors as error_esquema:
        resumen_motivos = construir_motivos_rechazo(error_esquema.failure_cases)
        idx_malos = resumen_motivos.index
        df_plata = df_bronce.loc[~df_bronce.index.isin(idx_malos)].copy()
        df_cuarentena = df_bronce.loc[df_bronce.index.isin(idx_malos)].copy()
        df_cuarentena["motivo_rechazo"] = df_cuarentena.index.map(resumen_motivos)
        return df_plata.reset_index(drop=True), df_cuarentena.reset_index(drop=True)


def procesar_archivo_bronce(
    ruta_bronce: Path,
    esquema: pa.DataFrameSchema,
    ruta_plata: Path,
    ruta_cuarentena: Path,
) -> tuple[dict[str, int], pd.DataFrame]:
    """Valida un archivo Bronce, persiste salidas LF y devuelve el DataFrame en memoria."""
    DATA_PLATA.mkdir(parents=True, exist_ok=True)
    DATA_CUARENTENA.mkdir(parents=True, exist_ok=True)
    df_bronce = pd.read_csv(ruta_bronce)
    df_plata, df_cuarentena = validar_lote_bronce(df_bronce, esquema)
    df_plata.to_csv(ruta_plata, index=False, encoding="utf-8", lineterminator="\n")
    df_cuarentena.to_csv(
        ruta_cuarentena, index=False, encoding="utf-8", lineterminator="\n"
    )
    conteos = {
        "bronce": len(df_bronce),
        "plata": len(df_plata),
        "cuarentena": len(df_cuarentena),
    }
    return conteos, df_plata


def ejecutar_puerta_calidad_en_memoria() -> (
    tuple[dict[str, dict[str, int]], dict[str, pd.DataFrame]]
):
    """Ejecuta la validación con esquemas cacheados y retorna conteos y DataFrames."""
    c_cl, df_cl = procesar_archivo_bronce(
        ARCHIVO_CLIMA_MENSUAL,
        ESQUEMA_CLIMA_CACHE,
        ARCHIVO_PLATA_CLIMA,
        ARCHIVO_CUARENTENA_CLIMA,
    )
    c_pr, df_pr = procesar_archivo_bronce(
        ARCHIVO_PRECIOS_MENSUAL,
        ESQUEMA_PRECIOS_CACHE,
        ARCHIVO_PLATA_PRECIOS,
        ARCHIVO_CUARENTENA_PRECIOS,
    )
    conteos = {"clima": c_cl, "precios": c_pr}
    marcos = {"clima": df_cl, "precios": df_pr}
    if ARCHIVO_GEOESPACIAL_NODOS.exists():
        c_geo, df_geo = procesar_archivo_bronce(
            ARCHIVO_GEOESPACIAL_NODOS,
            ESQUEMA_GEO_CACHE,
            ARCHIVO_PLATA_GEOESPACIAL,
            ARCHIVO_CUARENTENA_GEOESPACIAL,
        )
        conteos["geoespacial"] = c_geo
        marcos["geoespacial"] = df_geo
    return conteos, marcos


def ejecutar_puerta_calidad() -> dict[str, dict[str, int]]:
    """Ejecuta la puerta de calidad sobre clima, precios y nodos geoespaciales."""
    conteos, _ = ejecutar_puerta_calidad_en_memoria()
    return conteos


if __name__ == "__main__":
    resultado = ejecutar_puerta_calidad()
    print(f"Puerta de calidad completada: {resultado}")
