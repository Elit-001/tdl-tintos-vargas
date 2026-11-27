# Relatoría Técnica y de Negocio — Etapa E3 (Optimización, Datos Abiertos y Análisis Multivariado)

* **Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etapa:** `E3 — Optimización Medida del Pipeline, Publicación Abierta (Datasheet) y Estadística Multivariada`
* **Autores:** Carlos Daniel Tintos Beltrán (*Data Engineer & Quality Lead E3*) y Oliver Vargas García (*Data Statistician*)
* **Fecha:** 25 de noviembre de 2026

---

## 1. Diagnóstico de Cuellos de Botella e Impacto Real de las Optimizaciones en `pipeline/`

Al instrumentar la versión E2 de nuestro pipeline Medallion con `time.perf_counter()` y `tracemalloc` en [`pipeline/benchmark_e3.py`](../pipeline/benchmark_e3.py), descubrimos tres cuellos de botella concretos que penalizaban la latencia, la memoria y las operaciones de entrada/salida:

1. **Iteraciones por Columna y Funciones `lambda` en Limpieza (`775.45 ms` en E2):**
   * En la versión previa, las funciones de imputación, detección de atípicos por Tukey ($1.5 \times \text{IQR}$) y escalado Min-Max recorrían columna por columna invocando `.groupby(...)[col].transform(...)` quince veces seguidas e interpolando series completas aun cuando el lote tenía $0\%$ de valores nulos, además de generar cuatro copias completas del DataFrame en cascada.
   * **Solución en E3 ([`pipeline/limpieza.py`](../pipeline/limpieza.py)):** Vectorizamos el cálculo de cuantiles, mínimos y máximos directamente sobre matrices contiguas de NumPy (`np.quantile`, `np.clip`) con factorización única de grupos (`pd.factorize`), agregamos evaluación rápida de nulos (`np.isnan(matriz).any()`) y habilitamos transformaciones en sitio (`en_sitio=True`). Esta sola mejora redujo el tiempo de la etapa de limpieza de **$775.45\text{ ms}$ a $244.81\text{ ms}$ ($+68.43\%$ más rápido, más de $3\times$ de aceleración)** y disminuyó el pico global de memoria RAM en un **$5.67\%$**.
2. **Relecturas Redundantes de Disco y Recálculo Repetido de Hashes SHA-256 (`13` lecturas I/O en E2):**
   * Anteriormente, cada etapa guardaba archivos intermedios en `data/plata/` y la siguiente etapa volvía a leerlos desde el sistema de archivos; además, `obtener_metadatos_linaje_bronce()` recalculaba desde disco el hash `SHA-256` de los CSV crudos en cada llamada.
   * **Solución en E3 ([`pipeline/geoespacial.py`](../pipeline/geoespacial.py) y [`pipeline/orquestador_e1.py`](../pipeline/orquestador_e1.py)):** Implementamos paso directo de DataFrames en memoria entre etapas (conservando la escritura de artefactos en Plata/Oro para trazabilidad y compatibilidad total con tests), reemplazamos los bucles `.iterrows()` geoespaciales por un producto cartesiano vectorizado (`how="cross"` + `np.hypot` + `shapely.linestrings`) e incorporamos la caché en memoria `_CACHE_META_BRONCE` invalidada por `mtime_ns` y tamaño de archivo. Las lecturas de disco cayeron de **$13$ a solo $3$ operaciones por corrida ($-76.92\%$)** y el tiempo total de extremo a extremo bajó un **$27.16\%$** ($1,952.67\text{ ms} \rightarrow 1,422.36\text{ ms}$).
3. **Eficiencia de Almacenamiento Columnar (`-81.67%` en Oro y `-85.35%` en Publicado):**
   * Al tipar variables categóricas de baja cardinalidad como `category` y métricas continuas como `float32` exclusivamente en la salida Apache Parquet, el tamaño en disco de la Capa Oro bajó de **$402.21\text{ KB}$ a $73.72\text{ KB}$** y el dataset publicado pasó de **$305.98\text{ KB}$ (CSV LF) a $44.81\text{ KB}$ (Parquet)**, manteniendo intacta la precisión decimal de los CSV auditados.

---

## 2. Decisiones de Curación Abierta (`CC BY 4.0`) y *Datasheet* Estandarizado

Para transformar a **AgroPulse TDL** en un bien público digital útil para investigadores, cooperativas agrícolas y estudiantes sin comprometer la ética de datos, creamos el módulo [`pipeline/publicacion.py`](../pipeline/publicacion.py) y redactamos [`docs/E3/datasheet.md`](E3/datasheet.md) siguiendo a Gebru et al.:

* **Curación enfocada al usuario externo:** En lugar de exponer las $41$ columnas internas de trabajo (que incluían banderas auxiliares de *winsorización* y columnas normalizadas duplicadas `*_norm`), seleccionamos las **$27$ variables sustantivas** e integramos en cada fila el comprador ancla óptimo de Colima, su distancia vial en km y el *spread* local por lote de $400\text{ kg}$.
* **Transparencia sobre límites de uso:** Documentamos explícitamente que el dataset contiene **$0\%$ de PII**, se distribuye bajo **Creative Commons Attribution 4.0 (`CC BY 4.0`)** y **no debe emplearse** para decisiones automatizadas de crédito individual ni especulación contra pequeños productores.

---

## 3. Valor de Negocio del Análisis Multivariado (PCA + MANOVA) y Cierre SQA

El notebook [`laboratorio/E3_multivariado_pca_manova.ipynb`](../laboratorio/E3_multivariado_pca_manova.ipynb) cerró el ciclo analítico del observatorio (Series de Tiempo en E1 $\rightarrow$ Diseño Factorial en E2 $\rightarrow$ Multivariado en E3):

* **PCA** demostró que las $8$ variables agroclimáticas y de mercado pueden resumirse en **$3$ índices ortogonales** ($>83\%$ de varianza explicada) que alimentan de forma limpia el *scoring* del Oráculo Agrícola.
* **MANOVA Bifactorial** confirmó ($p < 0.0001$ en Wilks, Pillai, Hotelling-Lawley y Roy) una interacción crítica entre `cultivo` y `central_abasto`: mientras el *Aguacate Hass* absorbe con holgura fletes nacionales largos por su alta densidad de valor por kilogramo, los cultivos de menor precio unitario (*Plátano Chiapas* y *Papaya Maradol*) sufren una fuerte compresión de margen relativo en rutas lejanas, validando de forma concluyente la regla de negocio de AgroPulse de **consolidar lotes locales de $400\text{ kg}$ hacia compradores ancla dentro de Colima**.
* Finalmente, nuestra auditoría [`docs/auditoria/auditoria-iso-E3.md`](auditoria/auditoria-iso-E3.md) confirmó una disponibilidad acumulada de **$99.91\%$**, cero vulnerabilidades en dependencias y compatibilidad binaria `LF` garantizada entre Windows y Linux.
