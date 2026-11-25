"""Módulo de Publicación Abierta del Dataset Curado para Terceros (Entrega E3).

Cumple el criterio E3 de Ingeniería de Datos y Gobernanza: consolida un dataset
curado libre de PII (data/publicado/agropulse_colima_curado.csv y .parquet) con
licencia abierta CC BY 4.0, guía rápida de consumo y trazabilidad SHA-256 intacta.
"""

import pandas as pd

from config import (
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PUBLICADO_CSV,
    ARCHIVO_PUBLICADO_LICENCIA,
    ARCHIVO_PUBLICADO_PARQUET,
    ARCHIVO_PUBLICADO_README,
    COLUMNAS_LINAJE_ORO,
    DATA_PUBLICADO,
    NOMBRE_OBSERVATORIO,
)

COLUMNAS_SELECCION_PUBLICADO: list[str] = [
    "periodo_mensual",
    "cultivo",
    "variedad_sniim",
    "zona_agricola",
    "central_abasto",
    "precio_mayorista_mxn_kg",
    "volatilidad_mensual_pct",
    "costo_logistico_mxn_kg",
    "margen_comercial_mxn_kg",
    "margen_comercial_pct",
    "categoria_precio",
    "nivel_volatilidad",
    "temperatura_max_c",
    "temperatura_media_c",
    "precipitacion_acumulada_mm",
    "evapotranspiracion_mm",
    "humedad_relativa_pct",
    "comprador_ancla_optimo_colima",
    "distancia_vial_optima_km",
    "flete_local_400kg_mxn_kg",
    "spread_brokerage_colima_mxn_kg",
    "linaje_sha256_clima_bronce",
    *COLUMNAS_LINAJE_ORO,
]

TEXTO_LICENCIA_CC_BY_40: str = """Creative Commons Attribution 4.0 International (CC BY 4.0)

Conjunto de Datos Abiertos: AgroPulse TDL — Observatorio Agrocomercial y Climático de Colima
Autores: Proyecto Integrador Trusted Data Lab (Ingeniería de Datos, Estadística y SQA)
URL Oficial de Licencia: https://creativecommons.org/licenses/by/4.0/deed.es

Usted es libre de:
1. Compartir — copiar y redistribuir el material en cualquier medio o formato.
2. Adaptar — remezclar, transformar y construir a partir del material para cualquier
   propósito, incluso comercialmente.

Bajo los siguientes términos:
- Atribución (BY): Usted debe dar crédito de manera adecuada al Observatorio AgroPulse TDL
  y a sus fuentes primarias abiertas (Open-Meteo CC BY 4.0, SNIIM Datos Abiertos MX y
  OpenStreetMap ODbL 1.0), brindar un enlace a la licencia e indicar si se realizaron cambios.
- Sin restricciones adicionales: No puede aplicar términos legales ni medidas tecnológicas
  que restrinjan legalmente a otros a hacer cualquier uso permitido por la licencia.
- Privacidad garantizada: Este dataset contiene 0% de Datos Personales Identificables (PII).
"""


def enriquecer_con_ruta_optima_local(
    df_oro: pd.DataFrame, df_rutas: pd.DataFrame
) -> pd.DataFrame:
    """Integra la ruta óptima hacia comprador ancla en Colima por zona de origen."""
    df_opt = (
        df_rutas[df_rutas["es_ruta_optima"]]
        .rename(
            columns={
                "nodo_productor": "zona_agricola",
                "comprador_ancla": "comprador_ancla_optimo_colima",
                "distancia_vial_km": "distancia_vial_optima_km",
                "costo_flete_mxn_kg": "flete_local_400kg_mxn_kg",
                "spread_neto_mxn_kg": "spread_brokerage_colima_mxn_kg",
            }
        )[
            [
                "zona_agricola",
                "comprador_ancla_optimo_colima",
                "distancia_vial_optima_km",
                "flete_local_400kg_mxn_kg",
                "spread_brokerage_colima_mxn_kg",
            ]
        ]
        .drop_duplicates(subset=["zona_agricola"])
    )
    df_pub = pd.merge(df_oro, df_opt, on="zona_agricola", how="left")
    df_pub["linaje_id_registro"] = [
        f"PUB-E3-{idx:05d}" for idx in range(1, len(df_pub) + 1)
    ]
    return df_pub[COLUMNAS_SELECCION_PUBLICADO]


def optimizar_tipos_parquet(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte categorías y flotantes a tipos compactos para exportación Parquet."""
    df_pq = df.copy()
    cols_cat = [
        "cultivo",
        "variedad_sniim",
        "zona_agricola",
        "central_abasto",
        "categoria_precio",
        "nivel_volatilidad",
        "comprador_ancla_optimo_colima",
    ]
    for col in cols_cat:
        if col in df_pq.columns:
            df_pq[col] = df_pq[col].astype("category")
    for col in df_pq.select_dtypes(include=["float64"]).columns:
        df_pq[col] = df_pq[col].astype("float32")
    return df_pq


def escribir_metadatos_publicacion(filas: int, cols: int) -> None:
    """Genera los archivos LICENSE (CC BY 4.0) y README.md de consumo externo."""
    ARCHIVO_PUBLICADO_LICENCIA.write_text(
        TEXTO_LICENCIA_CC_BY_40, encoding="utf-8", newline="\n"
    )
    guia_md = (
        f"# Dataset Público Curado — {NOMBRE_OBSERVATORIO} (Entrega E3)\n\n"
        f"* **Archivo CSV (multiplataforma LF):** `agropulse_colima_curado.csv` (`{filas}` filas × `{cols}` columnas)\n"
        "* **Archivo Columnar Optimizado:** `agropulse_colima_curado.parquet`\n"
        "* **Licencia Abierta:** Creative Commons Attribution 4.0 International (`CC BY 4.0` — ver `LICENSE`)\n"
        "* **Ficha Técnica Completa (Datasheet):** [`docs/E3/datasheet.md`](../../docs/E3/datasheet.md)\n"
        "* **Privacidad:** `0%` Datos Personales Identificables (PII).\n\n"
        "## Ejemplo Rápido de Carga en Python\n"
        "```python\n"
        "import pandas as pd\n\n"
        "df = pd.read_csv('data/publicado/agropulse_colima_curado.csv')\n"
        "print(df[['periodo_mensual', 'cultivo', 'precio_mayorista_mxn_kg', 'spread_brokerage_colima_mxn_kg']].head())\n"
        "```\n"
    )
    ARCHIVO_PUBLICADO_README.write_text(guia_md, encoding="utf-8", newline="\n")


def publicar_dataset_curado(
    df_oro: pd.DataFrame | None = None, df_rutas: pd.DataFrame | None = None
) -> dict[str, int | float]:
    """Genera el paquete de datos abiertos en data/publicado/ en CSV LF y Parquet."""
    DATA_PUBLICADO.mkdir(parents=True, exist_ok=True)
    df_base = df_oro if df_oro is not None else pd.read_csv(ARCHIVO_ORO_ANALITICO)
    df_geo = df_rutas if df_rutas is not None else pd.read_csv(ARCHIVO_ORO_RUTAS_FLETE)
    df_curado = enriquecer_con_ruta_optima_local(df_base, df_geo)
    df_curado.to_csv(
        ARCHIVO_PUBLICADO_CSV, index=False, encoding="utf-8", lineterminator="\n"
    )
    df_pq = optimizar_tipos_parquet(df_curado)
    df_pq.to_parquet(ARCHIVO_PUBLICADO_PARQUET, index=False)
    escribir_metadatos_publicacion(len(df_curado), len(df_curado.columns))
    kb_csv = round(ARCHIVO_PUBLICADO_CSV.stat().st_size / 1024.0, 2)
    kb_pq = round(ARCHIVO_PUBLICADO_PARQUET.stat().st_size / 1024.0, 2)
    return {
        "filas_publicadas": len(df_curado),
        "columnas_publicadas": len(df_curado.columns),
        "tamano_csv_kb": kb_csv,
        "tamano_parquet_kb": kb_pq,
    }


if __name__ == "__main__":
    resumen = publicar_dataset_curado()
    print(f"Dataset curado publicado exitosamente: {resumen}")
