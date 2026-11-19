"""Orquestador Principal del Pipeline Medallion para las Entregas E1 y E2.

Ejecuta secuencialmente:
1. Puerta de Calidad (Bronce -> Plata y Cuarentena con Pandera, 0% borrado silencioso)
2. Limpieza Estadística (Diagnóstico MCAR/MAR, Imputación, IQR, Min-Max, Discretización)
3. Procesamiento Geoespacial GeoPandas (EPSG:4326 -> EPSG:32613 UTM 13N y costos de flete)
4. Integración Relacional y Linaje Total SHA-256 (Plata -> Capa Oro y diccionario_datos.md)
"""

from config import (
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_RUTAS_FLETE,
    NOMBRE_OBSERVATORIO,
)
from pipeline.geoespacial import ejecutar_procesamiento_geoespacial
from pipeline.integracion import ejecutar_integracion_oro
from pipeline.limpieza import ejecutar_limpieza_plata
from pipeline.puerta_calidad import ejecutar_puerta_calidad


def verificar_conservacion_registros(
    res_calidad: dict[str, dict[str, int]]
) -> None:
    """Comprueba que ningún registro de Bronce se haya perdido silenciosamente."""
    for dominio, conteos in res_calidad.items():
        if conteos["bronce"] != (conteos["plata"] + conteos["cuarentena"]):
            raise ValueError(
                f"Violación de conservación en {dominio}: {conteos}"
            )


def mostrar_resumen_pipeline_e1(
    res_calidad: dict[str, dict[str, int]],
    res_limpieza: dict[str, int],
    res_geo: dict[str, int | float],
    res_oro: dict[str, int | float],
) -> None:
    """Imprime en consola el dictamen de ejecución del pipeline Medallion E1-E2."""
    print("=" * 76)
    print(f" PIPELINE MEDALLION E1-E2 - {NOMBRE_OBSERVATORIO}")
    print("=" * 76)
    c_cl, c_pr = res_calidad["clima"], res_calidad["precios"]
    print(
        f" [1. Puerta Calidad] Clima  : Bronce={c_cl['bronce']} -> "
        f"Plata={c_cl['plata']} | Cuarentena={c_cl['cuarentena']}"
    )
    print(
        f" [1. Puerta Calidad] Precios: Bronce={c_pr['bronce']} -> "
        f"Plata={c_pr['plata']} | Cuarentena={c_pr['cuarentena']}"
    )
    if "geoespacial" in res_calidad:
        c_geo = res_calidad["geoespacial"]
        print(
            f" [1. Puerta Calidad] Nodos  : Bronce={c_geo['bronce']} -> "
            f"Plata={c_geo['plata']} | Cuarentena={c_geo['cuarentena']}"
        )
    print(
        f" [2. Limpieza Plata] Atípicos IQR tratados (winsorizados): "
        f"Clima={res_limpieza['atipicos_clima']} | Precios={res_limpieza['atipicos_precios']}"
    )
    print(
        f" [3. GeoPandas UTM ] Rutas  : {res_geo['rutas_calculadas']} rutas "
        f"| Dist. media={res_geo['distancia_media_km']} km "
        f"| Flete medio=${res_geo['flete_medio_mxn_kg']}/kg"
    )
    print(
        f" [4. Integración Oro] Dataset Analítico: {res_oro['filas_oro']} filas x "
        f"{res_oro['columnas_oro']} cols (Completitud={res_oro['completitud_pct']}%)"
    )
    print(f" [Artefacto Oro 1]   {ARCHIVO_ORO_ANALITICO}")
    print(f" [Artefacto Oro 2]   {ARCHIVO_ORO_RUTAS_FLETE}")
    print(f" [Diccionario Oro]   {ARCHIVO_DICCIONARIO_ORO}")
    print("=" * 76)


def ejecutar_pipeline_e1() -> dict[str, object]:
    """Ejecuta de punta a punta las etapas de procesamiento Medallion E1 y E2."""
    res_calidad = ejecutar_puerta_calidad()
    verificar_conservacion_registros(res_calidad)
    res_limpieza = ejecutar_limpieza_plata()
    res_geo = ejecutar_procesamiento_geoespacial()
    res_oro = ejecutar_integracion_oro()
    mostrar_resumen_pipeline_e1(res_calidad, res_limpieza, res_geo, res_oro)
    return {
        "calidad": res_calidad,
        "limpieza": res_limpieza,
        "geoespacial": res_geo,
        "oro": res_oro,
    }


if __name__ == "__main__":
    ejecutar_pipeline_e1()
