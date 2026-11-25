"""Pruebas unitarias de Optimización, Dataset Publicado y Benchmark (Entrega E3).

Verifica:
1. Existencia, esquema válido, cero nulos críticos, licencia abierta CC BY 4.0 y
   cero PII en el dataset publicado (data/publicado/agropulse_colima_curado.csv).
2. Equivalencia funcional y preservación exacta del linaje SHA-256 en formato LF.
3. Existencia y validez numérica de calidad/benchmark_e3.csv con mejora medible.
"""

import json
import re

import pandas as pd

from config import (
    ARCHIVO_BENCHMARK_E3,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_PARQUET,
    ARCHIVO_PUBLICADO_CSV,
    ARCHIVO_PUBLICADO_LICENCIA,
    ARCHIVO_PUBLICADO_PARQUET,
    ARCHIVO_PUBLICADO_README,
    COLUMNAS_LINAJE_ORO,
    DATA_BRONCE,
)
from extractores.base import ExtractorEtico

PATRON_CORREO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PATRON_TELEFONO_MX = re.compile(r"\b\d{10}\b")
COLUMNAS_SOSPECHOSAS_PII = {
    "nombre_persona",
    "telefono",
    "celular",
    "correo",
    "email",
    "curp",
    "rfc",
    "direccion_privada",
}


def test_dataset_publicado_esquema_licencia_y_cero_pii() -> None:
    """Valida el paquete abierto en data/publicado/ con CC BY 4.0, 0 nulos y 0 PII."""
    for ruta in (
        ARCHIVO_PUBLICADO_CSV,
        ARCHIVO_PUBLICADO_PARQUET,
        ARCHIVO_PUBLICADO_LICENCIA,
        ARCHIVO_PUBLICADO_README,
    ):
        assert ruta.exists(), f"Falta artefacto de publicación E3: {ruta}"
        assert ruta.stat().st_size > 0, f"Artefacto vacío: {ruta}"

    texto_licencia = ARCHIVO_PUBLICADO_LICENCIA.read_text(encoding="utf-8")
    assert "CC BY 4.0" in texto_licencia
    assert "Creative Commons Attribution 4.0" in texto_licencia

    df_pub = pd.read_csv(ARCHIVO_PUBLICADO_CSV)
    df_pq = pd.read_parquet(ARCHIVO_PUBLICADO_PARQUET)
    assert len(df_pub) == 768
    assert len(df_pq) == 768
    assert int(df_pub.isna().sum().sum()) == 0
    assert COLUMNAS_SOSPECHOSAS_PII.isdisjoint(set(df_pub.columns.str.lower()))

    muestra_texto = " ".join(
        df_pub.select_dtypes(include=["object"]).astype(str).to_numpy().flatten()
    )
    assert PATRON_CORREO.search(muestra_texto) is None, "Se detectó correo PII"
    assert PATRON_TELEFONO_MX.search(muestra_texto) is None, "Se detectó teléfono PII"


def test_preservacion_linaje_sha256_lf_y_equivalencia_oro_publicado() -> None:
    """Verifica formato LF, equivalencia numérica y coincidencia SHA-256 Bronce-Publicado."""
    bytes_pub = ARCHIVO_PUBLICADO_CSV.read_bytes()
    assert b"\r\n" not in bytes_pub, "El CSV publicado debe usar saltos LF puros"
    assert ARCHIVO_ORO_PARQUET.exists()

    df_oro = pd.read_csv(ARCHIVO_ORO_ANALITICO)
    df_pub = pd.read_csv(ARCHIVO_PUBLICADO_CSV)
    pd.testing.assert_series_equal(
        df_oro["precio_mayorista_mxn_kg"],
        df_pub["precio_mayorista_mxn_kg"],
        check_names=False,
    )
    for col in COLUMNAS_LINAJE_ORO:
        assert col in df_pub.columns
        assert int(df_pub[col].isna().sum()) == 0

    nombre_bronce = str(df_pub["linaje_archivo_bronce"].iloc[0])
    hash_pub = str(df_pub["linaje_sha256_bronce"].iloc[0])
    ruta_bronce = DATA_BRONCE / nombre_bronce
    datos_meta = json.loads(
        (DATA_BRONCE / f"{nombre_bronce}.meta.json").read_text(encoding="utf-8")
    )
    assert hash_pub == datos_meta["hash_sha256"]
    assert hash_pub == ExtractorEtico.calcular_hash_sha256(ruta_bronce)


def test_validez_evidencia_benchmark_e3() -> None:
    """Comprueba que calidad/benchmark_e3.csv exista en LF y demuestre mejora real."""
    assert ARCHIVO_BENCHMARK_E3.exists()
    assert b"\r\n" not in ARCHIVO_BENCHMARK_E3.read_bytes()

    df_bench = pd.read_csv(ARCHIVO_BENCHMARK_E3)
    cols_esperadas = {
        "metrica",
        "unidad",
        "antes_e2",
        "despues_e3",
        "mejora_porcentual",
    }
    assert cols_esperadas.issubset(set(df_bench.columns))
    assert len(df_bench) >= 6
    assert (df_bench["antes_e2"] > 0).all()
    assert (df_bench["despues_e3"] > 0).all()

    fila_total = df_bench[df_bench["metrica"] == "tiempo_total_pipeline_ms"].iloc[0]
    fila_io = df_bench[df_bench["metrica"] == "lecturas_disco_por_corrida"].iloc[0]
    fila_alm = df_bench[df_bench["metrica"] == "almacenamiento_capa_oro_kb"].iloc[0]
    assert float(fila_total["despues_e3"]) < float(fila_total["antes_e2"])
    assert float(fila_total["mejora_porcentual"]) > 0.0
    assert float(fila_io["despues_e3"]) < float(fila_io["antes_e2"])
    assert float(fila_alm["despues_e3"]) < float(fila_alm["antes_e2"])
