"""Configuración centralizada de rutas, coordenadas y constantes de AgroPulse TDL.

Cumple el Principio de Responsabilidad Única (SRP) de la rúbrica E0 de Ingeniería
de Datos al evitar rutas o parámetros hardcodeados en los módulos del proyecto.
"""

from pathlib import Path

# ==============================================================================
# 1. RUTAS CENTRALIZADAS DEL PROYECTO (ARQUITECTURA MEDALLION)
# ==============================================================================
RUTA_RAIZ: Path = Path(__file__).resolve().parent

RUTA_DATOS: Path = RUTA_RAIZ / "data"
DATA_BRONCE: Path = RUTA_DATOS / "bronce"
DATA_PLATA: Path = RUTA_DATOS / "plata"
DATA_ORO: Path = RUTA_DATOS / "oro"
DATA_CUARENTENA: Path = RUTA_DATOS / "cuarentena"

RUTA_CALIDAD: Path = RUTA_RAIZ / "calidad"
RUTA_BITACORA: Path = RUTA_CALIDAD / "bitacora_captura.csv"

ARCHIVO_CLIMA_MENSUAL: Path = DATA_BRONCE / "clima_historico_mensual.csv"
ARCHIVO_CLIMA_DIARIO: Path = DATA_BRONCE / "clima_captura_diaria.csv"
ARCHIVO_PRECIOS_MENSUAL: Path = DATA_BRONCE / "precios_agro_historico_mensual.csv"
ARCHIVO_PRECIOS_DIARIO: Path = DATA_BRONCE / "precios_captura_diaria.csv"

ARCHIVO_PLATA_CLIMA: Path = DATA_PLATA / "clima_validado_plata.csv"
ARCHIVO_PLATA_PRECIOS: Path = DATA_PLATA / "precios_validados_plata.csv"
ARCHIVO_PLATA_CLIMA_LIMPIO: Path = DATA_PLATA / "clima_limpio_plata.csv"
ARCHIVO_PLATA_PRECIOS_LIMPIO: Path = DATA_PLATA / "precios_limpios_plata.csv"

ARCHIVO_CUARENTENA_CLIMA: Path = DATA_CUARENTENA / "clima_rechazados_cuarentena.csv"
ARCHIVO_CUARENTENA_PRECIOS: Path = DATA_CUARENTENA / "precios_rechazados_cuarentena.csv"

ARCHIVO_ORO_ANALITICO: Path = DATA_ORO / "dataset_analitico.csv"
ARCHIVO_DICCIONARIO_ORO: Path = DATA_ORO / "diccionario_datos.md"
ARCHIVO_PRONOSTICOS_ORO: Path = DATA_ORO / "pronosticos_e1.csv"

ARCHIVO_GEOESPACIAL_NODOS: Path = DATA_BRONCE / "nodos_geoespaciales_colima.csv"
ARCHIVO_PLATA_GEOESPACIAL: Path = DATA_PLATA / "nodos_geoespaciales_plata.csv"
ARCHIVO_CUARENTENA_GEOESPACIAL: Path = (
    DATA_CUARENTENA / "nodos_geoespaciales_cuarentena.csv"
)
ARCHIVO_ORO_RUTAS_FLETE: Path = DATA_ORO / "rutas_flete_colima.csv"
ARCHIVO_ORO_GEOJSON_RUTAS: Path = DATA_ORO / "rutas_flete_colima.geojson"
ARCHIVO_ORO_PARQUET: Path = DATA_ORO / "dataset_analitico.parquet"

DATA_PUBLICADO: Path = RUTA_DATOS / "publicado"
ARCHIVO_PUBLICADO_CSV: Path = DATA_PUBLICADO / "agropulse_colima_curado.csv"
ARCHIVO_PUBLICADO_PARQUET: Path = DATA_PUBLICADO / "agropulse_colima_curado.parquet"
ARCHIVO_PUBLICADO_LICENCIA: Path = DATA_PUBLICADO / "LICENSE"
ARCHIVO_PUBLICADO_README: Path = DATA_PUBLICADO / "README.md"
ARCHIVO_BENCHMARK_E3: Path = RUTA_CALIDAD / "benchmark_e3.csv"

# ==============================================================================
# 2. COORDENADAS DE ZONAS AGROPRODUCTORAS DE COLIMA
# ==============================================================================
ZONAS_AGRICOLAS_COLIMA: dict[str, dict[str, float]] = {
    "Tecomán": {"latitud": 18.91, "longitud": -103.87},
    "Armería": {"latitud": 18.93, "longitud": -103.96},
    "Manzanillo": {"latitud": 19.05, "longitud": -104.31},
}

# ==============================================================================
# 3. CONSTANTES ÉTICAS DE EXTRACCIÓN Y RED
# ==============================================================================
NOMBRE_OBSERVATORIO: str = "AgroPulse TDL"
USER_AGENT_ACADEMICO: str = (
    "TDL-Observatorio/1.0 (proyecto academico; contacto: carlos.tintos@tecnm.mx)"
)
PAUSA_MINIMA_SEGUNDOS: float = 1.5
MAX_REINTENTOS_HTTP: int = 3
TIMEOUT_HTTP_SEGUNDOS: int = 20

# ==============================================================================
# 4. PARÁMETROS DE FUENTES DE DATOS Y VENTANA HISTÓRICA (>= 48 MESES)
# ==============================================================================
URL_API_CLIMA_HISTORICO: str = "https://archive-api.open-meteo.com/v1/archive"
URL_API_CLIMA_PRONOSTICO: str = "https://api.open-meteo.com/v1/forecast"
ZONA_HORARIA_LOCAL: str = "America/Mexico_City"

VARIABLES_OPEN_METEO: list[str] = [
    "temperature_2m_max",
    "temperature_2m_mean",
    "precipitation_sum",
    "et0_fao_evapotranspiration",
    "relative_humidity_2m_mean",
]

URL_BASE_SNIIM: str = "http://www.economia-sniim.gob.mx"
URL_PORTAL_SNIIM: str = (
    "http://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx"
)

FECHA_INICIO_HISTORICO: str = "2022-11-01"
FECHA_FIN_HISTORICO: str = "2026-10-31"
PERIODOS_MINIMOS_RUBRICA: int = 36
PERIODOS_HISTORICOS_META: int = 48

# ==============================================================================
# 5. CATÁLOGOS AGROCOMERCIALES Y BITÁCORA DE CALIDAD
# ==============================================================================
CULTIVOS_OBJETIVO: list[str] = [
    "Limón Mexicano",
    "Papaya Maradol",
    "Plátano Chiapas",
    "Aguacate Hass",
]

CENTRALES_ABASTO: list[str] = [
    "CDMX-Iztapalapa",
    "Guadalajara",
    "Monterrey",
    "Occidente",
]

MAPEO_CULTIVO_ZONA_ORIGEN: dict[str, str] = {
    "Limón Mexicano": "Tecomán",
    "Papaya Maradol": "Armería",
    "Plátano Chiapas": "Manzanillo",
    "Aguacate Hass": "Tecomán",
}

COLUMNAS_BITACORA: list[str] = [
    "timestamp_inicio",
    "timestamp_fin",
    "fuente",
    "estado",
    "registros_obtenidos",
    "tiempo_segundos",
    "mensaje_error",
]

# ==============================================================================
# 6. PARÁMETROS GEOESPACIALES, LOGÍSTICA DE FLETE Y LINAJE TOTAL (ENTREGA E2)
# ==============================================================================
URL_BASE_OVERPASS: str = "https://overpass-api.de"
URL_API_OVERPASS: str = "https://overpass-api.de/api/interpreter"

EPSG_WGS84: str = "EPSG:4326"
EPSG_UTM_COLIMA: str = "EPSG:32613"

FACTOR_SINUOSIDAD_VIAL: float = 1.24
COSTO_FLETE_MXN_POR_KM: float = 18.50
COSTO_MANIOBRA_LOTE_MXN: float = 220.0
PESO_LOTE_CONSOLIDADO_KG: float = 400.0

NODOS_PRODUCTORES_COLIMA: dict[str, dict[str, str | float]] = {
    "Tecomán": {
        "municipio": "Tecomán",
        "latitud": 18.9142,
        "longitud": -103.8753,
        "cultivo_principal": "Limón Mexicano",
    },
    "Armería": {
        "municipio": "Armería",
        "latitud": 18.9378,
        "longitud": -103.9644,
        "cultivo_principal": "Papaya Maradol",
    },
    "Manzanillo": {
        "municipio": "Manzanillo",
        "latitud": 19.0522,
        "longitud": -104.3158,
        "cultivo_principal": "Plátano Chiapas",
    },
    "Coquimatlán": {
        "municipio": "Coquimatlán",
        "latitud": 19.2058,
        "longitud": -103.8092,
        "cultivo_principal": "Aguacate Hass",
    },
}

COMPRADORES_ANCLA_COLIMA: dict[str, dict[str, str | float]] = {
    "Walmart Colima": {
        "municipio": "Colima",
        "latitud": 19.2614,
        "longitud": -103.7153,
        "demanda_lote_kg": 400.0,
        "prima_comercial_pct": 6.5,
    },
    "Empacadora San José": {
        "municipio": "Tecomán",
        "latitud": 18.9218,
        "longitud": -103.8842,
        "demanda_lote_kg": 400.0,
        "prima_comercial_pct": 5.0,
    },
    "Agroindustriales de Colima": {
        "municipio": "Villa de Álvarez",
        "latitud": 19.2391,
        "longitud": -103.7485,
        "demanda_lote_kg": 400.0,
        "prima_comercial_pct": 5.8,
    },
    "Limones Prolim": {
        "municipio": "Armería",
        "latitud": 18.9385,
        "longitud": -103.9621,
        "demanda_lote_kg": 400.0,
        "prima_comercial_pct": 4.5,
    },
}

COLUMNAS_LINAJE_ORO: list[str] = [
    "linaje_id_registro",
    "linaje_archivo_bronce",
    "linaje_sha256_bronce",
    "linaje_fecha_ingesta_utc",
    "linaje_fuente",
]
