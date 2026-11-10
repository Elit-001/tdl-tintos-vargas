"""Pruebas unitarias de extractores y validación de Capa Bronce (Entrega E0).

Verifica existencia de archivos crudos, cumplimiento estricto del mínimo de
periodos históricos (> 36 periodos), esquemas de columnas y bitácora de captura.
"""

import pandas as pd

from config import (
    ARCHIVO_CLIMA_DIARIO,
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_PRECIOS_DIARIO,
    ARCHIVO_PRECIOS_MENSUAL,
    CENTRALES_ABASTO,
    COLUMNAS_BITACORA,
    CULTIVOS_OBJETIVO,
    PAUSA_MINIMA_SEGUNDOS,
    PERIODOS_HISTORICOS_META,
    PERIODOS_MINIMOS_RUBRICA,
    RUTA_BITACORA,
    USER_AGENT_ACADEMICO,
)
from extractores.base import ExtractorEtico


def test_configuracion_extractor_etico() -> None:
    """Comprueba que ExtractorEtico configure User-Agent académico y pausa >= 1.5s."""
    extractor = ExtractorEtico(url_base="https://open-meteo.com")
    assert extractor.user_agent == USER_AGENT_ACADEMICO
    assert extractor.pausa_minima >= PAUSA_MINIMA_SEGUNDOS
    assert extractor.sesion.headers.get("User-Agent") == USER_AGENT_ACADEMICO


def test_existencia_archivos_capa_bronce() -> None:
    """Verifica que existan los 4 datasets en data/bronce/ y la bitácora de captura."""
    archivos = [
        ARCHIVO_CLIMA_MENSUAL,
        ARCHIVO_CLIMA_DIARIO,
        ARCHIVO_PRECIOS_MENSUAL,
        ARCHIVO_PRECIOS_DIARIO,
        RUTA_BITACORA,
    ]
    for ruta in archivos:
        assert ruta.exists(), f"No existe el archivo requerido: {ruta}"
        assert ruta.stat().st_size > 0, f"El archivo está vacío: {ruta}"


def test_periodos_y_esquema_clima_bronce() -> None:
    """Valida que clima histórico supere 36 periodos (>= 48) y tenga sus columnas."""
    df_mensual = pd.read_csv(ARCHIVO_CLIMA_MENSUAL)
    df_diario = pd.read_csv(ARCHIVO_CLIMA_DIARIO)
    columnas_clima = {
        "zona_agricola",
        "latitud",
        "longitud",
        "temperatura_max_c",
        "temperatura_media_c",
        "precipitacion_acumulada_mm",
        "evapotranspiracion_mm",
        "humedad_relativa_pct",
        "fecha_captura",
        "fuente_origen",
    }
    periodos = df_mensual["periodo_mensual"].nunique()
    assert periodos > PERIODOS_MINIMOS_RUBRICA
    assert periodos >= PERIODOS_HISTORICOS_META
    assert columnas_clima.issubset(set(df_mensual.columns))
    assert columnas_clima.issubset(set(df_diario.columns))


def test_periodos_y_esquema_precios_bronce() -> None:
    """Valida 48 periodos (768 registros = 48x4x4) y columnas de precios mayoristas."""
    df_mensual = pd.read_csv(ARCHIVO_PRECIOS_MENSUAL)
    df_diario = pd.read_csv(ARCHIVO_PRECIOS_DIARIO)
    columnas_precios = {
        "cultivo",
        "central_abasto",
        "variedad_sniim",
        "precio_mayorista_mxn_kg",
        "volatilidad_mensual_pct",
        "costo_logistico_mxn_kg",
        "margen_comercial_mxn_kg",
        "margen_comercial_pct",
        "fecha_captura",
        "fuente_origen",
    }
    periodos = df_mensual["periodo_mensual"].nunique()
    assert periodos > PERIODOS_MINIMOS_RUBRICA
    assert periodos >= PERIODOS_HISTORICOS_META
    assert len(df_mensual) == 768
    assert set(df_mensual["cultivo"].unique()) == set(CULTIVOS_OBJETIVO)
    assert set(df_mensual["central_abasto"].unique()) == set(CENTRALES_ABASTO)
    assert columnas_precios.issubset(set(df_mensual.columns))
    assert columnas_precios.issubset(set(df_diario.columns))


def test_integridad_bitacora_captura() -> None:
    """Verifica el esquema exacto de calidad/bitacora_captura.csv para MTBF/MTTR."""
    df_bitacora = pd.read_csv(RUTA_BITACORA)
    assert list(df_bitacora.columns) == COLUMNAS_BITACORA
    assert len(df_bitacora) >= 2
    assert (df_bitacora["estado"] == "EXITOSO").all()
    assert (df_bitacora["registros_obtenidos"] > 0).all()

