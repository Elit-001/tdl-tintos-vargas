"""Script orquestador principal de captura de datos para la Capa Bronce (E0-E2).

Ejecuta secuencialmente los extractores de clima (Open-Meteo), precios (SNIIM)
y nodos geoespaciales de Colima (OpenStreetMap), valida los archivos crudos y
sus fichas .meta.json con hash SHA-256, y presenta un resumen en consola.
"""

import pandas as pd

from config import (
    ARCHIVO_CLIMA_DIARIO,
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_GEOESPACIAL_NODOS,
    ARCHIVO_PRECIOS_DIARIO,
    ARCHIVO_PRECIOS_MENSUAL,
    NOMBRE_OBSERVATORIO,
    PERIODOS_HISTORICOS_META,
    PERIODOS_MINIMOS_RUBRICA,
    RUTA_BITACORA,
)
from extractores.extractor_api_clima import ejecutar_extractor_clima
from extractores.extractor_geoespacial import ejecutar_extractor_geoespacial
from extractores.extractor_web_precios import ejecutar_extractor_precios


def verificar_archivos_bronce() -> dict[str, int]:
    """Verifica existencia, fichas .meta.json y periodos históricos en Capa Bronce."""
    rutas_esperadas = [
        ARCHIVO_CLIMA_MENSUAL,
        ARCHIVO_CLIMA_DIARIO,
        ARCHIVO_PRECIOS_MENSUAL,
        ARCHIVO_PRECIOS_DIARIO,
        ARCHIVO_GEOESPACIAL_NODOS,
    ]
    for ruta in rutas_esperadas:
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo faltante en Capa Bronce: {ruta}")
        ficha_meta = ruta.with_name(f"{ruta.name}.meta.json")
        if not ficha_meta.exists():
            raise FileNotFoundError(f"Ficha .meta.json faltante: {ficha_meta}")

    df_clima = pd.read_csv(ARCHIVO_CLIMA_MENSUAL)
    df_precios = pd.read_csv(ARCHIVO_PRECIOS_MENSUAL)
    df_geo = pd.read_csv(ARCHIVO_GEOESPACIAL_NODOS)
    periodos_clima = int(df_clima["periodo_mensual"].nunique())
    periodos_precios = int(df_precios["periodo_mensual"].nunique())

    if (
        periodos_clima < PERIODOS_HISTORICOS_META
        or periodos_precios < PERIODOS_HISTORICOS_META
    ):
        raise ValueError(
            f"Periodos insuficientes: clima={periodos_clima}, precios={periodos_precios}"
        )
    return {
        "periodos_clima": periodos_clima,
        "periodos_precios": periodos_precios,
        "nodos_geo": len(df_geo),
    }


def mostrar_resumen_consola(
    resumen_clima: dict[str, int],
    resumen_precios: dict[str, int],
    resumen_geo: dict[str, int],
    verificacion: dict[str, int],
) -> None:
    """Imprime en consola el reporte consolidado de la ejecución en Capa Bronce."""
    print("=" * 74)
    print(f" RESUMEN DE CAPTURA MULTIFUENTE - {NOMBRE_OBSERVATORIO} (E0-E2)")
    print("=" * 74)
    print(
        f" [Fuente 1] Clima Open-Meteo  : {resumen_clima['mensuales']} reg. mensuales "
        f"| {resumen_clima['diarios']} reg. diarios "
        f"({verificacion['periodos_clima']} periodos >= {PERIODOS_MINIMOS_RUBRICA} req.)"
    )
    print(
        f" [Fuente 2] Precios SNIIM Web : {resumen_precios['mensuales']} reg. mensuales "
        f"| {resumen_precios['diarios']} reg. diarios "
        f"({verificacion['periodos_precios']} periodos >= {PERIODOS_MINIMOS_RUBRICA} req.)"
    )
    print(
        f" [Fuente 3] Nodos OSM Colima  : {resumen_geo['productores']} productores "
        f"| {resumen_geo['compradores']} compradores ancla "
        f"({verificacion['nodos_geo']} nodos totales)"
    )
    print(f" [Calidad]  Bitácora activa   : {RUTA_BITACORA}")
    print("=" * 74)


def ejecutar_captura_completa() -> None:
    """Ejecuta en orden los tres extractores, valida Bronce y muestra resultados."""
    resumen_clima = ejecutar_extractor_clima()
    resumen_precios = ejecutar_extractor_precios()
    resumen_geo = ejecutar_extractor_geoespacial()
    verificacion = verificar_archivos_bronce()
    mostrar_resumen_consola(resumen_clima, resumen_precios, resumen_geo, verificacion)


if __name__ == "__main__":
    ejecutar_captura_completa()
