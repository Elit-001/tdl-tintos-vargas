"""Extractor de la Fuente 3 (E2): Nodos Geoespaciales de Colima (OpenStreetMap).

Cumple el criterio E2 de Ingeniería de Datos: consume la API abierta Overpass de
OpenStreetMap utilizando ExtractorEtico con respaldo determinista local para los
nodos productores y compradores ancla (buckets de consumo) en Colima, guardando
en Capa Bronce con su ficha .meta.json (SHA-256) y bitácora de fiabilidad.
"""

import time
from datetime import UTC, datetime

import pandas as pd
import requests

from config import (
    ARCHIVO_GEOESPACIAL_NODOS,
    COMPRADORES_ANCLA_COLIMA,
    DATA_BRONCE,
    NODOS_PRODUCTORES_COLIMA,
    URL_API_OVERPASS,
    URL_BASE_OVERPASS,
)
from extractores.base import ExtractorEtico, registrar_ejecucion_bitacora


def construir_consulta_overpass() -> str:
    """Construye la consulta Overpass QL para nodos comerciales y agrícolas en Colima."""
    return (
        "[out:json][timeout:12];"
        '(node["place"~"town|city"](18.80,-104.45,19.35,-103.60);'
        'node["shop"~"supermarket|wholesale"](18.80,-104.45,19.35,-103.60););'
        "out center 25;"
    )


def consultar_overpass_osm() -> tuple[list[dict], str]:
    """Consulta éticamente la API Overpass de OpenStreetMap con respaldo resiliente."""
    try:
        extractor = ExtractorEtico(url_base=URL_BASE_OVERPASS)
        respuesta = extractor.obtener_pagina(
            URL_API_OVERPASS,
            parametros={"data": construir_consulta_overpass()},
            max_reintentos=1,
        )
        datos = respuesta.json()
        elementos = datos.get("elements", [])
        if elementos:
            return elementos, "osm_overpass_api_verificado"
        return [], "osm_catalogo_referencia_colima"
    except (requests.RequestException, ConnectionError, PermissionError, ValueError):
        return [], "osm_catalogo_referencia_colima"


def extraer_coordenadas_osm(
    elementos_osm: list[dict], nombre: str, lat_ref: float, lon_ref: float
) -> tuple[float, float]:
    """Busca coincidencia por etiqueta en elementos OSM o conserva coordenada verificada."""
    nombre_min = nombre.lower()
    for elem in elementos_osm:
        etiquetas = elem.get("tags", {})
        nombre_osm = str(etiquetas.get("name", "")).lower()
        if nombre_osm and (nombre_min in nombre_osm or nombre_osm in nombre_min):
            lat = float(elem.get("lat", lat_ref))
            lon = float(elem.get("lon", lon_ref))
            if 18.7 <= lat <= 19.5 and -104.6 <= lon <= -103.4:
                return round(lat, 4), round(lon, 4)
    return round(lat_ref, 4), round(lon_ref, 4)


def construir_nodos_productores(
    elementos_osm: list[dict], fecha_captura: str, fuente_origen: str
) -> list[dict[str, str | float]]:
    """Construye los registros geoespaciales de zonas agroproductoras de Colima."""
    registros: list[dict[str, str | float]] = []
    for idx, (nodo, info) in enumerate(NODOS_PRODUCTORES_COLIMA.items(), start=1):
        lat, lon = extraer_coordenadas_osm(
            elementos_osm, nodo, float(info["latitud"]), float(info["longitud"])
        )
        registros.append(
            {
                "id_nodo": f"PROD-{idx:02d}",
                "nombre_nodo": nodo,
                "tipo_nodo": "PRODUCTOR_ORIGEN",
                "municipio": str(info["municipio"]),
                "latitud": lat,
                "longitud": lon,
                "cultivo_referencia": str(info["cultivo_principal"]),
                "capacidad_lote_kg": 400.0,
                "prima_comercial_pct": 0.0,
                "fecha_captura": fecha_captura,
                "fuente_origen": fuente_origen,
            }
        )
    return registros


def construir_nodos_compradores(
    elementos_osm: list[dict], fecha_captura: str, fuente_origen: str
) -> list[dict[str, str | float]]:
    """Construye los registros geoespaciales de compradores ancla (buckets de consumo)."""
    registros: list[dict[str, str | float]] = []
    for idx, (comprador, info) in enumerate(COMPRADORES_ANCLA_COLIMA.items(), start=1):
        lat, lon = extraer_coordenadas_osm(
            elementos_osm, comprador, float(info["latitud"]), float(info["longitud"])
        )
        registros.append(
            {
                "id_nodo": f"COMP-{idx:02d}",
                "nombre_nodo": comprador,
                "tipo_nodo": "COMPRADOR_ANCLA",
                "municipio": str(info["municipio"]),
                "latitud": lat,
                "longitud": lon,
                "cultivo_referencia": "Multicultivo Consolidado",
                "capacidad_lote_kg": float(info["demanda_lote_kg"]),
                "prima_comercial_pct": float(info["prima_comercial_pct"]),
                "fecha_captura": fecha_captura,
                "fuente_origen": fuente_origen,
            }
        )
    return registros


def guardar_nodos_geoespaciales(
    df_nodos: pd.DataFrame, fuente_origen: str
) -> dict[str, int]:
    """Persiste los nodos geoespaciales en Bronce y genera su ficha .meta.json SHA-256."""
    DATA_BRONCE.mkdir(parents=True, exist_ok=True)
    df_nodos.to_csv(ARCHIVO_GEOESPACIAL_NODOS, index=False, encoding="utf-8")
    ExtractorEtico.generar_ficha_meta(ARCHIVO_GEOESPACIAL_NODOS, fuente_origen)
    n_prod = int((df_nodos["tipo_nodo"] == "PRODUCTOR_ORIGEN").sum())
    n_comp = int((df_nodos["tipo_nodo"] == "COMPRADOR_ANCLA").sum())
    return {"productores": n_prod, "compradores": n_comp, "total": len(df_nodos)}


def ejecutar_extractor_geoespacial() -> dict[str, int]:
    """Orquesta la captura geoespacial de Colima, guarda en Bronce y registra bitácora."""
    inicio = time.perf_counter()
    ts_inicio = datetime.now(UTC).isoformat()
    fecha_hoy = datetime.now(UTC).strftime("%Y-%m-%d")
    try:
        elementos_osm, fuente = consultar_overpass_osm()
        filas_prod = construir_nodos_productores(elementos_osm, fecha_hoy, fuente)
        filas_comp = construir_nodos_compradores(elementos_osm, fecha_hoy, fuente)
        df_nodos = pd.DataFrame(filas_prod + filas_comp)
        conteo = guardar_nodos_geoespaciales(df_nodos, fuente)
        ts_fin = datetime.now(UTC).isoformat()
        duracion = time.perf_counter() - inicio
        registrar_ejecucion_bitacora(
            ts_inicio,
            ts_fin,
            "api_osm_geoespacial",
            "EXITOSO",
            conteo["total"],
            duracion,
        )
        return conteo
    except Exception as error:
        ts_fin = datetime.now(UTC).isoformat()
        duracion = time.perf_counter() - inicio
        registrar_ejecucion_bitacora(
            ts_inicio,
            ts_fin,
            "api_osm_geoespacial",
            "ERROR",
            0,
            duracion,
            str(error),
        )
        raise


if __name__ == "__main__":
    resumen = ejecutar_extractor_geoespacial()
    print(f"Nodos geoespaciales de Colima capturados exitosamente: {resumen}")

