"""Script orquestador principal de captura de datos para la Capa Bronce (E0).

Ejecuta secuencialmente los extractores de clima (Open-Meteo) y precios (SNIIM),
valida el cumplimiento de >= 48 periodos históricos (>= 36 requeridos en rúbrica)
y presenta un resumen ejecutivo en consola.
"""

import pandas as pd

from config import (
    ARCHIVO_CLIMA_DIARIO,
    ARCHIVO_CLIMA_MENSUAL,
    ARCHIVO_PRECIOS_DIARIO,
    ARCHIVO_PRECIOS_MENSUAL,
    NOMBRE_OBSERVATORIO,
    PERIODOS_HISTORICOS_META,
    PERIODOS_MINIMOS_RUBRICA,
    RUTA_BITACORA,
)
from extractores.extractor_api_clima import ejecutar_extractor_clima
from extractores.extractor_web_precios import ejecutar_extractor_precios


def verificar_archivos_bronce() -> dict[str, int]:
    """Verifica existencia y cantidad mínima de periodos históricos en Capa Bronce."""
    rutas_esperadas = [
        ARCHIVO_CLIMA_MENSUAL,
        ARCHIVO_CLIMA_DIARIO,
        ARCHIVO_PRECIOS_MENSUAL,
        ARCHIVO_PRECIOS_DIARIO,
    ]
    for ruta in rutas_esperadas:
        if not ruta.exists():
            raise FileNotFoundError(f"Archivo faltante en Capa Bronce: {ruta}")

    df_clima = pd.read_csv(ARCHIVO_CLIMA_MENSUAL)
    df_precios = pd.read_csv(ARCHIVO_PRECIOS_MENSUAL)
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
    }


def mostrar_resumen_consola(
    resumen_clima: dict[str, int],
    resumen_precios: dict[str, int],
    verificacion: dict[str, int],
) -> None:
    """Imprime en consola el reporte consolidado de la ejecución en Capa Bronce."""
    print("=" * 72)
    print(f" RESUMEN DE CAPTURA - {NOMBRE_OBSERVATORIO} (ENTREGA E0)")
    print("=" * 72)
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
    print(f" [Calidad]  Bitácora activa   : {RUTA_BITACORA}")
    print("=" * 72)


def ejecutar_captura_completa() -> None:
    """Ejecuta en orden ambos extractores, valida Bronce y muestra resultados."""
    resumen_clima = ejecutar_extractor_clima()
    resumen_precios = ejecutar_extractor_precios()
    verificacion = verificar_archivos_bronce()
    mostrar_resumen_consola(resumen_clima, resumen_precios, verificacion)


if __name__ == "__main__":
    ejecutar_captura_completa()

