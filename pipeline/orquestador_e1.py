"""Orquestador Principal del Pipeline Medallion para la Entrega E1.

Ejecuta secuencialmente:
1. Puerta de Calidad (Bronce -> Plata y Cuarentena con Pandera, 0% borrado silencioso)
2. Limpieza Estadística (Diagnóstico MCAR/MAR, Imputación, IQR, Min-Max, Discretización)
3. Integración Relacional (Plata -> data/oro/dataset_analitico.csv y diccionario_datos.md)
"""

from config import (
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    NOMBRE_OBSERVATORIO,
)
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
    res_oro: dict[str, int | float],
) -> None:
    """Imprime en consola el dictamen de ejecución del pipeline Medallion E1."""
    print("=" * 74)
    print(f" PIPELINE MEDALLION E1 - {NOMBRE_OBSERVATORIO}")
    print("=" * 74)
    c_cl, c_pr = res_calidad["clima"], res_calidad["precios"]
    print(
        f" [1. Puerta Calidad] Clima  : Bronce={c_cl['bronce']} -> "
        f"Plata={c_cl['plata']} | Cuarentena={c_cl['cuarentena']}"
    )
    print(
        f" [1. Puerta Calidad] Precios: Bronce={c_pr['bronce']} -> "
        f"Plata={c_pr['plata']} | Cuarentena={c_pr['cuarentena']}"
    )
    print(
        f" [2. Limpieza Plata] Atípicos IQR tratados (winsorizados): "
        f"Clima={res_limpieza['atipicos_clima']} | Precios={res_limpieza['atipicos_precios']}"
    )
    print(
        f" [3. Integración Oro] Dataset Analítico: {res_oro['filas_oro']} filas x "
        f"{res_oro['columnas_oro']} cols (Completitud={res_oro['completitud_pct']}%)"
    )
    print(f" [Artefacto Oro]     {ARCHIVO_ORO_ANALITICO}")
    print(f" [Diccionario Oro]   {ARCHIVO_DICCIONARIO_ORO}")
    print("=" * 74)


def ejecutar_pipeline_e1() -> dict[str, object]:
    """Ejecuta de punta a punta las tres etapas de procesamiento de la Entrega E1."""
    res_calidad = ejecutar_puerta_calidad()
    verificar_conservacion_registros(res_calidad)
    res_limpieza = ejecutar_limpieza_plata()
    res_oro = ejecutar_integracion_oro()
    mostrar_resumen_pipeline_e1(res_calidad, res_limpieza, res_oro)
    return {"calidad": res_calidad, "limpieza": res_limpieza, "oro": res_oro}


if __name__ == "__main__":
    ejecutar_pipeline_e1()

