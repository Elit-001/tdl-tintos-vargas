"""Pruebas unitarias de la Puerta de Calidad, Limpieza e Integración (Entrega E1).

Verifica que Pandera desvíe registros corruptos a Cuarentena con motivo_rechazo
(0% borrado silencioso) y que Capa Oro cumpla completitud >= 98%.
"""

import pandas as pd

from config import (
    ARCHIVO_CUARENTENA_CLIMA,
    ARCHIVO_CUARENTENA_PRECIOS,
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_PLATA_CLIMA_LIMPIO,
    ARCHIVO_PLATA_PRECIOS_LIMPIO,
)
from pipeline.puerta_calidad import crear_esquema_precios, validar_lote_bronce


def test_puerta_calidad_envia_corruptos_a_cuarentena() -> None:
    """Comprueba que un precio negativo vaya a cuarentena con motivo_rechazo."""
    base = {
        "periodo_mensual": "2026-10",
        "cultivo": "Limón Mexicano",
        "central_abasto": "Guadalajara",
        "variedad_sniim": "Limón c/semilla # 2 - Primera",
        "volatilidad_mensual_pct": 14.2,
        "costo_logistico_mxn_kg": 2.15,
        "margen_comercial_mxn_kg": 9.10,
        "margen_comercial_pct": 37.1,
        "fecha_captura": "2026-11-10",
        "fuente_origen": "sniim_web_verificado",
    }
    df_prueba = pd.DataFrame([
        {**base, "precio_mayorista_mxn_kg": 24.50},
        {**base, "precio_mayorista_mxn_kg": -15.00},
    ])
    df_plata, df_cuarentena = validar_lote_bronce(df_prueba, crear_esquema_precios())
    assert len(df_plata) == 1
    assert len(df_cuarentena) == 1
    assert len(df_plata) + len(df_cuarentena) == len(df_prueba)
    assert "motivo_rechazo" in df_cuarentena.columns
    assert "precio_mayorista_mxn_kg" in str(df_cuarentena.iloc[0]["motivo_rechazo"])


def test_existencia_y_completitud_capa_oro() -> None:
    """Verifica que existan los artefactos de Plata, Cuarentena y Oro con >= 98% completitud."""
    rutas = [
        ARCHIVO_CUARENTENA_CLIMA,
        ARCHIVO_CUARENTENA_PRECIOS,
        ARCHIVO_PLATA_CLIMA_LIMPIO,
        ARCHIVO_PLATA_PRECIOS_LIMPIO,
        ARCHIVO_ORO_ANALITICO,
        ARCHIVO_DICCIONARIO_ORO,
    ]
    for ruta in rutas:
        assert ruta.exists(), f"Falta el archivo esperado de E1: {ruta}"

    df_oro = pd.read_csv(ARCHIVO_ORO_ANALITICO)
    completitud = (1.0 - float(df_oro.isna().mean().mean())) * 100.0
    assert len(df_oro) == 768
    assert completitud >= 98.0
    assert "categoria_precio" in df_oro.columns
    assert "precio_mayorista_mxn_kg_norm" in df_oro.columns
    assert "temperatura_max_c" in df_oro.columns
