# Ficha Oficial de Entrega — Etapa E2 (Enriquecimiento Geoespacial, Diseño Factorial y Auditoría ISO)

* **Nombre del Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etiqueta de entrega (Git Tag):** `e2`
* **Fecha de entrega:** 19 de noviembre de 2026
* **Integrantes del Equipo y Alternancia de *Quality Lead*:**
  * **Carlos Daniel Tintos Beltrán** — *Data Engineer* (Extractor geoespacial OpenStreetMap, procesamiento GeoPandas `EPSG:32613`, linaje total SHA-256 en Capa Oro y mapa logístico en Streamlit)
  * **Oliver Vargas García** — *Data Statistician & Quality Lead (E2)* (Diseño de experimentos factorial $2^3$ y fraccionado $2^{4-1}$ en `E2_diseno_experimentos.ipynb`, Auditoría ISO/IEC 25010 e ISO/IEC 25012, Declaración de Ética y Relatoría E2)

---

## Resumen Ejecutivo (3 líneas)

En esta **Entrega E2**, **AgroPulse TDL** incorpora una tercera fuente geoespacial abierta de **OpenStreetMap (API Overpass)** para el estado de Colima ([`extractores/extractor_geoespacial.py`](../../extractores/extractor_geoespacial.py)), reproyecta coordenadas de `EPSG:4326` a `EPSG:32613` (UTM Zona 13N) con **GeoPandas** ([`pipeline/geoespacial.py`](../../pipeline/geoespacial.py)) para calcular distancias viales reales y costos de flete por lote consolidado de $400\text{ kg}$ hacia $4$ compradores ancla (*Walmart Colima, Empacadora San José, Agroindustriales de Colima y Limones Prolim*), e inyecta **trazabilidad y linaje criptográfico total (`SHA-256`)** en el $100\%$ de los registros de la Capa Oro. En el eje estadístico, ejecutamos el laboratorio reproducible [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) con un **Diseño Factorial Completo $2^3$** ($N=32$, $R^2 = 0.9854$) y un **Diseño Factorial Fraccionado $2^{4-1}$ de Resolución IV ($I = ABCD$, generador $D = ABC$)** validando normalidad (Shapiro-Wilk $p = 0.509$) y homocedasticidad (Levene $p = 0.785$). Finalmente, certificamos el sistema mediante el reporte formal [`docs/auditoria/auditoria-iso-E2.md`](../auditoria/auditoria-iso-E2.md) bajo **ISO/IEC 25010** e **ISO/IEC 25012** y la declaración [`docs/etica-datos.md`](../etica-datos.md).

---

## Evidencias por Materia y Criterios de la Rúbrica E2

### 1. Ingeniería de Datos — Mtro. Román (*GEOESPACIAL Y LINAJE TOTAL*)

| Criterio de Evaluación (Rúbrica E2) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Extractor geoespacial ético (OpenStreetMap) + `.meta.json` SHA-256** | Cumplido | [`extractor_geoespacial.py`](../../extractores/extractor_geoespacial.py), [`nodos_geoespaciales_colima.csv`](../../data/bronce/nodos_geoespaciales_colima.csv), [`nodos_geoespaciales_colima.csv.meta.json`](../../data/bronce/nodos_geoespaciales_colima.csv.meta.json) | Consume Overpass API con `ExtractorEtico`, respaldo local para $4$ productores y $4$ compradores ancla en Colima, bitácora y hash SHA-256 automático. |
| **Procesamiento GeoPandas (`EPSG:4326` $\rightarrow$ `EPSG:32613`) y fletes** | Cumplido | [`pipeline/geoespacial.py`](../../pipeline/geoespacial.py), [`rutas_flete_colima.csv`](../../data/oro/rutas_flete_colima.csv), [`rutas_flete_colima.geojson`](../../data/oro/rutas_flete_colima.geojson) | Reproyección métrica a UTM Zona 13N, cálculo de las $16$ rutas logísticas en km, flete por lote de $400\text{ kg}$ y selección de ruta óptima por margen neto. |
| **Linaje y trazabilidad total (`Bronce -> Plata -> Oro`)** | Cumplido | [`pipeline/integracion.py`](../../pipeline/integracion.py), [`dataset_analitico.csv`](../../data/oro/dataset_analitico.csv), [`rutas_flete_colima.csv`](../../data/oro/rutas_flete_colima.csv), [`diccionario_datos.md`](../../data/oro/diccionario_datos.md) | Inclusión sin nulos de las $5$ columnas `linaje_id_registro`, `linaje_archivo_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_fuente`. |
| **Visualización cartográfica en Tablero Público** | Cumplido | [`tablero/app.py`](../../tablero/app.py) | Mapa de red logística de Colima con nodos productores, compradores ancla, rutas óptimas en verde y matriz interactiva de costos y *spread*. |

#### Tabla de Trazabilidad Criptográfica Bronce $\rightarrow$ Oro (SHA-256 Verificado)
| Artefacto en Capa Oro (`data/oro/`) | Filas | Archivo Origen (`linaje_archivo_bronce`) | Firma `linaje_sha256_bronce` (Verificada contra `.meta.json`) | Completitud Linaje |
| :--- | :---: | :--- | :--- | :---: |
| [`dataset_analitico.csv`](../../data/oro/dataset_analitico.csv) | `768` | `precios_agro_historico_mensual.csv` (+ hash clima) | `558e2fa0b2fba4c2ee501273857c2f9b90aaa7d3a9d72a5804e13b3458c4db4b` | **$100.0\%$ ($0$ nulos)** |
| [`rutas_flete_colima.csv`](../../data/oro/rutas_flete_colima.csv) | `16` | `nodos_geoespaciales_colima.csv` | `d22df26a64995b4951c07a2adb9a7b96e264f2890e8bc14422803e32a9cf741d` | **$100.0\%$ ($0$ nulos)** |
| [`pronosticos_e1.csv`](../../data/oro/pronosticos_e1.csv) | `6` | `precios_agro_historico_mensual.csv` | `558e2fa0b2fba4c2ee501273857c2f9b90aaa7d3a9d72a5804e13b3458c4db4b` | **$100.0\%$ ($0$ nulos)** |

---

### 2. Análisis Estadístico para Ciencia de Datos — Mtro. Joel (*DISEÑO DE EXPERIMENTOS*)

| Criterio de Evaluación (Rúbrica E2) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Diseño Factorial Completo $2^3$ ($N=32$) y Tabla ANOVA** | Cumplido | [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) | Evalúa $A$ (Distancia), $B$ (Volumen $400\text{ kg}$) y $C$ (Estacionalidad) sobre el *spread* neto ($\text{MXN/kg}$); $R^2 = 0.9854$, efectos principales e interacciones $A \times B$ y $B \times C$ significativos ($p < 0.001$). |
| **Gráficas de efectos principales, interacción y supuestos ANOVA** | Cumplido | [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) | Gráficas embebidas en el notebook; residuos validados con **Shapiro-Wilk** ($W = 0.9704, p = 0.5095 > 0.05$) y **Levene** ($F = 0.5535, p = 0.7854 > 0.05$). |
| **Diseño Factorial Fraccionado $2^{4-1}$ (Resolución IV, $D = ABC$)** | Cumplido | [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) | Incorpora el factor $D$ (Comprador Ancla Retail vs. Empacadora) con relación definitoria $I = ABCD$, tabla completa de estructura de alias y recomendación operativa. |

---

### 3. Calidad en los Sistemas de Información — Mtra. Isis (*AUDITORÍA ISO Y ÉTICA*)

| Criterio de Evaluación (Rúbrica E2) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Auditoría formal ISO/IEC 25010 e ISO/IEC 25012** | Cumplido | [`docs/auditoria/auditoria-iso-E2.md`](../auditoria/auditoria-iso-E2.md) | Evaluación de las $8$ características ISO 25010 ($\text{MTBF} = 301.49\text{ hrs}$, $\text{MTTR} = 0.40\text{ hrs}$, $A = 99.87\%$) y las $7$ dimensiones ISO 25012 con rotación de *Quality Lead* a Oliver Vargas. |
| **Declaración de Ética, Legalidad y Mitigación de Sesgos** | Cumplido | [`docs/etica-datos.md`](../etica-datos.md) | Análisis legal de licencias (CC BY 4.0, Datos Abiertos MX, ODbL 1.0), verificación de `robots.txt`, cero PII y mitigación de sesgos de escala y cobertura rural. |
| **Pruebas unitarias E2 (linaje SHA-256 y GeoPandas) + Bitácoras PSP** | Cumplido | [`tests/test_pipeline_e2.py`](../../tests/test_pipeline_e2.py), [`tiempo-carlos.csv`](../../calidad/tiempo-carlos.csv), [`defectos-carlos.csv`](../../calidad/defectos-carlos.csv), [`tiempo-oliver.csv`](../../calidad/tiempo-oliver.csv), [`defectos-oliver.csv`](../../calidad/defectos-oliver.csv) | Suite `pytest` validando $0$ nulos en linaje, coincidencia exacta SHA-256 con `.meta.json` y distancias/fletes $> 0$, más registros PSP de E2. |
| **Relatoría técnica y de negocio E2** | Cumplido | [`docs/relatoria-E2.md`](../relatoria-E2.md) | Síntesis de decisiones geoespaciales, hallazgos del diseño factorial en el margen de intermediación y lecciones aprendidas de la auditoría ISO. |

---

## Comandos de Ejecución y Verificación Local (E2)

```bash
# 1. Ejecutar captura multifuente (Clima + Precios + Nodos Geoespaciales OSM con .meta.json SHA-256)
python -m extractores.ejecutar_captura

# 2. Ejecutar pipeline Medallion completo E1-E2 (Puerta de Calidad + Limpieza + GeoPandas UTM + Linaje Oro)
python -m pipeline.orquestador_e1

# 3. Validar linter, pruebas unitarias (E0 + E1 + E2) y seguridad de dependencias
ruff check .
pytest tests/ -v
pip-audit --skip-editable --progress-spinner off
```

