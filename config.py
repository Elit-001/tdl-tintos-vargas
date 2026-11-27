"""Configuración centralizada de rutas, 10 municipios de Colima y constantes TDL.

Cumple el Principio de Responsabilidad Única (SRP): centraliza rutas Medallion,
los 10 municipios agroproductores de Colima, mercados reales SNIIM (incluyendo
Colima), compradores ancla con demandas reales y flota logística escalonada.
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
# 2. COORDENADAS REALES DE LOS 10 MUNICIPIOS DE COLIMA
# ==============================================================================
ZONAS_AGRICOLAS_COLIMA: dict[str, dict[str, float]] = {
    "Colima": {"latitud": 19.2433, "longitud": -103.7247},
    "Villa de Álvarez": {"latitud": 19.2669, "longitud": -103.7369},
    "Comala": {"latitud": 19.3264, "longitud": -103.7594},
    "Cuauhtémoc": {"latitud": 19.3286, "longitud": -103.6028},
    "Coquimatlán": {"latitud": 19.2058, "longitud": -103.8092},
    "Ixtlahuacán": {"latitud": 19.0019, "longitud": -103.7364},
    "Minatitlán": {"latitud": 19.3858, "longitud": -104.0575},
    "Tecomán": {"latitud": 18.9142, "longitud": -103.8753},
    "Armería": {"latitud": 18.9378, "longitud": -103.9644},
    "Manzanillo": {"latitud": 19.0522, "longitud": -104.3158},
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
# 4. PARÁMETROS DE FUENTES REALES (OPEN-METEO, SNIIM OFICIAL Y OSRM/OSM)
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
URL_TABLA_HISTORICA_SNIIM: str = (
    "http://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx"
)

FECHA_INICIO_HISTORICO: str = "2022-11-01"
FECHA_FIN_HISTORICO: str = "2026-10-31"
PERIODOS_MINIMOS_RUBRICA: int = 36
PERIODOS_HISTORICOS_META: int = 48

# ==============================================================================
# 5. CATÁLOGOS AGROCOMERCIALES REALES (CON COLIMA COMO PLAZA CENTRAL)
# ==============================================================================
CULTIVOS_OBJETIVO: list[str] = [
    "Limón Mexicano",
    "Papaya Maradol",
    "Plátano Chiapas",
    "Aguacate Hass",
]

CENTRALES_ABASTO: list[str] = [
    "Colima",
    "Guadalajara",
    "Morelia",
    "CDMX-Iztapalapa",
    "Monterrey",
]

DESTINOS_SNIIM_IDS: dict[str, int] = {
    "Colima": 80,
    "Guadalajara": 140,
    "Morelia": 160,
    "CDMX-Iztapalapa": 100,
    "Monterrey": 190,
}

PRODUCTOS_SNIIM_IDS: dict[str, list[int]] = {
    "Limón Mexicano": [421, 419, 417],
    "Papaya Maradol": [609, 623],
    "Plátano Chiapas": [663, 735, 670, 732],
    "Aguacate Hass": [133, 136],
}

COSTO_PRODUCCION_CAMPO_MXN_KG: dict[str, float] = {
    "Limón Mexicano": 9.80,
    "Papaya Maradol": 7.40,
    "Plátano Chiapas": 6.20,
    "Aguacate Hass": 26.50,
}

FLETE_NACIONAL_DESDE_COLIMA_MXN_KG: dict[str, float] = {
    "Colima": 0.65,
    "Guadalajara": 2.15,
    "Morelia": 2.65,
    "CDMX-Iztapalapa": 4.25,
    "Monterrey": 5.85,
}

MAPEO_CULTIVO_ZONA_ORIGEN: dict[str, str] = {
    "Limón Mexicano": "Tecomán",
    "Papaya Maradol": "Armería",
    "Plátano Chiapas": "Manzanillo",
    "Aguacate Hass": "Comala",
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
# 6. RED GEOESPACIAL ESTATAL (10 MUNICIPIOS X 6 COMPRADORES EN COLIMA) Y FLOTA
# ==============================================================================
URL_BASE_OVERPASS: str = "https://overpass-api.de"
URL_API_OVERPASS: str = "https://overpass-api.de/api/interpreter"
URL_BASE_OSRM: str = "https://router.project-osrm.org"
URL_TABLA_OSRM: str = "https://router.project-osrm.org/table/v1/driving"

EPSG_WGS84: str = "EPSG:4326"
EPSG_UTM_COLIMA: str = "EPSG:32613"

FACTOR_SINUOSIDAD_VIAL: float = 1.32
COSTO_FLETE_MXN_POR_KM: float = 18.50
COSTO_MANIOBRA_LOTE_MXN: float = 220.0
PESO_LOTE_CONSOLIDADO_KG: float = 1000.0
COMISION_BROKERAGE_PCT: float = 8.5
DESCUENTO_COYOTE_PCT: float = 38.0

NODOS_PRODUCTORES_COLIMA: dict[str, dict[str, str | float]] = {
    "Colima": {
        "municipio": "Colima",
        "latitud": 19.2433,
        "longitud": -103.7247,
        "cultivo_principal": "Limón Mexicano",
    },
    "Villa de Álvarez": {
        "municipio": "Villa de Álvarez",
        "latitud": 19.2669,
        "longitud": -103.7369,
        "cultivo_principal": "Papaya Maradol",
    },
    "Comala": {
        "municipio": "Comala",
        "latitud": 19.3264,
        "longitud": -103.7594,
        "cultivo_principal": "Aguacate Hass",
    },
    "Cuauhtémoc": {
        "municipio": "Cuauhtémoc",
        "latitud": 19.3286,
        "longitud": -103.6028,
        "cultivo_principal": "Aguacate Hass",
    },
    "Coquimatlán": {
        "municipio": "Coquimatlán",
        "latitud": 19.2058,
        "longitud": -103.8092,
        "cultivo_principal": "Limón Mexicano",
    },
    "Ixtlahuacán": {
        "municipio": "Ixtlahuacán",
        "latitud": 19.0019,
        "longitud": -103.7364,
        "cultivo_principal": "Papaya Maradol",
    },
    "Minatitlán": {
        "municipio": "Minatitlán",
        "latitud": 19.3858,
        "longitud": -104.0575,
        "cultivo_principal": "Aguacate Hass",
    },
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
}

COMPRADORES_ANCLA_COLIMA: dict[str, dict[str, str | float]] = {
    "Mercado Constitución Colima": {
        "municipio": "Colima",
        "latitud": 19.2402,
        "longitud": -103.7299,
        "demanda_lote_kg": 1000.0,
        "prima_comercial_pct": 3.5,
    },
    "Walmart Colima": {
        "municipio": "Colima",
        "latitud": 19.2386,
        "longitud": -103.7156,
        "demanda_lote_kg": 1200.0,
        "prima_comercial_pct": 7.5,
    },
    "Soriana Híper Villa de Álvarez": {
        "municipio": "Villa de Álvarez",
        "latitud": 19.2726,
        "longitud": -103.7374,
        "demanda_lote_kg": 900.0,
        "prima_comercial_pct": 6.2,
    },
    "Bodega Aurrera Tecomán": {
        "municipio": "Tecomán",
        "latitud": 18.9223,
        "longitud": -103.8834,
        "demanda_lote_kg": 1500.0,
        "prima_comercial_pct": 5.0,
    },
    "Mi Bodega Aurrera Armería": {
        "municipio": "Armería",
        "latitud": 18.9349,
        "longitud": -103.9701,
        "demanda_lote_kg": 950.0,
        "prima_comercial_pct": 4.8,
    },
    "Soriana Híper Manzanillo": {
        "municipio": "Manzanillo",
        "latitud": 19.1039,
        "longitud": -104.3267,
        "demanda_lote_kg": 1200.0,
        "prima_comercial_pct": 6.8,
    },
}

FLOTA_VEHICULAR_COLIMA: list[dict[str, str | float | bool]] = [
    {
        "vehiculo": "Camioneta Pickup (<= 850 kg)",
        "capacidad_max_kg": 850.0,
        "maniobra_fija_mxn": 180.0,
        "tarifa_km_mxn": 12.50,
        "refrigerado": False,
    },
    {
        "vehiculo": "Camión Rabón 3.5 Ton (851 - 3,500 kg)",
        "capacidad_max_kg": 3500.0,
        "maniobra_fija_mxn": 380.0,
        "tarifa_km_mxn": 19.50,
        "refrigerado": False,
    },
    {
        "vehiculo": "Torton Refrigerado (3,501 - 10,000 kg)",
        "capacidad_max_kg": 10000.0,
        "maniobra_fija_mxn": 750.0,
        "tarifa_km_mxn": 28.00,
        "refrigerado": True,
    },
]

COLUMNAS_LINAJE_ORO: list[str] = [
    "linaje_id_registro",
    "linaje_archivo_bronce",
    "linaje_sha256_bronce",
    "linaje_fecha_ingesta_utc",
    "linaje_fuente",
]
