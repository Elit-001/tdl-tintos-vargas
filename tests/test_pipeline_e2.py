"""Pruebas unitarias de Ingeniería Geoespacial y Linaje Total SHA-256 (Entrega E2).

Verifica:
1. Cero nulos en las 5 columnas obligatorias de linaje en todos los archivos de data/oro/.
2. Coincidencia exacta entre linaje_sha256_bronce en Oro y los archivos .meta.json en Bronce.
3. Cálculo geoespacial válido con GeoPandas (distancias en km > 0 y costos de flete > 0).
"""

import json

import geopandas as gpd
import pandas as pd

from config import (
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_GEOJSON_RUTAS,
    ARCHIVO_ORO_RUTAS_FLETE,
    COLUMNAS_LINAJE_ORO,
    DATA_BRONCE,
    DATA_ORO,
)
from extractores.base import ExtractorEtico


def test_cero_nulos_columnas_linaje_en_oro() -> None:
    """Comprueba que todos los CSV de data/oro/ incluyan las 5 columnas de linaje sin nulos."""
    archivos_oro = sorted(DATA_ORO.glob("*.csv"))
    assert len(archivos_oro) >= 2, "Deben existir al menos dataset_analitico y rutas_flete en Oro"
    for ruta_oro in archivos_oro:
        df = pd.read_csv(ruta_oro)
        for col in COLUMNAS_LINAJE_ORO:
            assert col in df.columns, f"Falta columna de linaje {col} en {ruta_oro.name}"
            assert int(df[col].isna().sum()) == 0, f"Existen nulos en {col} de {ruta_oro.name}"
            assert (df[col].astype(str).str.len() > 0).all()
        assert df["linaje_id_registro"].is_unique, f"IDs no únicos en {ruta_oro.name}"


def test_coincidencia_exacta_sha256_oro_con_meta_bronce() -> None:
    """Verifica que linaje_sha256_bronce en Oro coincida con data/bronce/*.meta.json."""
    for ruta_oro in sorted(DATA_ORO.glob("*.csv")):
        df = pd.read_csv(ruta_oro)
        for _, fila in df.iterrows():
            nombre_bronce = str(fila["linaje_archivo_bronce"])
            hash_oro = str(fila["linaje_sha256_bronce"])
            ruta_bronce = DATA_BRONCE / nombre_bronce
            ruta_meta = DATA_BRONCE / f"{nombre_bronce}.meta.json"
            assert ruta_bronce.exists(), f"No existe archivo fuente en Bronce: {ruta_bronce}"
            assert ruta_meta.exists(), f"No existe ficha .meta.json: {ruta_meta}"
            datos_meta = json.loads(ruta_meta.read_text(encoding="utf-8"))
            hash_real = ExtractorEtico.calcular_hash_sha256(ruta_bronce)
            assert hash_oro == datos_meta["hash_sha256"]
            assert hash_oro == hash_real


def test_calculo_geoespacial_distancias_y_fletes_colima() -> None:
    """Valida distancias en km > 0, costos de flete > 0 y GeoJSON de rutas en Colima."""
    assert ARCHIVO_GEOESPACIAL_NODOS.exists()
    assert ARCHIVO_ORO_RUTAS_FLETE.exists()
    assert ARCHIVO_ORO_GEOJSON_RUTAS.exists()

    df_rutas = pd.read_csv(ARCHIVO_ORO_RUTAS_FLETE)
    gdf_rutas = gpd.read_file(ARCHIVO_ORO_GEOJSON_RUTAS)

    assert len(df_rutas) == 16
    assert len(gdf_rutas) == 16
    assert (df_rutas["distancia_lineal_km"] > 0.0).all()
    assert (df_rutas["distancia_vial_km"] > 0.0).all()
    assert (df_rutas["costo_flete_lote_400kg_mxn"] > 0.0).all()
    assert (df_rutas["costo_flete_mxn_kg"] > 0.0).all()
    assert int(df_rutas["es_ruta_optima"].sum()) == 4
    assert ARCHIVO_ORO_ANALITICO.exists()

