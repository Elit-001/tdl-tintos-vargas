"""Puerta de Calidad Automatizada con Pandera (Transición Bronce -> Plata / Cuarentena).

Cumple el criterio E1 de Ingeniería de Datos y Calidad en SI (ISO/IEC 25012):
valida esquemas y rangos físicos/económicos sin realizar borrado silencioso,
enviando todo registro inválido a data/cuarentena/ con su motivo_rechazo.
"""

from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from config import (
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_CUARENTENA_CLIMA,
    ARCHIVO_CUARENTENA_PRECIOS,
    ARCHIVO_PLATA_CLIMA,
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
    return pa.Column(float, pa.Check.in_range(min_val, max_val), nullable=nulo, coerce=True)


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
        return df_bronce.copy(), df_cuarentena_vacio
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
) -> dict[str, int]:
    """Valida un archivo de Bronce y persiste sus salidas en Plata y Cuarentena."""
    DATA_PLATA.mkdir(parents=True, exist_ok=True)
    DATA_CUARENTENA.mkdir(parents=True, exist_ok=True)
    df_bronce = pd.read_csv(ruta_bronce)
    df_plata, df_cuarentena = validar_lote_bronce(df_bronce, esquema)
    df_plata.to_csv(ruta_plata, index=False, encoding="utf-8")
    df_cuarentena.to_csv(ruta_cuarentena, index=False, encoding="utf-8")
    return {
        "bronce": len(df_bronce),
        "plata": len(df_plata),
        "cuarentena": len(df_cuarentena),
    }


def ejecutar_puerta_calidad() -> dict[str, dict[str, int]]:
    """Ejecuta la puerta de calidad sobre precios y clima garantizando 0% pérdida."""
    res_clima = procesar_archivo_bronce(
        ARCHIVO_CLIMA_MENSUAL,
        crear_esquema_clima(),
        ARCHIVO_PLATA_CLIMA,
        ARCHIVO_CUARENTENA_CLIMA,
    )
    res_precios = procesar_archivo_bronce(
        ARCHIVO_PRECIOS_MENSUAL,
        crear_esquema_precios(),
        ARCHIVO_PLATA_PRECIOS,
        ARCHIVO_CUARENTENA_PRECIOS,
    )
    return {"clima": res_clima, "precios": res_precios}


if __name__ == "__main__":
    resultado = ejecutar_puerta_calidad()
    print(f"Puerta de calidad completada: {resultado}")
