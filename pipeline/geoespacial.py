"""Módulo de Procesamiento Geoespacial y Costos Logísticos con GeoPandas (E2).

Cumple el criterio E2 de Ingeniería de Datos: reproyecta coordenadas de EPSG:4326
a EPSG:32613 (UTM Zona 13N para Colima), calcula distancias reales en kilómetros
entre productores y compradores ancla, optimiza el margen de intermediación por
lote de 400 kg e inyecta trazabilidad completa de linaje (Bronce -> Plata -> Oro).
"""

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

from config import (
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_ORO_GEOJSON_RUTAS,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PLATA_GEOESPACIAL,
    COSTO_FLETE_MXN_POR_KM,
    COSTO_MANIOBRA_LOTE_MXN,
    DATA_ORO,
    EPSG_UTM_COLIMA,
    EPSG_WGS84,
    FACTOR_SINUOSIDAD_VIAL,
    PESO_LOTE_CONSOLIDADO_KG,
)
from extractores.base import ExtractorEtico

PRECIOS_BASE_CULTIVO_COLIMA: dict[str, float] = {
    "Limón Mexicano": 24.50,
    "Papaya Maradol": 18.80,
    "Plátano Chiapas": 15.40,
    "Aguacate Hass": 58.00,
}


def obtener_metadatos_linaje_bronce(ruta_bronce: Path) -> dict[str, str]:
    """Lee y sincroniza la ficha .meta.json de un archivo crudo en Capa Bronce."""
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


def reproyectar_nodos_utm(df_nodos: pd.DataFrame) -> gpd.GeoDataFrame:
    """Convierte la tabla de nodos a GeoDataFrame WGS84 y reproyecta a UTM 13N."""
    geometrias = [
        Point(float(lon), float(lat))
        for lon, lat in zip(df_nodos["longitud"], df_nodos["latitud"], strict=False)
    ]
    gdf_wgs84 = gpd.GeoDataFrame(df_nodos.copy(), geometry=geometrias, crs=EPSG_WGS84)
    return gdf_wgs84.to_crs(EPSG_UTM_COLIMA)


def calcular_economia_ruta(
    fila_prod: pd.Series, fila_comp: pd.Series, dist_lineal_km: float
) -> dict[str, str | float | bool]:
    """Calcula distancia vial, costo de flete y spread B2B para un lote de 400 kg."""
    dist_vial_km = max(1.2, round(dist_lineal_km * FACTOR_SINUOSIDAD_VIAL, 2))
    flete_lote = round(
        COSTO_MANIOBRA_LOTE_MXN + (dist_vial_km * COSTO_FLETE_MXN_POR_KM), 2
    )
    flete_kg = round(flete_lote / PESO_LOTE_CONSOLIDADO_KG, 2)
    cultivo = str(fila_prod["cultivo_referencia"])
    precio_base = PRECIOS_BASE_CULTIVO_COLIMA.get(cultivo, 22.0)
    prima = float(fila_comp["prima_comercial_pct"]) / 100.0
    precio_venta = round(precio_base * (1.0 + prima), 2)
    precio_compra = round(precio_base * 0.84, 2)
    spread_kg = round(precio_venta - precio_compra - flete_kg, 2)
    return {
        "id_ruta": f"{fila_prod['id_nodo']}_{fila_comp['id_nodo']}",
        "nodo_productor": str(fila_prod["nombre_nodo"]),
        "municipio_origen": str(fila_prod["municipio"]),
        "cultivo_origen": cultivo,
        "lat_productor": float(fila_prod["latitud"]),
        "lon_productor": float(fila_prod["longitud"]),
        "comprador_ancla": str(fila_comp["nombre_nodo"]),
        "municipio_destino": str(fila_comp["municipio"]),
        "lat_comprador": float(fila_comp["latitud"]),
        "lon_comprador": float(fila_comp["longitud"]),
        "lote_consolidado_kg": PESO_LOTE_CONSOLIDADO_KG,
        "distancia_lineal_km": round(max(0.8, dist_lineal_km), 2),
        "distancia_vial_km": dist_vial_km,
        "costo_flete_lote_400kg_mxn": flete_lote,
        "costo_flete_mxn_kg": flete_kg,
        "precio_compra_productor_mxn_kg": precio_compra,
        "precio_venta_comprador_mxn_kg": precio_venta,
        "spread_neto_mxn_kg": spread_kg,
        "margen_lote_400kg_mxn": round(spread_kg * PESO_LOTE_CONSOLIDADO_KG, 2),
    }


def construir_matriz_rutas_colima(gdf_utm: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Calcula las 16 rutas productor-comprador en UTM 13N y etiqueta la óptima."""
    prods = gdf_utm[gdf_utm["tipo_nodo"] == "PRODUCTOR_ORIGEN"].reset_index(drop=True)
    comps = gdf_utm[gdf_utm["tipo_nodo"] == "COMPRADOR_ANCLA"].reset_index(drop=True)
    registros: list[dict[str, str | float | bool]] = []
    lineas_wgs84: list[LineString] = []
    for _, prod in prods.iterrows():
        for _, comp in comps.iterrows():
            dist_km = float(prod.geometry.distance(comp.geometry)) / 1000.0
            info_ruta = calcular_economia_ruta(prod, comp, dist_km)
            registros.append(info_ruta)
            lineas_wgs84.append(
                LineString(
                    [
                        (float(prod["longitud"]), float(prod["latitud"])),
                        (float(comp["longitud"]), float(comp["latitud"])),
                    ]
                )
            )
    df_rutas = pd.DataFrame(registros)
    idx_opt = df_rutas.groupby("nodo_productor")["spread_neto_mxn_kg"].idxmax()
    df_rutas["es_ruta_optima"] = df_rutas.index.isin(idx_opt)
    df_rutas = adjuntar_columnas_linaje(df_rutas, ARCHIVO_GEOESPACIAL_NODOS, "GEO-E2")
    return gpd.GeoDataFrame(df_rutas, geometry=lineas_wgs84, crs=EPSG_WGS84)


def ejecutar_procesamiento_geoespacial() -> dict[str, int | float]:
    """Ejecuta el cálculo geoespacial completo y persiste CSV y GeoJSON en Capa Oro."""
    DATA_ORO.mkdir(parents=True, exist_ok=True)
    df_plata_geo = pd.read_csv(ARCHIVO_PLATA_GEOESPACIAL)
    gdf_utm = reproyectar_nodos_utm(df_plata_geo)
    gdf_rutas = construir_matriz_rutas_colima(gdf_utm)

    df_csv = pd.DataFrame(gdf_rutas.drop(columns=["geometry"]))
    df_csv.to_csv(ARCHIVO_ORO_RUTAS_FLETE, index=False, encoding="utf-8")
    gdf_rutas.to_file(ARCHIVO_ORO_GEOJSON_RUTAS, driver="GeoJSON")

    return {
        "rutas_calculadas": len(df_csv),
        "distancia_media_km": round(float(df_csv["distancia_vial_km"].mean()), 2),
        "flete_medio_mxn_kg": round(float(df_csv["costo_flete_mxn_kg"].mean()), 2),
        "spread_optimo_medio_mxn_kg": round(
            float(df_csv[df_csv["es_ruta_optima"]]["spread_neto_mxn_kg"].mean()), 2
        ),
    }


if __name__ == "__main__":
    resumen = ejecutar_procesamiento_geoespacial()
    print(f"Procesamiento geoespacial en Capa Oro completado: {resumen}")

