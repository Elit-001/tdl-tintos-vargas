# Datasheet for Dataset — `agropulse_colima_curado` (Entrega E3 / Actualización Estatal Auditada)

> **Estructura Estandarizada:** Elaborado conforme a la metodología internacional *Datasheets for Datasets* (Gebru et al., 2021 — *Communications of the ACM*) y alineado con la norma **ISO/IEC 25012** de Calidad de Datos del proyecto integrador **Trusted Data Lab (TDL)**.

---

## 1. Motivación

* **¿Con qué propósito se creó este conjunto de datos?**
  Se creó para habilitar decisiones basadas en evidencia cuantitativa dentro del sector agrocomercial de **los 10 municipios del estado de Colima, México**, específicamente para operar y auditar el motor de **Marketplace de Intermediación Inteligente (*Brokerage*)** del observatorio **AgroPulse TDL**. El dataset integra en una sola vista limpia las cotizaciones históricas y diarias oficiales del SNIIM (incluyendo la plaza de Colima), la variabilidad hidroclimática ERA5 de las zonas productoras y los costos logísticos por carretera real hacia compradores formales establecidos en Colima.
* **¿Quién creó el conjunto de datos y en nombre de qué entidad?**
  Fue diseñado, extraído, procesado y certificado por el equipo del proyecto integrador **Trusted Data Lab** del **Tecnológico Nacional de México (TecNM)**:
  * **Carlos Daniel Tintos Beltrán** — *Data Engineer & Quality Lead (E1 / E3)*
  * **Oliver Vargas García** — *Data Statistician & Quality Lead (E2)*
* **¿Quién financió la creación del conjunto de datos?**
  Proyecto académico autofinanciado en el marco de las asignaturas de *Ingeniería de Datos* (Mtro. Román), *Análisis Estadístico para Ciencia de Datos* (Mtro. Joel) y *Calidad en los Sistemas de Información* (Mtra. Isis). No existen conflictos de interés comerciales ni patrocinios privados.

---

## 2. Composición

* **¿Qué representan las instancias que componen el conjunto de datos?**
  Cada instancia (fila) representa un **corte mensual agrocomercial y agroclimático** para una combinación única de `periodo_mensual` $\times$ `cultivo` $\times$ `central_abasto`, vinculada a su región agroproductora representativa en Colima (`zona_agricola`) y a su ruta carretera óptima de comercialización B2B local (`comprador_ancla_optimo_colima`).
* **¿Cuántas instancias contiene en total?**
  Contiene exactamente **$960$ instancias consolidadas** (`48` periodos mensuales continuos entre `2022-11` y `2026-10` $\times$ `4` cultivos estratégicos de Colima $\times$ `5` mercados mayoristas oficiales del SNIIM), complementadas en el almacén con cobertura climática y logística sobre los **10 municipios de Colima** y **60 rutas carreteras reales** (`10 municipios × 6 compradores`).
* **¿Qué atributos contiene cada instancia?**
  Cada fila consta de **$27$ columnas curadas** agrupadas en $5$ dominios:
  1. **Identificación espacio-temporal y taxonómica ($5$ cols):** `periodo_mensual`, `cultivo` (*Limón Mexicano, Papaya Maradol, Plátano Chiapas, Aguacate Hass*), `variedad_sniim`, `zona_agricola` (*Tecomán, Armería, Manzanillo, Comala*) y `central_abasto` (*Colima, Guadalajara, Morelia, CDMX-Iztapalapa, Monterrey*).
  2. **Indicadores económicos y discretización ($7$ cols):** `precio_mayorista_mxn_kg`, `volatilidad_mensual_pct` (coeficiente de variación mensual real `CV%`), `costo_logistico_mxn_kg`, `margen_comercial_mxn_kg`, `margen_comercial_pct`, `categoria_precio` (`Bajo/Medio/Alto`) y `nivel_volatilidad` (`Estable/Moderada/Alta`).
  3. **Variables hidroclimáticas mensuales ($5$ cols):** `temperatura_max_c`, `temperatura_media_c`, `precipitacion_acumulada_mm`, `evapotranspiracion_mm` (FAO ET0) y `humedad_relativa_pct`.
  4. **Optimización geoespacial local B2B en Colima ($4$ cols):** `comprador_ancla_optimo_colima` (*entre los 6 comercios y mercados reales verificados en OpenStreetMap: Mercado Constitución Colima, Walmart Colima, Soriana Híper Villa de Álvarez, Bodega Aurrera Tecomán, Mi Bodega Aurrera Armería y Soriana Híper Manzanillo*), `distancia_vial_optima_km`, `flete_local_400kg_mxn_kg` y `spread_brokerage_colima_mxn_kg`.
  5. **Trazabilidad y linaje criptográfico (`SHA-256`, $6$ cols):** `linaje_sha256_clima_bronce`, `linaje_id_registro`, `linaje_archivo_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_fuente`.
* **¿Falta información en instancias individuales (`valores nulos`)?**
  **No ($0.0\%$ de valores nulos; completitud verificada del $100.0\%$).** Cualquier mes sin reporte diario puntual se diagnostica e imputa condicionalmente en Capa Plata.
* **¿Existen errores conocidos, fuentes de ruido o redundancias?**
  * Los precios reflejan cotizaciones frecuentes mayoristas oficiales del SNIIM y no incluyen descuentos informales a pie de huerta (*coyotaje*).
  * Las distancias viales locales provienen de la red carretera real de OpenStreetMap vía **OSRM Driving Table API** (`router.project-osrm.org`), con respaldo métrico `EPSG:32613` (UTM Zona 13N).
* **¿Contiene datos confidenciales o Datos Personales Identificables (PII)?**
  **Rotundamente NO ($0\%$ PII).** No existen nombres de personas físicas, teléfonos, correos personales, RFC, CURP ni coordenadas de parcelas privadas. Todas las ubicaciones corresponden a cabeceras de los 10 municipios de Colima y sucursales comerciales públicas verificadas en OpenStreetMap.

---

## 3. Proceso de Recolección

* **¿Cómo se adquirieron los datos de cada fuente?**
  Mediante extracción automatizada, programática y ética implementada en Python ([`extractores/`](../../extractores)):
  1. **Clima (`Open-Meteo Archive & Forecast API`):** Peticiones HTTP REST JSON sobre reanálisis climático ERA5/NOAA para los **10 municipios de Colima**.
  2. **Precios Mayoristas (`SNIIM — Secretaría de Economía`):** Extracción ética mediante `ExtractorEtico` ([`extractores/base.py`](../../extractores/base.py)) consultando `ResultadosConsultaFechaFrutasYHortalizas.aspx` por **ventanas anuales (`2022–2026`)** para evitar el truncamiento de 1,000 filas por tabla HTML en `DestinoId` `80` (*Colima*), `140` (*Guadalajara*), `160` (*Morelia*), `100` (*CDMX-Iztapalapa*) y `190` (*Monterrey*).
  3. **Red Geoespacial y Carretera (`OpenStreetMap Overpass + Nominatim + OSRM`):** Consulta acotada al estado de Colima (`18.80,-104.45,19.45,-103.50`) para los 10 municipios y 6 compradores reales, más matriz de ruteo vehicular OSRM.
* **¿Cuál es el marco temporal y frecuencia de captura?**
  Ventana histórica mensual de $48$ meses (`noviembre 2022 – octubre 2026`) más boletines diarios vigentes, actualizada diariamente vía GitHub Actions (`cron: "0 8 * * *"` UTC) y auditada en [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv).
* **¿Se realizó revisión ética y legal?**
  Sí. El análisis completo de términos de servicio, cumplimiento de `robots.txt`, licencias abiertas y mitigación de sesgos está documentado en [`docs/etica-datos.md`](../etica-datos.md).

---

## 4. Preprocesamiento, Limpieza y Etiquetado

* **¿Qué transformaciones se aplicaron desde los datos crudos hasta el dataset publicado?**
  El procesamiento sigue estrictamente la arquitectura **Medallion (`Bronce -> Plata -> Oro -> Publicado`)**:
  1. **Sellado Criptográfico en Bronce:** Normalización a `LF` (`\n`) y generación de `<archivo>.meta.json` con hash `SHA-256` y `timestamp_captura` UTC.
  2. **Puerta de Calidad (`pipeline/puerta_calidad.py`):** Contratos `pandera` cacheados en memoria ($0\%$ borrado silencioso hacia `data/cuarentena/`).
  3. **Limpieza Vectorizada (`pipeline/limpieza.py`):** Diagnóstico MCAR/MAR, *winsorización* matricial de valores extremos por criterio de Tukey ($1.5 \times \text{IQR}$ por grupo), escalado Min-Max y discretización interpretable.
  4. **Cálculo Geoespacial y Motor de Brokerage (`pipeline/geoespacial.py` y `pipeline/motor_brokerage.py`):** Reproyección `EPSG:4326` $\rightarrow$ `EPSG:32613`, matriz vial OSRM de 60 rutas y liquidación dinámica multi-productor de kilaje libre.
  5. **Curación y Exportación Dual (`pipeline/publicacion.py`):** Selección de las $27$ variables analíticas, preservación del linaje `SHA-256` y escritura simultánea en CSV UTF-8 (`LF`) y Apache Parquet optimizado (`category` / `float32`).
* **¿Están disponibles los datos crudos originales?**
  Sí, todos los datos crudos junto con sus fichas `.meta.json` residen públicamente en [`data/bronce/`](../../data/bronce).

---

## 5. Casos de Uso (Recomendados y NO Recomendados)

* **Usos Recomendados:**
  * Modelado estadístico reproducible: pronósticos de series de tiempo (ARIMA, Holt-Winters), diseño de experimentos logísticos y análisis multivariado (PCA, MANOVA).
  * Planeación de acopio colectivo multi-productor (aportes libres en kilos o rejas de $20\text{ kg}$) para cooperativas agrícolas y pequeños productores de los 10 municipios de Colima mediante [`tablero/vistas_productor.py`](../../tablero/vistas_productor.py).
  * Prácticas docentes de Ingeniería de Datos, trazabilidad criptográfica y auditoría de calidad ISO/IEC 25012.
* **Usos NO Recomendados (Restricciones Éticas y Operativas):**
  * **No usar para otorgamiento o rechazo automatizado de créditos agrícolas individuales** ni fijación punitiva de seguros sin inspección agronómica presencial de parcela.
  * **No usar para especulación acaparadora** en perjuicio de pequeños productores rurales.
  * **No extrapolar directamente a otros estados o países** sin recalibrar los nodos UTM y tarifas locales de transporte.

---

## 6. Distribución y Mantenimiento

* **¿Cómo y dónde se distribuye el conjunto de datos?**
  Se distribuye gratuitamente en [`data/publicado/`](../../data/publicado) del repositorio oficial de GitHub (`https://github.com/Elit-001/tdl-tintos-vargas`) en dos formatos interoperables:
  * [`agropulse_colima_curado.csv`](../../data/publicado/agropulse_colima_curado.csv) (`960` filas $\times$ `27` columnas en UTF-8 con terminador `LF`).
  * [`agropulse_colima_curado.parquet`](../../data/publicado/agropulse_colima_curado.parquet) (formato columnar comprimido).
* **¿Bajo qué licencia se publica?**
  Bajo licencia abierta **Creative Commons Attribution 4.0 International (`CC BY 4.0`)** en [`data/publicado/LICENSE`](../../data/publicado/LICENSE).
* **¿Quién mantiene el dataset y cuál es la política de versionado y actualización?**
  * **Responsables de mantenimiento:** Equipo AgroPulse TDL (`carlos.tintos@tecnm.mx`).
  * **Versionado inmutable:** Mediante etiquetas de Git auditadas por entrega (`e0`, `e1`, `e2`, `e3`) y verificación automática `SHA-256` en Integración Continua (`pytest` + GitHub Actions).
  * **Actualización:** Sincronización diaria automatizada mediante `.github/workflows/captura_diaria.yml` (incluyendo regeneración sincronizada de `data/publicado/`).
