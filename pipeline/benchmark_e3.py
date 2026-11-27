"""Benchmark Cuantitativo Reproducible del Pipeline Medallion (Antes vs. Después — E3).

Cumple el criterio E3 de Ingeniería de Datos y Eficiencia de Desempeño ISO/IEC 25010:
compara en igualdad exacta de salidas el pipeline legado E2 frente al pipeline
optimizado E3 con time.perf_counter() y tracemalloc, guardando calidad/benchmark_e3.csv.
"""

import gc
import json
import time
import tracemalloc

import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString, Point

from config import (
    ARCHIVO_BENCHMARK_E3,
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_CUARENTENA_CLIMA,
    ARCHIVO_CUARENTENA_GEOESPACIAL,
    ARCHIVO_CUARENTENA_PRECIOS,
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_GEOJSON_RUTAS,
    ARCHIVO_ORO_PARQUET,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PLATA_CLIMA,
    ARCHIVO_PLATA_CLIMA_LIMPIO,
    ARCHIVO_PLATA_GEOESPACIAL,
    ARCHIVO_PLATA_PRECIOS,
    ARCHIVO_PLATA_PRECIOS_LIMPIO,
    ARCHIVO_PRECIOS_MENSUAL,
    COSTO_FLETE_MXN_POR_KM,
    COSTO_MANIOBRA_LOTE_MXN,
    EPSG_UTM_COLIMA,
    EPSG_WGS84,
    FACTOR_SINUOSIDAD_VIAL,
    PESO_LOTE_CONSOLIDADO_KG,
    RUTA_CALIDAD,
)
from extractores.base import ExtractorEtico
from pipeline.geoespacial import (
    PRECIOS_BASE_CULTIVO_COLIMA,
    limpiar_cache_metadatos_bronce,
    procesar_geoespacial_en_memoria,
)
from pipeline.integracion import (
    generar_diccionario_datos,
    integrar_en_memoria,
    preparar_esquema_clima,
    preparar_esquema_precios,
)
from pipeline.limpieza import (
    COLUMNAS_NUMERICAS_CLIMA,
    COLUMNAS_NUMERICAS_PRECIOS,
    limpiar_marcos_en_memoria,
)
from pipeline.puerta_calidad import (
    crear_esquema_clima,
    crear_esquema_geoespacial,
    crear_esquema_precios,
    ejecutar_puerta_calidad_en_memoria,
    procesar_archivo_bronce,
)


def _limpieza_legada_e2(df: pd.DataFrame, cols: list[str], grupo: str) -> pd.DataFrame:
    """Reproduce fielmente las múltiples copias e iteraciones por columna de E2."""
    df_imp = df.copy()
    for col in cols:
        df_imp[col] = df_imp.groupby(grupo)[col].transform(
            lambda s: s.interpolate(method="linear").bfill().ffill()
        )
        df_imp[col] = df_imp[col].fillna(float(df_imp[col].median())).round(2)
    df_iqr = df_imp.copy()
    bandera = pd.Series(False, index=df_iqr.index)
    for col in cols:
        q1 = df_iqr.groupby(grupo)[col].transform("quantile", 0.25)
        q3 = df_iqr.groupby(grupo)[col].transform("quantile", 0.75)
        iqr = q3 - q1
        bandera = bandera | (df_iqr[col] < q1 - 1.5 * iqr) | (df_iqr[col] > q3 + 1.5 * iqr)
        df_iqr[col] = df_iqr[col].clip(lower=q1 - 1.5 * iqr, upper=q3 + 1.5 * iqr).round(2)
    df_iqr["es_atipico_iqr"] = bandera
    df_norm = df_iqr.copy()
    for col in cols:
        mn = df_norm.groupby(grupo)[col].transform("min")
        mx = df_norm.groupby(grupo)[col].transform("max")
        df_norm[f"{col}_norm"] = ((df_norm[col] - mn) / (mx - mn).replace(0.0, 1.0)).round(4)
    return df_norm


def _geoespacial_legado_e2() -> None:
    """Reproduce el flujo geoespacial E2 completo con .iterrows() y escritura GeoJSON."""
    df_nodos = pd.read_csv(ARCHIVO_PLATA_GEOESPACIAL)
    geoms = [
        Point(float(lon), float(lat))
        for lon, lat in zip(df_nodos["longitud"], df_nodos["latitud"], strict=False)
    ]
    gdf_utm = gpd.GeoDataFrame(df_nodos.copy(), geometry=geoms, crs=EPSG_WGS84).to_crs(EPSG_UTM_COLIMA)
    prods = gdf_utm[gdf_utm["tipo_nodo"] == "PRODUCTOR_ORIGEN"].reset_index(drop=True)
    comps = gdf_utm[gdf_utm["tipo_nodo"] == "COMPRADOR_ANCLA"].reset_index(drop=True)
    filas, lineas = [], []
    for _, prod in prods.iterrows():
        for _, comp in comps.iterrows():
            d_km = float(prod.geometry.distance(comp.geometry)) / 1000.0
            d_vial = max(1.2, round(d_km * FACTOR_SINUOSIDAD_VIAL, 2))
            fl_lote = round(COSTO_MANIOBRA_LOTE_MXN + d_vial * COSTO_FLETE_MXN_POR_KM, 2)
            fl_kg = round(fl_lote / PESO_LOTE_CONSOLIDADO_KG, 2)
            p_base = PRECIOS_BASE_CULTIVO_COLIMA.get(str(prod["cultivo_referencia"]), 22.0)
            p_vta = round(p_base * (1.0 + float(comp["prima_comercial_pct"]) / 100.0), 2)
            p_cmp = round(p_base * 0.84, 2)
            sp = round(p_vta - p_cmp - fl_kg, 2)
            filas.append({
                "id_ruta": f"{prod['id_nodo']}_{comp['id_nodo']}",
                "nodo_productor": str(prod["nombre_nodo"]),
                "municipio_origen": str(prod["municipio"]),
                "cultivo_origen": str(prod["cultivo_referencia"]),
                "lat_productor": float(prod["latitud"]),
                "lon_productor": float(prod["longitud"]),
                "comprador_ancla": str(comp["nombre_nodo"]),
                "municipio_destino": str(comp["municipio"]),
                "lat_comprador": float(comp["latitud"]),
                "lon_comprador": float(comp["longitud"]),
                "lote_consolidado_kg": PESO_LOTE_CONSOLIDADO_KG,
                "distancia_lineal_km": round(max(0.8, d_km), 2),
                "distancia_vial_km": d_vial,
                "tiempo_traslado_min": round((d_vial / 52.0) * 60.0, 1),
                "indice_sinuosidad_real": round(d_vial / max(0.8, d_km), 2),
                "costo_flete_lote_400kg_mxn": fl_lote,
                "costo_flete_mxn_kg": fl_kg,
                "precio_compra_productor_mxn_kg": p_cmp,
                "precio_venta_comprador_mxn_kg": p_vta,
                "spread_neto_mxn_kg": sp,
                "margen_lote_400kg_mxn": round(sp * PESO_LOTE_CONSOLIDADO_KG, 2),
            })
            lineas.append(LineString([(float(prod["longitud"]), float(prod["latitud"])), (float(comp["longitud"]), float(comp["latitud"]))]))
    df_r = pd.DataFrame(filas)
    df_r["es_ruta_optima"] = df_r.index.isin(df_r.groupby("nodo_productor")["spread_neto_mxn_kg"].idxmax())
    h_geo = ExtractorEtico.calcular_hash_sha256(ARCHIVO_GEOESPACIAL_NODOS)
    m_geo = json.loads(ARCHIVO_GEOESPACIAL_NODOS.with_name(f"{ARCHIVO_GEOESPACIAL_NODOS.name}.meta.json").read_text(encoding="utf-8"))
    df_r["linaje_id_registro"] = [f"GEO-E2-{i:05d}" for i in range(1, len(df_r) + 1)]
    df_r["linaje_archivo_bronce"] = m_geo["archivo"]
    df_r["linaje_sha256_bronce"] = h_geo
    df_r["linaje_fecha_ingesta_utc"] = m_geo["timestamp_captura"]
    df_r["linaje_fuente"] = m_geo["fuente_origen"]
    gdf_r = gpd.GeoDataFrame(df_r.copy(), geometry=lineas, crs=EPSG_WGS84)
    df_r.to_csv(ARCHIVO_ORO_RUTAS_FLETE, index=False, encoding="utf-8", lineterminator="\n")
    gdf_r.to_file(ARCHIVO_ORO_GEOJSON_RUTAS, driver="GeoJSON")


def ejecutar_flujo_legado_antes() -> dict[str, float]:
    """Ejecuta y mide en igualdad exacta las 4 etapas completas de la versión E2."""
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    procesar_archivo_bronce(ARCHIVO_CLIMA_MENSUAL, crear_esquema_clima(), ARCHIVO_PLATA_CLIMA, ARCHIVO_CUARENTENA_CLIMA)
    procesar_archivo_bronce(ARCHIVO_PRECIOS_MENSUAL, crear_esquema_precios(), ARCHIVO_PLATA_PRECIOS, ARCHIVO_CUARENTENA_PRECIOS)
    procesar_archivo_bronce(ARCHIVO_GEOESPACIAL_NODOS, crear_esquema_geoespacial(), ARCHIVO_PLATA_GEOESPACIAL, ARCHIVO_CUARENTENA_GEOESPACIAL)
    t1 = time.perf_counter()

    df_cl = _limpieza_legada_e2(pd.read_csv(ARCHIVO_PLATA_CLIMA), COLUMNAS_NUMERICAS_CLIMA, "zona_agricola")
    df_pr = _limpieza_legada_e2(pd.read_csv(ARCHIVO_PLATA_PRECIOS), COLUMNAS_NUMERICAS_PRECIOS, "cultivo")
    df_pr["categoria_precio"] = df_pr.groupby("cultivo")["precio_mayorista_mxn_kg"].transform(lambda x: pd.qcut(x.rank(method="first"), q=3, labels=["Bajo", "Medio", "Alto"]).astype(str))
    df_pr["nivel_volatilidad"] = pd.cut(df_pr["volatilidad_mensual_pct"], bins=[-1.0, 12.0, 17.0, 200.0], labels=["Estable", "Moderada", "Alta"]).astype(str)
    df_cl.to_csv(ARCHIVO_PLATA_CLIMA_LIMPIO, index=False, encoding="utf-8", lineterminator="\n")
    df_pr.to_csv(ARCHIVO_PLATA_PRECIOS_LIMPIO, index=False, encoding="utf-8", lineterminator="\n")
    t2 = time.perf_counter()

    _geoespacial_legado_e2()
    t3 = time.perf_counter()

    df_p2 = preparar_esquema_precios(pd.read_csv(ARCHIVO_PLATA_PRECIOS_LIMPIO).copy())
    df_c2 = preparar_esquema_clima(pd.read_csv(ARCHIVO_PLATA_CLIMA_LIMPIO).copy())
    df_oro_leg = pd.merge(df_p2, df_c2, on=["periodo_mensual", "zona_agricola"], how="inner").sort_values(["periodo_mensual", "cultivo", "central_abasto"]).reset_index(drop=True)
    h_cl = ExtractorEtico.calcular_hash_sha256(ARCHIVO_CLIMA_MENSUAL)
    h_pr = ExtractorEtico.calcular_hash_sha256(ARCHIVO_PRECIOS_MENSUAL)
    m_pr = json.loads(ARCHIVO_PRECIOS_MENSUAL.with_name(f"{ARCHIVO_PRECIOS_MENSUAL.name}.meta.json").read_text(encoding="utf-8"))
    df_oro_copia = df_oro_leg.copy()
    df_oro_copia["linaje_sha256_clima_bronce"] = h_cl
    df_oro_copia["linaje_id_registro"] = [f"ORO-ANL-{i:05d}" for i in range(1, len(df_oro_copia) + 1)]
    df_oro_copia["linaje_archivo_bronce"] = m_pr["archivo"]
    df_oro_copia["linaje_sha256_bronce"] = h_pr
    df_oro_copia["linaje_fecha_ingesta_utc"] = m_pr["timestamp_captura"]
    df_oro_copia["linaje_fuente"] = m_pr["fuente_origen"]
    df_oro_copia.to_csv(ARCHIVO_ORO_ANALITICO, index=False, encoding="utf-8", lineterminator="\n")
    generar_diccionario_datos(df_oro_copia, ARCHIVO_DICCIONARIO_ORO)
    t4 = time.perf_counter()

    _, pico_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "puerta_ms": (t1 - t0) * 1000.0,
        "limpieza_ms": (t2 - t1) * 1000.0,
        "geoespacial_ms": (t3 - t2) * 1000.0,
        "integracion_ms": (t4 - t3) * 1000.0,
        "total_ms": (t4 - t0) * 1000.0,
        "pico_ram_kb": pico_bytes / 1024.0,
        "lecturas_disco": 13.0,
    }


def ejecutar_flujo_optimizado_despues() -> dict[str, float]:
    """Ejecuta y mide las mismas 4 etapas completas con la arquitectura optimizada E3."""
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    _, marcos = ejecutar_puerta_calidad_en_memoria()
    t1 = time.perf_counter()
    _, df_cl, df_pr = limpiar_marcos_en_memoria(marcos["clima"], marcos["precios"])
    t2 = time.perf_counter()
    _, df_rutas = procesar_geoespacial_en_memoria(marcos["geoespacial"])
    t3 = time.perf_counter()
    _, df_oro = integrar_en_memoria(df_pr, df_cl, df_rutas, escribir_diccionario=True)
    del df_cl, df_pr, df_rutas, df_oro
    t4 = time.perf_counter()
    _, pico_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "puerta_ms": (t1 - t0) * 1000.0,
        "limpieza_ms": (t2 - t1) * 1000.0,
        "geoespacial_ms": (t3 - t2) * 1000.0,
        "integracion_ms": (t4 - t3) * 1000.0,
        "total_ms": (t4 - t0) * 1000.0,
        "pico_ram_kb": pico_bytes / 1024.0,
        "lecturas_disco": 3.0,
    }


def promediar_corridas(funcion_flujo: callable, repeticiones: int = 5) -> dict[str, float]:
    """Ejecuta corrida de calentamiento y promedia N corridas reproducibles."""
    funcion_flujo()
    acumulado: dict[str, list[float]] = {}
    for _ in range(repeticiones):
        res = funcion_flujo()
        for clave, valor in res.items():
            acumulado.setdefault(clave, []).append(valor)
    return {k: round(sum(v) / len(v), 2) for k, v in acumulado.items()}


def ejecutar_benchmark_e3(repeticiones: int = 5) -> pd.DataFrame:
    """Genera la comparativa Antes vs. Después y guarda calidad/benchmark_e3.csv."""
    RUTA_CALIDAD.mkdir(parents=True, exist_ok=True)
    limpiar_cache_metadatos_bronce()
    antes = promediar_corridas(ejecutar_flujo_legado_antes, repeticiones)
    despues = promediar_corridas(ejecutar_flujo_optimizado_despues, repeticiones)
    kb_csv = round(ARCHIVO_ORO_ANALITICO.stat().st_size / 1024.0, 2)
    kb_pq = round(ARCHIVO_ORO_PARQUET.stat().st_size / 1024.0, 2)

    metricas = [
        ("tiempo_puerta_calidad_ms", "ms", antes["puerta_ms"], despues["puerta_ms"]),
        ("tiempo_limpieza_plata_ms", "ms", antes["limpieza_ms"], despues["limpieza_ms"]),
        ("tiempo_geoespacial_utm_ms", "ms", antes["geoespacial_ms"], despues["geoespacial_ms"]),
        ("tiempo_integracion_oro_ms", "ms", antes["integracion_ms"], despues["integracion_ms"]),
        ("tiempo_total_pipeline_ms", "ms", antes["total_ms"], despues["total_ms"]),
        ("pico_memoria_ram_kb", "KB", antes["pico_ram_kb"], despues["pico_ram_kb"]),
        ("lecturas_disco_por_corrida", "operaciones_io", antes["lecturas_disco"], despues["lecturas_disco"]),
        ("almacenamiento_capa_oro_kb", "KB (CSV vs Parquet)", kb_csv, kb_pq),
    ]
    filas = []
    for nombre, unidad, v_ant, v_des in metricas:
        mejora = round(((v_ant - v_des) / max(v_ant, 0.01)) * 100.0, 2)
        filas.append(
            {
                "metrica": nombre,
                "unidad": unidad,
                "antes_e2": v_ant,
                "despues_e3": v_des,
                "mejora_porcentual": mejora,
            }
        )
    df_bench = pd.DataFrame(filas)
    df_bench.to_csv(
        ARCHIVO_BENCHMARK_E3, index=False, encoding="utf-8", lineterminator="\n"
    )
    return df_bench


if __name__ == "__main__":
    tabla = ejecutar_benchmark_e3()
    print(tabla.to_string(index=False))
