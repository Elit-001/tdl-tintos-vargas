"""Orquestador Principal Optimizado del Pipeline Medallion (Entregas E1, E2 y E3).

Ejecuta secuencialmente en memoria sin relecturas redundantes de disco:
1. Puerta de Calidad (Bronce -> Plata y Cuarentena con esquemas Pandera cacheados)
2. Limpieza Estadística Vectorizada (MCAR/MAR, IQR en NumPy, Min-Max, categorías)
3. Procesamiento Geoespacial Vectorizado (EPSG:32613 UTM 13N sin .iterrows())
4. Integración Relacional y Linaje Total SHA-256 (CSV LF + Parquet en Capa Oro)
5. Publicación Abierta Curada (data/publicado/ con licencia CC BY 4.0)
"""

from config import (
    ARCHIVO_DICCIONARIO_ORO,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PUBLICADO_CSV,
    NOMBRE_OBSERVATORIO,
)
from pipeline.geoespacial import procesar_geoespacial_en_memoria
from pipeline.integracion import generar_diccionario_datos, integrar_en_memoria
from pipeline.limpieza import limpiar_marcos_en_memoria
from pipeline.publicacion import (
    enriquecer_con_ruta_optima_local,
    publicar_dataset_curado,
)
from pipeline.puerta_calidad import ejecutar_puerta_calidad_en_memoria


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
    res_pub: dict[str, int | float],
) -> None:
    """Imprime en consola el dictamen de ejecución del pipeline Medallion E1-E3."""
    print("=" * 76)
    print(f" PIPELINE MEDALLION OPTIMIZADO E1-E3 - {NOMBRE_OBSERVATORIO}")
    print("=" * 76)
    c_cl, c_pr = res_calidad["clima"], res_calidad["precios"]
    print(
        f" [1. Puerta Calidad] Clima={c_cl['plata']}/{c_cl['bronce']} | "
        f"Precios={c_pr['plata']}/{c_pr['bronce']} (Cuarentena=0)"
    )
    print(
        f" [2. Limpieza Plata] Atípicos IQR tratados: "
        f"Clima={res_limpieza['atipicos_clima']} | Precios={res_limpieza['atipicos_precios']}"
    )
    print(
        f" [3. GeoPandas UTM ] Rutas={res_geo['rutas_calculadas']} | "
        f"Dist. media={res_geo['distancia_media_km']} km | Flete=${res_geo['flete_medio_mxn_kg']}/kg"
    )
    print(
        f" [4. Integración Oro] Dataset={res_oro['filas_oro']}x{res_oro['columnas_oro']} "
        f"(Completitud={res_oro['completitud_pct']}%)"
    )
    print(
        f" [5. Publicado E3  ] Curado={res_pub['filas_publicadas']}x{res_pub['columnas_publicadas']} "
        f"| CSV={res_pub['tamano_csv_kb']} KB vs Parquet={res_pub['tamano_parquet_kb']} KB"
    )
    print(f" [Artefactos Clave]  {ARCHIVO_ORO_ANALITICO.name} | {ARCHIVO_ORO_RUTAS_FLETE.name}")
    print(f" [Publicado / Dicc]  {ARCHIVO_PUBLICADO_CSV.name} | {ARCHIVO_DICCIONARIO_ORO.name}")
    print("=" * 76)


def ejecutar_pipeline_e1(silencioso: bool = False) -> dict[str, object]:
    """Ejecuta de punta a punta las etapas Medallion E1-E3 pasando datos en memoria."""
    res_calidad, marcos_plata = ejecutar_puerta_calidad_en_memoria()
    verificar_conservacion_registros(res_calidad)
    res_limpieza, df_cl_limpio, df_pr_limpio = limpiar_marcos_en_memoria(
        marcos_plata["clima"], marcos_plata["precios"]
    )
    res_geo, df_rutas = procesar_geoespacial_en_memoria(
        marcos_plata.get("geoespacial")
    )
    res_oro, df_oro = integrar_en_memoria(
        df_pr_limpio, df_cl_limpio, df_rutas, escribir_diccionario=False
    )
    res_pub = publicar_dataset_curado(df_oro, df_rutas)
    df_pub = enriquecer_con_ruta_optima_local(df_oro, df_rutas)
    generar_diccionario_datos(
        df_oro, ARCHIVO_DICCIONARIO_ORO, df_rutas_mem=df_rutas, df_pub_mem=df_pub
    )
    if not silencioso:
        mostrar_resumen_pipeline_e1(
            res_calidad, res_limpieza, res_geo, res_oro, res_pub
        )
    return {
        "calidad": res_calidad,
        "limpieza": res_limpieza,
        "geoespacial": res_geo,
        "oro": res_oro,
        "publicado": res_pub,
    }


if __name__ == "__main__":
    ejecutar_pipeline_e1()
