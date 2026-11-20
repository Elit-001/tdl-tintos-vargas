# Reporte de Auditoría Formal de Calidad — ISO/IEC 25010 e ISO/IEC 25012 (Entrega E2)

* **Observatorio Auditado:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etapa del Proyecto:** `E2 — Enriquecimiento Geoespacial, Diseño Factorial y Auditoría ISO`
* **Fecha de Auditoría:** 19 de noviembre de 2026
* **Alternancia del Rol de *Quality Lead* (IEEE 730):**
  * **Auditor Líder en E2 (*Quality Lead*):** **Oliver Vargas García** (*Data Statistician*) — Audita el pipeline geoespacial, linaje SHA-256, suite `pytest` y seguridad CI/CD desarrollados por Ingeniería de Datos.
  * **Auditor de Par Técnico en E2:** **Carlos Daniel Tintos Beltrán** (*Data Engineer*) — Verifica la reproducibilidad del notebook [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) y los supuestos estadísticos del ANOVA.

---

## 1. Evaluación de Calidad del Producto de Software — Norma ISO/IEC 25010

La norma **ISO/IEC 25010** evalúa la calidad interna y externa del software a través de $8$ características fundamentales. A continuación se presenta la matriz de evaluación cuantitativa sobre el código fuente de AgroPulse TDL (`extractores/`, `pipeline/`, `tablero/` y `tests/`).

| Característica ISO/IEC 25010 | Subcaracterística Evaluada | Métrica / Indicador Objetivo | Meta SQA | Valor Medido (E2) | Evidencia Reproducible en el Repositorio | Dictamen |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **1. Adecuación Funcional** | Completitud e idoneidad funcional | Cobertura de extractores multifuente ($3$ fuentes) + reproyección UTM `EPSG:32613` + linaje SHA-256 | $100\%$ | **$100\%$ ($3/3$ fuentes y $5/5$ cols. linaje)** | [`extractor_geoespacial.py`](../../extractores/extractor_geoespacial.py), [`pipeline/geoespacial.py`](../../pipeline/geoespacial.py), [`pipeline/integracion.py`](../../pipeline/integracion.py) | **CUMPLE** |
| **2. Eficiencia de Desempeño** | Comportamiento temporal | Tiempo total de ejecución del pipeline Medallion (`Bronce -> Plata -> Oro`) | $< 30.0\text{ s}$ | **$4.82\text{ s}$** (extractores: $11.4\text{ s}$ promedio) | [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv), [`pipeline/orquestador_e1.py`](../../pipeline/orquestador_e1.py) | **CUMPLE** |
| **3. Compatibilidad** | Interoperabilidad | Exportación estándar CSV UTF-8 + GeoJSON RFC 7946 (`EPSG:4326` / `EPSG:32613`) | $100\%$ | **$100\%$ compatible** | [`rutas_flete_colima.csv`](../../data/oro/rutas_flete_colima.csv), [`rutas_flete_colima.geojson`](../../data/oro/rutas_flete_colima.geojson) | **CUMPLE** |
| **4. Usabilidad** | Inteligibilidad y operabilidad | Tablero público con pronóstico IC $95\%$, botón *"Ofrecer producto"* y mapa de rutas óptimas | $\ge 3$ módulos visuales claros | **$3$ módulos interactivos** | [`tablero/app.py`](../../tablero/app.py) | **CUMPLE** |
| **5. Fiabilidad** | Disponibilidad, madurez y tolerancia a fallos | Disponibilidad operativa $A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$ | $\ge 95.0\%$ | **$99.85\%$** ($17/17$ corridas exitosas en bitácora) | [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) | **CUMPLE** |
| **6. Seguridad** | Confidencialidad, integridad y trazabilidad | $0$ secretos expuestos (`gitleaks`), $0$ CVEs (`pip-audit`) y verificación criptográfica SHA-256 | $0$ vulnerabilidades / $100\%$ SHA-256 | **$0$ secretos, $0$ CVEs, $5/5$ `.meta.json` SHA-256** | [`ci_cd.yml`](../../.github/workflows/ci_cd.yml), [`data/bronce/*.meta.json`](../../data/bronce/nodos_geoespaciales_colima.csv.meta.json) | **CUMPLE** |
| **7. Mantenibilidad** | Modularidad, analizabilidad y capacidad de prueba | Funciones $\le 30$ líneas, $0$ errores de `ruff check .` y $100\%$ tests en verde (`pytest`) | $0$ errores linter / $100\%$ tests | **$0$ warnings `ruff` / $10/10$ tests `pytest` en verde** | [`tests/test_extractores.py`](../../tests/test_extractores.py), [`tests/test_pipeline_e1.py`](../../tests/test_pipeline_e1.py), [`tests/test_pipeline_e2.py`](../../tests/test_pipeline_e2.py) | **CUMPLE** |
| **8. Portabilidad** | Adaptabilidad e instalabilidad | Ejecución reproducible en Linux (`ubuntu-latest` GitHub Actions) y Windows local | $100\%$ | **$100\%$ multi-OS** | [`captura_diaria.yml`](../../.github/workflows/captura_diaria.yml), [`requirements.txt`](../../requirements.txt) | **CUMPLE** |

### 1.1 Cálculo Auditado de Fiabilidad (MTBF, MTTR y Disponibilidad en E2)
A partir de los registros acumulados en [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) entre el `2026-11-07T00:53:54Z` y el `2026-11-19T14:47:25Z` ($301.89\text{ horas}$ de operación continua supervisada con $17$ ejecuciones registradas en `EXITOSO` tras la activación de los mecanismos de respaldo resiliente y $1$ incidente transitorio de red en etapa de pruebas resuelto en $24\text{ min} = 0.40\text{ hrs}$):

$$\text{MTBF} = \frac{T_{\text{operación}} - T_{\text{reparación}}}{N_{\text{fallos}}} = \frac{301.89 - 0.40}{1} = 301.49\text{ horas}$$

$$\text{MTTR} = \frac{0.40\text{ horas}}{1} = 0.40\text{ horas (24 minutos)}$$

$$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} = \frac{301.49}{301.49 + 0.40} = 0.99867 \implies \mathbf{99.87\%} \quad (\ge 95.0\% \text{ exigido por la rúbrica})$$

---

## 2. Evaluación de Calidad de Datos en Capa Oro — Norma ISO/IEC 25012

La auditoría bajo **ISO/IEC 25012** se ejecutó directamente sobre los artefactos productivos de la Capa Oro: [`data/oro/dataset_analitico.csv`](../../data/oro/dataset_analitico.csv) ($768\text{ filas} \times 41\text{ columnas}$), [`data/oro/rutas_flete_colima.csv`](../../data/oro/rutas_flete_colima.csv) ($16\text{ rutas} \times 25\text{ columnas}$) y [`data/oro/pronosticos_e1.csv`](../../data/oro/pronosticos_e1.csv).

| Dimensión ISO/IEC 25012 | Definición Aplicada al Observatorio | Regla de Validación Automatizada | Meta | Resultado Auditado en Capa Oro | Dictamen |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **1. Exactitud (*Accuracy*)** | Cercanía de los valores a la realidad física, económica y geográfica de Colima | Validación `pandera` de rangos climáticos, precios $> 0$ y coordenadas dentro del *bounding box* de Colima (`lat` $\in [18.7, 19.5]$, `lon` $\in [-104.6, -103.4]$) | $100\%$ en Oro | **$100.0\%$** ($0$ registros fuera de rango en Oro) | **CUMPLE** |
| **2. Completitud (*Completeness*)** | Proporción de celdas no nulas en atributos analíticos y de linaje | `1 - df.isna().mean().mean()` y $0$ nulos en las $5$ columnas `linaje_*` | $\ge 98.0\%$ ($100\%$ en linaje) | **$100.0\%$ en `dataset_analitico.csv` y $100.0\%$ en `rutas_flete_colima.csv`** | **CUMPLE** |
| **3. Consistencia (*Consistency*)** | Coherencia referencial y geométrica sin contradicciones entre capas | Conservación estricta `Bronce == Plata + Cuarentena` y distancias UTM `EPSG:32613` $> 0\text{ km}$ | $100\%$ | **$100.0\%$** ($768 + 0 = 768$; $144 + 0 = 144$; $8 + 0 = 8$) | **CUMPLE** |
| **4. Credibilidad (*Credibility*)** | Veracidad y autenticidad de las fuentes de origen | Verificación criptográfica **SHA-256** entre `linaje_sha256_bronce` en Oro y `data/bronce/*.meta.json` | $100\%$ coincidencia | **$100.0\%$ coincidencia exacta** en los $3$ datasets de Oro | **CUMPLE** |
| **5. Actualidad (*Currentness*)** | Vigencia temporal de los datos para decisiones de *brokerage* | Ventana histórica de $48$ meses + captura diaria automatizada por cron (`0 8 * * *` UTC) | $\ge 36$ periodos + cron activo | **$48$ periodos mensuales + timestamp UTC en `.meta.json`** | **CUMPLE** |
| **6. Trazabilidad (*Traceability*)** | Capacidad de rastrear cada fila de Oro hasta su archivo crudo en Bronce | Presencia obligatoria de `linaje_id_registro`, `linaje_archivo_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_fuente` | $5/5$ columnas sin nulos | **$5/5$ columnas presentes y pobladas al $100\%$** | **CUMPLE** |
| **7. Conformidad (*Compliance*)** | Apego a estándares legales, éticos y de privacidad | Cumplimiento de `robots.txt`, licencias abiertas y $0$ Datos Personales (PII) | $0$ registros con PII | **$0$ datos personales** (verificado en [`docs/etica-datos.md`](../etica-datos.md)) | **CUMPLE** |

---

## 3. Hallazgos Detectados Durante la Auditoría E2 y Acciones Correctivas (PSP)

Durante la inspección cruzada liderada por Oliver Vargas García (*Quality Lead E2*), se identificaron y corrigieron $3$ hallazgos técnicos antes de certificar la entrega:

1. **Hallazgo H-E2-01 (Exactitud Geoespacial — Defecto #9 en [`calidad/defectos-carlos.csv`](../../calidad/defectos-carlos.csv)):**
   * *Descripción:* El prototipo inicial calculaba distancias euclidianas directamente sobre coordenadas geográficas (`EPSG:4326` en grados decimales), distorsionando la escala longitudinal en la costa de Colima.
   * *Acción Correctiva:* Se implementó `reproyectar_nodos_utm()` en [`pipeline/geoespacial.py`](../../pipeline/geoespacial.py) para transformar los puntos a **`EPSG:32613` (WGS 84 / UTM Zona 13N)** en metros antes de invocar `.distance()`, aplicando además el factor de sinuosidad carretera ($1.24$).
2. **Hallazgo H-E2-02 (Sincronización de Hash de Linaje — Defecto #10 y #11 en [`calidad/defectos-carlos.csv`](../../calidad/defectos-carlos.csv)):**
   * *Descripción:* El archivo auxiliar `data/oro/pronosticos_e1.csv` no incluía las $5$ columnas de linaje y existía riesgo de desfase si un CSV de Bronce se actualizaba sin refrescar su `.meta.json`.
   * *Acción Correctiva:* Se crearon las funciones `obtener_metadatos_linaje_bronce()` y `actualizar_linaje_pronosticos()` para garantizar que el $100\%$ de los archivos en `data/oro/` coincidan byte a byte con el hash SHA-256 de `data/bronce/*.meta.json`.
3. **Hallazgo H-E2-03 (Resolución del Diseño Fraccionado — Defecto #10 en [`calidad/defectos-oliver.csv`](../../calidad/defectos-oliver.csv)):**
   * *Descripción:* El borrador inicial del experimento fraccionado usaba un generador de Resolución III, confundiendo efectos principales con interacciones de dos factores.
   * *Acción Correctiva:* Se elevó el diseño en [`laboratorio/E2_diseno_experimentos.ipynb`](../../laboratorio/E2_diseno_experimentos.ipynb) a un diseño **$2^{4-1}$ de Resolución IV ($I = ABCD$, generador $D = ABC$)** y se añadieron las pruebas formales de Shapiro-Wilk y Levene.

---

## 4. Dictamen Final de Auditoría SQA (Etapa E2)

Con base en la evidencia verificable de las pruebas automatizadas (`pytest tests/ -v`: $100\%$ aprobadas), revisión estática (`ruff check .`: $0$ infracciones), auditoría de dependencias (`pip-audit`: $0$ vulnerabilidades) y validación criptográfica de linaje SHA-256, se emite un **DICTAMEN FAVORABLE DE CONFORMIDAD TOTAL** bajo las normas **ISO/IEC 25010** e **ISO/IEC 25012** para la Entrega E2 de **AgroPulse TDL**.

