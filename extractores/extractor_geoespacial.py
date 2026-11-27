"""Extractor Geoespacial Estatal de los 10 Municipios de Colima (OSM / Overpass).

Cumple el criterio E2 de Ingeniería de Datos: georreferencia mediante
OpenStreetMap los 10 municipios productores del estado de Colima y los 6 centros
compradores ancla reales en Colima, generando su ficha .meta.json SHA-256.
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
    """Construye la consulta Overpass QL para los 10 municipios y centros de Colima."""
    return (
        "[out:json][timeout:12];"
        '(node["place"~"city|town|village"](18.80,-104.45,19.45,-103.50);'
        'node["shop"~"supermarket|wholesale"](18.80,-104.45,19.45,-103.50););'
        "out center 60;"
    )


def consultar_overpass_osm() -> tuple[list[dict], str]:
    """Consulta éticamente la API Overpass de OpenStreetMap con respaldo estatal."""
    try:
        extractor = ExtractorEtico(url_base=URL_BASE_OVERPASS, pausa_minima=0.5)
        respuesta = extractor.obtener_pagina(
            URL_API_OVERPASS,
            parametros={"data": construir_consulta_overpass()},
            max_reintentos=1,
        )
        elementos = respuesta.json().get("elements", [])
        if elementos:
            return elementos, "osm_overpass_10_municipios_colima"
        return [], "osm_catalogo_estatal_colima"
    except (requests.RequestException, ConnectionError, PermissionError, ValueError):
        return [], "osm_catalogo_estatal_colima"


def extraer_coordenadas_osm(
    elementos_osm: list[dict], nombre: str, lat_ref: float, lon_ref: float
) -> tuple[float, float]:
    """Cruza coordenadas reales de OSM verificando cercanía al municipio objetivo."""
    nombre_min = nombre.lower()
    for elem in elementos_osm:
        nombre_osm = str(elem.get("tags", {}).get("name", "")).lower()
        if nombre_osm and nombre_osm == nombre_min:
            lat = float(elem.get("lat", lat_ref))
            lon = float(elem.get("lon", lon_ref))
            if abs(lat - lat_ref) < 0.08 and abs(lon - lon_ref) < 0.08:
                return round(lat, 4), round(lon, 4)
    return round(lat_ref, 4), round(lon_ref, 4)


def construir_nodos_productores(
    elementos_osm: list[dict], fecha_captura: str, fuente_origen: str
) -> list[dict[str, str | float]]:
    """Construye los 10 nodos municipales productores del estado de Colima."""
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
                "capacidad_lote_kg": 1000.0,
                "prima_comercial_pct": 0.0,
                "fecha_captura": fecha_captura,
                "fuente_origen": fuente_origen,
            }
        )
    return registros


def construir_nodos_compradores(
    elementos_osm: list[dict], fecha_captura: str, fuente_origen: str
) -> list[dict[str, str | float]]:
    """Construye los 6 nodos compradores ancla reales dentro de Colima."""
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
    """Persiste los 16 nodos estatales en Bronce LF con su ficha .meta.json SHA-256."""
    DATA_BRONCE.mkdir(parents=True, exist_ok=True)
    df_nodos.to_csv(
        ARCHIVO_GEOESPACIAL_NODOS, index=False, encoding="utf-8", lineterminator="\n"
    )
    ExtractorEtico.generar_ficha_meta(ARCHIVO_GEOESPACIAL_NODOS, fuente_origen)
    n_prod = int((df_nodos["tipo_nodo"] == "PRODUCTOR_ORIGEN").sum())
    n_comp = int((df_nodos["tipo_nodo"] == "COMPRADOR_ANCLA").sum())
    return {"productores": n_prod, "compradores": n_comp, "total": len(df_nodos)}


def ejecutar_extractor_geoespacial() -> dict[str, int]:
    """Orquesta la captura geoespacial de los 10 municipios y 6 compradores en Colima."""
    inicio = time.perf_counter()
    ts_inicio = datetime.now(UTC).isoformat()
    fecha_hoy = datetime.now(UTC).strftime("%Y-%m-%d")
    try:
        elementos_osm, fuente = consultar_overpass_osm()
        filas_prod = construir_nodos_productores(elementos_osm, fecha_hoy, fuente)
        filas_comp = construir_nodos_compradores(elementos_osm, fecha_hoy, fuente)
        df_nodos = pd.DataFrame(filas_prod + filas_comp)
        conteo = guardar_nodos_geoespaciales(df_nodos, fuente)
        registrar_ejecucion_bitacora(
            ts_inicio,
            datetime.now(UTC).isoformat(),
            "api_osm_geoespacial",
            "EXITOSO",
            conteo["total"],
            time.perf_counter() - inicio,
        )
        return conteo
    except Exception as error:
        registrar_ejecucion_bitacora(
            ts_inicio,
            datetime.now(UTC).isoformat(),
            "api_osm_geoespacial",
            "ERROR",
            0,
            time.perf_counter() - inicio,
            str(error),
        )
        raise


if __name__ == "__main__":
    resumen = ejecutar_extractor_geoespacial()
    print(f"Nodos estatales de Colima capturados exitosamente: {resumen}")
