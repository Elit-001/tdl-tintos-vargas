"""Módulo Geoespacial Estatal (10 Municipios de Colima) con GeoPandas + OSRM Vial.

Reproyecta los 16 nodos de Colima a EPSG:32613 (UTM Zona 13N), consulta distancias
y tiempos reales por carretera pavimentada en OpenStreetMap (OSRM Table API) con
respaldo geométrico UTM, y calcula costos logísticos reales e índice de sinuosidad.
"""

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
import shapely

from config import (
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_ORO_GEOJSON_RUTAS,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PLATA_GEOESPACIAL,
    ARCHIVO_PRECIOS_DIARIO,
    ARCHIVO_PRECIOS_MENSUAL,
    COSTO_FLETE_MXN_POR_KM,
    COSTO_MANIOBRA_LOTE_MXN,
    DATA_ORO,
    EPSG_UTM_COLIMA,
    EPSG_WGS84,
    FACTOR_SINUOSIDAD_VIAL,
    PESO_LOTE_CONSOLIDADO_KG,
    TIMEOUT_HTTP_SEGUNDOS,
    URL_TABLA_OSRM,
    USER_AGENT_ACADEMICO,
)
from extractores.base import ExtractorEtico

PRECIOS_RESPALDO_COLIMA: dict[str, float] = {
    "Limón Mexicano": 24.00,
    "Papaya Maradol": 20.50,
    "Plátano Chiapas": 16.50,
    "Aguacate Hass": 52.00,
}
PRECIOS_BASE_CULTIVO_COLIMA = PRECIOS_RESPALDO_COLIMA

_CACHE_META_BRONCE: dict[str, tuple[int, int, dict[str, str]]] = {}
_CACHE_MATRIZ_OSRM: dict[str, tuple[np.ndarray, np.ndarray]] = {}
_CACHE_PRECIOS_COLIMA: dict[tuple[int, int], dict[str, float]] = {}


def limpiar_cache_metadatos_bronce() -> None:
    """Limpia la caché en memoria de metadatos SHA-256 y precios locales."""
    _CACHE_META_BRONCE.clear()
    _CACHE_PRECIOS_COLIMA.clear()


def obtener_metadatos_linaje_bronce(ruta_bronce: Path) -> dict[str, str]:
    """Lee y cachea en memoria la ficha .meta.json evitando lecturas redundantes."""
    clave = str(ruta_bronce.resolve())
    estat = ruta_bronce.stat()
    entrada_cache = _CACHE_META_BRONCE.get(clave)
    if entrada_cache and entrada_cache[:2] == (estat.st_mtime_ns, estat.st_size):
        return entrada_cache[2]

    ruta_meta = ruta_bronce.with_name(f"{ruta_bronce.name}.meta.json")
    hash_actual = ExtractorEtico.calcular_hash_sha256(ruta_bronce)
    if not ruta_meta.exists():
        ExtractorEtico.generar_ficha_meta(ruta_bronce)
    datos_meta = json.loads(ruta_meta.read_text(encoding="utf-8"))
    if datos_meta.get("hash_sha256") != hash_actual:
        ExtractorEtico.generar_ficha_meta(
            ruta_bronce, str(datos_meta.get("fuente_origen", "capa_bronce_agropulse"))
        )
        datos_meta = json.loads(ruta_meta.read_text(encoding="utf-8"))
    estat_fin = ruta_bronce.stat()
    _CACHE_META_BRONCE[clave] = (estat_fin.st_mtime_ns, estat_fin.st_size, datos_meta)
    return datos_meta


def adjuntar_columnas_linaje(
    df: pd.DataFrame, ruta_bronce: Path, prefijo_id: str
) -> pd.DataFrame:
    """Agrega las 5 columnas obligatorias de linaje rastreables hasta data/bronce/."""
    meta = obtener_metadatos_linaje_bronce(ruta_bronce)
    df_lin = df.copy()
    df_lin["linaje_id_registro"] = [
        f"{prefijo_id}-{idx:05d}" for idx in range(1, len(df_lin) + 1)
    ]
    df_lin["linaje_archivo_bronce"] = str(meta["archivo"])
    df_lin["linaje_sha256_bronce"] = str(meta["hash_sha256"])
    df_lin["linaje_fecha_ingesta_utc"] = str(meta["timestamp_captura"])
    df_lin["linaje_fuente"] = str(meta["fuente_origen"])
    return df_lin


def obtener_precios_reales_plaza_colima() -> dict[str, float]:
    """Obtiene y cachea por mtime la última cotización real vigente en Colima."""
    mt_m = ARCHIVO_PRECIOS_MENSUAL.stat().st_mtime_ns if ARCHIVO_PRECIOS_MENSUAL.exists() else 0
    mt_d = ARCHIVO_PRECIOS_DIARIO.stat().st_mtime_ns if ARCHIVO_PRECIOS_DIARIO.exists() else 0
    llave = (mt_m, mt_d)
    if llave in _CACHE_PRECIOS_COLIMA:
        return _CACHE_PRECIOS_COLIMA[llave]
    precios = dict(PRECIOS_RESPALDO_COLIMA)
    if mt_m:
        df_m = pd.read_csv(ARCHIVO_PRECIOS_MENSUAL)
        df_col_m = df_m[df_m["central_abasto"] == "Colima"]
        if not df_col_m.empty:
            ult_m = (
                df_col_m.sort_values("periodo_mensual")
                .groupby("cultivo")["precio_mayorista_mxn_kg"]
                .last()
                .to_dict()
            )
            precios.update({str(k): float(v) for k, v in ult_m.items()})
    if mt_d:
        df_d = pd.read_csv(ARCHIVO_PRECIOS_DIARIO)
        df_col_d = df_d[df_d["central_abasto"] == "Colima"]
        if not df_col_d.empty:
            ult_d = (
                df_col_d.sort_values("fecha")
                .groupby("cultivo")["precio_mayorista_mxn_kg"]
                .last()
                .to_dict()
            )
            precios.update({str(k): float(v) for k, v in ult_d.items()})
    _CACHE_PRECIOS_COLIMA[llave] = precios
    return precios


def consultar_distancias_carretera_osrm(
    prods: pd.DataFrame, comps: pd.DataFrame
) -> tuple[np.ndarray, np.ndarray] | None:
    """Consulta en una sola llamada HTTP la matriz carretera real en km y minutos."""
    coords_p = [f"{lon},{lat}" for lon, lat in zip(prods["longitud"], prods["latitud"], strict=False)]
    coords_c = [f"{lon},{lat}" for lon, lat in zip(comps["longitud"], comps["latitud"], strict=False)]
    cadena = ";".join(coords_p + coords_c)
    if cadena in _CACHE_MATRIZ_OSRM:
        return _CACHE_MATRIZ_OSRM[cadena]
    idx_src = ";".join(str(i) for i in range(len(coords_p)))
    idx_dst = ";".join(str(i + len(coords_p)) for i in range(len(coords_c)))
    url = f"{URL_TABLA_OSRM}/{cadena}?sources={idx_src}&destinations={idx_dst}&annotations=distance,duration"
    try:
        resp = requests.get(
            url, headers={"User-Agent": USER_AGENT_ACADEMICO}, timeout=TIMEOUT_HTTP_SEGUNDOS
        )
        resp.raise_for_status()
        datos = resp.json()
        dist_km = (np.asarray(datos["distances"], dtype=float) / 1000.0).flatten()
        dur_min = (np.asarray(datos["durations"], dtype=float) / 60.0).flatten()
        _CACHE_MATRIZ_OSRM[cadena] = (dist_km, dur_min)
        return dist_km, dur_min
    except (requests.RequestException, KeyError, ValueError, TypeError):
        return None


def reproyectar_nodos_utm(df_nodos: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convierte nodos a GeoDataFrame WGS84 de forma vectorizada y pasa a UTM 13N."""
    geometrias = gpd.points_from_xy(
        df_nodos["longitud"], df_nodos["latitud"], crs=EPSG_WGS84
    )
    gdf_wgs84 = gpd.GeoDataFrame(df_nodos.copy(), geometry=geometrias, crs=EPSG_WGS84)
    return gdf_wgs84.to_crs(EPSG_UTM_COLIMA)


def _extraer_tabla_coordenadas_utm(gdf_sub: gpd.GeoDataFrame) -> pd.DataFrame:
    """Extrae vectores X/Y en metros desde la geometría reproyectada en UTM 13N."""
    df_xy = pd.DataFrame(gdf_sub.drop(columns=["geometry"])).reset_index(drop=True)
    df_xy["utm_x"] = gdf_sub.geometry.x.to_numpy()
    df_xy["utm_y"] = gdf_sub.geometry.y.to_numpy()
    return df_xy


def construir_matriz_rutas_colima(gdf_utm: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Calcula las 60 rutas reales (10 municipios x 6 compradores) en Colima."""
    prods = _extraer_tabla_coordenadas_utm(
        gdf_utm[gdf_utm["tipo_nodo"] == "PRODUCTOR_ORIGEN"]
    )
    comps = _extraer_tabla_coordenadas_utm(
        gdf_utm[gdf_utm["tipo_nodo"] == "COMPRADOR_ANCLA"]
    )
    pares = pd.merge(prods, comps, how="cross", suffixes=("_prod", "_comp"))
    dist_utm_km = np.maximum(
        0.8,
        np.hypot(
            pares["utm_x_prod"].to_numpy() - pares["utm_x_comp"].to_numpy(),
            pares["utm_y_prod"].to_numpy() - pares["utm_y_comp"].to_numpy(),
        )
        / 1000.0,
    )
    res_osrm = consultar_distancias_carretera_osrm(prods, comps)
    if res_osrm is not None and len(res_osrm[0]) == len(pares):
        dist_vial = np.maximum(1.5, np.round(res_osrm[0], 2))
        tiempo_min = np.maximum(4.0, np.round(res_osrm[1], 1))
    else:
        dist_vial = np.maximum(1.5, np.round(dist_utm_km * FACTOR_SINUOSIDAD_VIAL, 2))
        tiempo_min = np.round((dist_vial / 52.0) * 60.0, 1)

    lote_ref = pares["capacidad_lote_kg_comp"].to_numpy(dtype=float)
    flete_lote = np.round(
        COSTO_MANIOBRA_LOTE_MXN + (dist_vial * COSTO_FLETE_MXN_POR_KM), 2
    )
    flete_kg = np.round(flete_lote / np.maximum(lote_ref, 400.0), 2)
    mapa_precios = obtener_precios_reales_plaza_colima()
    precios_base = (
        pares["cultivo_referencia_prod"].map(mapa_precios).fillna(22.0).to_numpy()
    )
    primas = pares["prima_comercial_pct_comp"].to_numpy(dtype=float) / 100.0
    p_venta = np.round(precios_base * (1.0 + primas), 2)
    p_compra = np.round(precios_base * 0.84, 2)
    spread_kg = np.round(p_venta - p_compra - flete_kg, 2)

    df_rutas = pd.DataFrame(
        {
            "id_ruta": pares["id_nodo_prod"] + "_" + pares["id_nodo_comp"],
            "nodo_productor": pares["nombre_nodo_prod"],
            "municipio_origen": pares["municipio_prod"],
            "cultivo_origen": pares["cultivo_referencia_prod"],
            "lat_productor": pares["latitud_prod"].astype(float),
            "lon_productor": pares["longitud_prod"].astype(float),
            "comprador_ancla": pares["nombre_nodo_comp"],
            "municipio_destino": pares["municipio_comp"],
            "lat_comprador": pares["latitud_comp"].astype(float),
            "lon_comprador": pares["longitud_comp"].astype(float),
            "lote_consolidado_kg": lote_ref,
            "distancia_lineal_km": np.round(dist_utm_km, 2),
            "distancia_vial_km": dist_vial,
            "tiempo_traslado_min": tiempo_min,
            "indice_sinuosidad_real": np.round(dist_vial / dist_utm_km, 2),
            "costo_flete_lote_400kg_mxn": np.round(
                COSTO_MANIOBRA_LOTE_MXN + dist_vial * COSTO_FLETE_MXN_POR_KM, 2
            ),
            "costo_flete_mxn_kg": flete_kg,
            "precio_compra_productor_mxn_kg": p_compra,
            "precio_venta_comprador_mxn_kg": p_venta,
            "spread_neto_mxn_kg": spread_kg,
            "margen_lote_400kg_mxn": np.round(spread_kg * PESO_LOTE_CONSOLIDADO_KG, 2),
        }
    )
    idx_opt = df_rutas.groupby("nodo_productor")["spread_neto_mxn_kg"].idxmax()
    df_rutas["es_ruta_optima"] = df_rutas.index.isin(idx_opt)
    df_rutas = adjuntar_columnas_linaje(df_rutas, ARCHIVO_GEOESPACIAL_NODOS, "GEO-E2")
    coords_lineas = np.stack(
        [
            np.column_stack([df_rutas["lon_productor"], df_rutas["lat_productor"]]),
            np.column_stack([df_rutas["lon_comprador"], df_rutas["lat_comprador"]]),
        ],
        axis=1,
    )
    return gpd.GeoDataFrame(
        df_rutas, geometry=shapely.linestrings(coords_lineas), crs=EPSG_WGS84
    )


def procesar_geoespacial_en_memoria(
    df_plata_geo: pd.DataFrame | None = None,
) -> tuple[dict[str, int | float], pd.DataFrame]:
    """Ejecuta el cálculo geoespacial estatal de 60 rutas y devuelve resumen."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    df_nodos = (
        df_plata_geo
        if df_plata_geo is not None
        else pd.read_csv(ARCHIVO_PLATA_GEOESPACIAL)
    )
    gdf_utm = reproyectar_nodos_utm(df_nodos)
    gdf_rutas = construir_matriz_rutas_colima(gdf_utm)

    df_csv = pd.DataFrame(gdf_rutas.drop(columns=["geometry"]))
    df_csv.to_csv(
        ARCHIVO_ORO_RUTAS_FLETE, index=False, encoding="utf-8", lineterminator="\n"
    )
    gdf_rutas.to_file(ARCHIVO_ORO_GEOJSON_RUTAS, driver="GeoJSON")
    resumen = {
        "rutas_calculadas": len(df_csv),
        "distancia_media_km": round(float(df_csv["distancia_vial_km"].mean()), 2),
        "flete_medio_mxn_kg": round(float(df_csv["costo_flete_mxn_kg"].mean()), 2),
        "spread_optimo_medio_mxn_kg": round(
            float(df_csv[df_csv["es_ruta_optima"]]["spread_neto_mxn_kg"].mean()), 2
        ),
    }
    return resumen, df_csv


def ejecutar_procesamiento_geoespacial() -> dict[str, int | float]:
    """Punto de entrada estándar para generar rutas_flete_colima.csv y .geojson."""
    resumen, _ = procesar_geoespacial_en_memoria()
    return resumen


if __name__ == "__main__":
    resumen = ejecutar_procesamiento_geoespacial()
    print(f"Procesamiento geoespacial estatal en Colima completado: {resumen}")
