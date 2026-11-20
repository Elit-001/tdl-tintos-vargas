# Relatoría Técnica y de Negocio — Etapa E2 (Geoespacial, Diseño Factorial y Auditoría ISO)

* **Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etapa:** `E2 — Enriquecimiento Geoespacial, Diseño de Experimentos y Auditoría ISO`
* **Autores:** Carlos Daniel Tintos Beltrán (*Data Engineer*) y Oliver Vargas García (*Data Statistician & Quality Lead E2*)
* **Fecha:** 19 de noviembre de 2026

---

## 1. Integración Geoespacial y Optimización Logística del Modelo Brokerage

En la etapa E1 establecimos el motor predictivo de series de tiempo para anticipar los picos de precio mayorista; sin embargo, para que el modelo comercial de **Marketplace de Intermediación Inteligente (*Brokerage*)** sea rentable en la práctica dentro del estado de Colima, resultaba indispensable cuantificar el costo real de mover un lote consolidado de **$400\text{ kg}$** ($4$ pequeños productores $\times 100\text{ kg}$) desde su huerta de origen hasta la puerta del comprador ancla.

Para resolverlo en E2 implementamos dos módulos clave:
1. **Captura Geoespacial Ética ([`extractores/extractor_geoespacial.py`](../extractores/extractor_geoespacial.py)):** Integramos la API abierta Overpass de **OpenStreetMap** utilizando `ExtractorEtico` para georreferenciar los $4$ nodos agroproductores del estado (`Tecomán`, `Armería`, `Manzanillo` y `Coquimatlán`) y los $4$ compradores ancla (*buckets* de consumo: *Walmart Colima*, *Empacadora San José*, *Agroindustriales de Colima* y *Limones Prolim*), generando automáticamente su ficha [`nodos_geoespaciales_colima.csv.meta.json`](../data/bronce/nodos_geoespaciales_colima.csv.meta.json) con firma `SHA-256`.
2. **Reproyección Métrica UTM 13N con GeoPandas ([`pipeline/geoespacial.py`](../pipeline/geoespacial.py)):** Uno de los principales retos técnicos fue evitar el error clásico de medir distancias en grados decimales (`EPSG:4326`). Reproyectamos los nodos a **`EPSG:32613` (WGS 84 / UTM Zona 13N)** en metros, aplicamos el factor de sinuosidad vial de las carreteras de Colima ($1.24$) y modelamos la estructura de costo logístico ($\$220\text{ MXN}$ de maniobra fija por lote $+ \$18.50\text{ MXN/km}$). El resultado en [`data/oro/rutas_flete_colima.csv`](../data/oro/rutas_flete_colima.csv) reveló que la distancia vial media es de **$37.81\text{ km}$** con un costo de flete promedio de **$\$2.30\text{ MXN/kg}$**, mientras que la asignación óptima por nodo productor reduce el flete en rutas intrarregionales hasta **$\$0.56\text{--}\$0.62\text{ MXN/kg}$**.

---

## 2. Impacto del Diseño de Experimentos Factorial ($2^3$ y $2^{4-1}$) en la Regla de Negocio

En [`laboratorio/E2_diseno_experimentos.ipynb`](../laboratorio/E2_diseno_experimentos.ipynb) diseñamos y ejecutamos un estudio experimental riguroso sobre el **margen neto de intermediación (*spread* en $\text{MXN/kg}$)**:

1. **Hallazgos del Diseño Factorial Completo $2^3$ ($N = 32, R^2 = 98.54\%$):**
   * **El Volumen de Consolidación ($B$: $100\text{ kg}$ vs. $400\text{ kg}$) es el factor de mayor impacto positivo:** Incrementa el *spread* neto en **$+2.36\text{ MXN/kg}$** ($F = 1581.4, p < 0.0001$). Esto demuestra matemáticamente la tesis central de AgroPulse: un pequeño agricultor con $100\text{ kg}$ no puede absorber solo la maniobra fija ni acceder al contrato corporativo, pero al agrupar a $4$ productores en un pool de $400\text{ kg}$ mediante el botón **"Ofrecer producto"**, el margen del lote sube en **$+\$944\text{ MXN}$**.
   * **La Interacción $A \times B$ (`Distancia` $\times$ `Volumen`) es altamente significativa ($+0.68\text{ MXN/kg}, p < 0.0001$):** Demuestra que cuando el lote se consolida a $400\text{ kg}$, la penalización económica de recorrer rutas largas ($> 35\text{ km}$ hacia Colima capital o Villa de Álvarez) se amortigua sustancialmente.
   * **Validez de Supuestos:** Los residuos del modelo cumplieron normalidad (**Shapiro-Wilk** $W = 0.9704, p = 0.5095$) y homocedasticidad (**Levene** $F = 0.5535, p = 0.7854$).
2. **Hallazgos del Diseño Factorial Fraccionado $2^{4-1}$ de Resolución IV ($I = ABCD$, generador $D = ABC$):**
   * Al introducir el cuarto factor **$D$ (`Tipo de Comprador Ancla`: Empacadora Regional vs. Retail Corporativo Walmart)** con la mitad de corridas experimentales, la estructura de alias de Resolución IV permitió estimar los $4$ efectos principales limpios de confusión con interacciones de dos factores.
   * El factor $D$ aporta **$+0.96\text{ MXN/kg}$** ($p < 0.0001$) gracias a la prima comercial del $+6.5\%$ pagada por el canal retail cuando la distancia logística es moderada (como el corredor **Coquimatlán $\rightarrow$ Walmart Colima** a $21.6\text{ km}$, que genera un margen neto de **$\$4,784\text{ MXN}$ por lote de $400\text{ kg}$** de Aguacate Hass).

---

## 3. Linaje Criptográfico Total y Lecciones Aprendidas de la Auditoría ISO

Bajo la coordinación de Oliver Vargas García como *Quality Lead* en E2 ([`docs/auditoria/auditoria-iso-E2.md`](auditoria/auditoria-iso-E2.md)), auditamos el sistema frente a las normas **ISO/IEC 25010** (software) e **ISO/IEC 25012** (datos):

* **Trazabilidad de Punta a Punta (`Bronce -> Plata -> Oro`):** Implementamos en [`pipeline/geoespacial.py`](../pipeline/geoespacial.py) y [`pipeline/integracion.py`](../pipeline/integracion.py) la inyección automática de las $5$ columnas obligatorias de linaje (`linaje_id_registro`, `linaje_archivo_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_fuente`). Hoy cualquier fila de [`dataset_analitico.csv`](../data/oro/dataset_analitico.csv) o [`rutas_flete_colima.csv`](../data/oro/rutas_flete_colima.csv) puede auditarse criptográficamente contra el archivo `.meta.json` de la Capa Bronce.
* **Fiabilidad Operativa Acumulada:** Tras más de $301\text{ horas}$ de operación del pipeline automatizado, nuestra bitácora [`calidad/bitacora_captura.csv`](../calidad/bitacora_captura.csv) registra una disponibilidad real de **$99.87\%$** ($\text{MTBF} = 301.49\text{ hrs}$, $\text{MTTR} = 0.40\text{ hrs}$), superando ampliamente el umbral del $95\%$ requerido para la certificación del Sello TDL.

