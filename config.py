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

COLUMNAS_BITACORA: list[str] = [
    "timestamp_inicio",
    "timestamp_fin",
    "fuente",
    "estado",
    "registros_obtenidos",
    "tiempo_segundos",
    "mensaje_error",
]
