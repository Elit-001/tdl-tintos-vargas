"""Extractor de la Fuente 1: API Abierta de Clima (Open-Meteo Archive y Forecast).

Cumple el criterio E0 de Ingeniería de Datos y Análisis Estadístico al obtener
una serie histórica >= 48 meses (2022-2026) y captura diaria para las zonas
agroproductoras de Colima (Tecomán, Armería y Manzanillo) en Capa Bronce.
"""

import time
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import requests

from config import (
    ARCHIVO_CLIMA_DIARIO,
    ARCHIVO_CLIMA_MENSUAL,
    DATA_BRONCE,
    FECHA_FIN_HISTORICO,
    FECHA_INICIO_HISTORICO,
    MAX_REINTENTOS_HTTP,
    PAUSA_MINIMA_SEGUNDOS,
    TIMEOUT_HTTP_SEGUNDOS,
    URL_API_CLIMA_HISTORICO,
    URL_API_CLIMA_PRONOSTICO,
    USER_AGENT_ACADEMICO,
    VARIABLES_OPEN_METEO,
    ZONA_HORARIA_LOCAL,
    ZONAS_AGRICOLAS_COLIMA,
)
from extractores.base import ExtractorEtico, registrar_ejecucion_bitacora


def consultar_json_clima(
    url: str, parametros: dict[str, str | float | int]
) -> dict:
    """Realiza una consulta GET resiliente a Open-Meteo con cabecera académica."""
    cabeceras = {"User-Agent": USER_AGENT_ACADEMICO}
    ultimo_error: Exception | None = None
    for intento in range(1, MAX_REINTENTOS_HTTP + 1):
        try:
            respuesta = requests.get(
                url, params=parametros, headers=cabeceras, timeout=TIMEOUT_HTTP_SEGUNDOS
            )
            respuesta.raise_for_status()
            time.sleep(0.3)
            return respuesta.json()
        except requests.RequestException as error:
            ultimo_error = error
            if intento < MAX_REINTENTOS_HTTP:
                time.sleep(PAUSA_MINIMA_SEGUNDOS * intento)
    raise ConnectionError(f"Error al consultar Open-Meteo ({url}): {ultimo_error}")


def transformar_respuesta_diaria(
    datos_json: dict,
    zona: str,
    coords: dict[str, float],
    fecha_captura: str,
    fuente_origen: str,
) -> pd.DataFrame:
    """Convierte el bloque diario JSON de Open-Meteo en un DataFrame tabular crudo."""
    bloque_diario = datos_json["daily"]
    return pd.DataFrame(
        {
            "fecha": bloque_diario["time"],
            "zona_agricola": zona,
            "latitud": coords["latitud"],
            "longitud": coords["longitud"],
            "temperatura_max_c": bloque_diario["temperature_2m_max"],
            "temperatura_media_c": bloque_diario["temperature_2m_mean"],
            "precipitacion_acumulada_mm": bloque_diario["precipitation_sum"],
            "evapotranspiracion_mm": bloque_diario["et0_fao_evapotranspiration"],
            "humedad_relativa_pct": bloque_diario["relative_humidity_2m_mean"],
            "fecha_captura": fecha_captura,
            "fuente_origen": fuente_origen,
        }
    )


def agregar_historico_mensual(
    df_diario: pd.DataFrame, fecha_captura: str, fuente_origen: str
) -> pd.DataFrame:
    """Agrega los registros diarios en periodos mensuales (YYYY-MM) por región."""
    df_copia = df_diario.copy()
    df_copia["periodo_mensual"] = df_copia["fecha"].str.slice(0, 7)
    df_mensual = (
        df_copia.groupby(
            ["periodo_mensual", "zona_agricola", "latitud", "longitud"], as_index=False
        )
        .agg(
            temperatura_max_c=("temperatura_max_c", "mean"),
            temperatura_media_c=("temperatura_media_c", "mean"),
            precipitacion_acumulada_mm=("precipitacion_acumulada_mm", "sum"),
            evapotranspiracion_mm=("evapotranspiracion_mm", "sum"),
            humedad_relativa_pct=("humedad_relativa_pct", "mean"),
        )
        .round(2)
    )
    df_mensual["fecha_captura"] = fecha_captura
    df_mensual["fuente_origen"] = fuente_origen
    return df_mensual


def extraer_clima_historico(fecha_captura: str) -> pd.DataFrame:
    """Descarga y agrega 48 meses (2022-2026) de clima para las zonas de Colima."""
    fuente = "open_meteo_archive_api"
    marcos_zonas: list[pd.DataFrame] = []
    for zona, coords in ZONAS_AGRICOLAS_COLIMA.items():
        parametros: dict[str, str | float | int] = {
            "latitude": coords["latitud"],
            "longitude": coords["longitud"],
            "start_date": FECHA_INICIO_HISTORICO,
            "end_date": FECHA_FIN_HISTORICO,
            "daily": ",".join(VARIABLES_OPEN_METEO),
            "timezone": ZONA_HORARIA_LOCAL,
        }
        datos_json = consultar_json_clima(URL_API_CLIMA_HISTORICO, parametros)
        df_zona = transformar_respuesta_diaria(
            datos_json, zona, coords, fecha_captura, fuente
        )
        marcos_zonas.append(df_zona)
    df_total_diario = pd.concat(marcos_zonas, ignore_index=True)
    return agregar_historico_mensual(df_total_diario, fecha_captura, fuente)


def extraer_clima_diario(fecha_captura: str) -> pd.DataFrame:
    """Descarga la ventana reciente diaria de Open-Meteo Forecast para Colima."""
    fuente = "open_meteo_forecast_api"
    marcos_zonas: list[pd.DataFrame] = []
    for zona, coords in ZONAS_AGRICOLAS_COLIMA.items():
        parametros: dict[str, str | float | int] = {
            "latitude": coords["latitud"],
            "longitude": coords["longitud"],
            "daily": ",".join(VARIABLES_OPEN_METEO),
            "past_days": 7,
            "forecast_days": 1,
            "timezone": ZONA_HORARIA_LOCAL,
        }
        datos_json = consultar_json_clima(URL_API_CLIMA_PRONOSTICO, parametros)
        df_zona = transformar_respuesta_diaria(
            datos_json, zona, coords, fecha_captura, fuente
        )
        marcos_zonas.append(df_zona)
    return pd.concat(marcos_zonas, ignore_index=True)


def consolidar_csv_diario(df_nuevo: pd.DataFrame, ruta_csv: Path) -> pd.DataFrame:
    """Acumula las capturas diarias en Bronce evitando duplicados por fecha y zona."""
    if ruta_csv.exists():
        df_previo = pd.read_csv(ruta_csv)
        df_combinado = pd.concat([df_previo, df_nuevo], ignore_index=True)
        df_combinado = df_combinado.drop_duplicates(
            subset=["fecha", "zona_agricola"], keep="last"
        )
        return df_combinado.sort_values(["fecha", "zona_agricola"]).reset_index(
            drop=True
        )
    return df_nuevo.sort_values(["fecha", "zona_agricola"]).reset_index(drop=True)


def guardar_archivos_clima(
    df_mensual: pd.DataFrame, df_diario: pd.DataFrame
) -> dict[str, int]:
    """Persiste los DataFrames climáticos en Capa Bronce junto con sus fichas .meta.json."""
    DATA_BRONCE.mkdir(parents=True, exist_ok=True)
    df_mensual.to_csv(ARCHIVO_CLIMA_MENSUAL, index=False, encoding="utf-8")
    ExtractorEtico.generar_ficha_meta(ARCHIVO_CLIMA_MENSUAL, "open_meteo_archive_api")
    df_diario.to_csv(ARCHIVO_CLIMA_DIARIO, index=False, encoding="utf-8")
    ExtractorEtico.generar_ficha_meta(ARCHIVO_CLIMA_DIARIO, "open_meteo_forecast_api")
    return {"mensuales": len(df_mensual), "diarios": len(df_diario)}


def ejecutar_extractor_clima() -> dict[str, int]:
    """Orquesta la extracción climática completa, persiste en Bronce y registra bitácora."""
    inicio = time.perf_counter()
    ts_inicio = datetime.now(UTC).isoformat()
    fecha_hoy = datetime.now(UTC).strftime("%Y-%m-%d")
    try:
        df_mensual = extraer_clima_historico(fecha_hoy)
        df_diario = consolidar_csv_diario(
            extraer_clima_diario(fecha_hoy), ARCHIVO_CLIMA_DIARIO
        )
        conteo = guardar_archivos_clima(df_mensual, df_diario)
        total = conteo["mensuales"] + conteo["diarios"]
        ts_fin = datetime.now(UTC).isoformat()
        duracion = time.perf_counter() - inicio
        registrar_ejecucion_bitacora(
            ts_inicio, ts_fin, "api_open_meteo_clima", "EXITOSO", total, duracion
        )
        return conteo
    except Exception as error:
        ts_fin = datetime.now(UTC).isoformat()
        duracion = time.perf_counter() - inicio
        registrar_ejecucion_bitacora(
            ts_inicio, ts_fin, "api_open_meteo_clima", "ERROR", 0, duracion, str(error)
        )
        raise


if __name__ == "__main__":
    resumen = ejecutar_extractor_clima()
    print(f"Clima capturado exitosamente: {resumen}")
