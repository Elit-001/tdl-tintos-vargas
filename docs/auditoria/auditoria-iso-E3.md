# Reporte de Auditoría Formal de Calidad y Eficiencia — ISO/IEC 25010 e ISO/IEC 25012 (Entrega E3)

* **Observatorio Auditado:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etapa del Proyecto:** `E3 — Optimización Medida del Pipeline, Publicación Abierta (Datasheet) y Estadística Multivariada (PCA / MANOVA)`
* **Fecha de Auditoría:** 25 de noviembre de 2026
* **Alternancia del Rol de *Quality Lead* (IEEE 730):**
  * **Auditor Líder en E3 (*Quality Lead*):** **Carlos Daniel Tintos Beltrán** (*Data Engineer*) — Certifica las métricas de eficiencia ISO/IEC 25010, el paquete de publicación abierta `CC BY 4.0`, la disponibilidad operativa y la reproducibilidad estadística del notebook multivariado.
  * **Auditor de Par Técnico en E3:** **Oliver Vargas García** (*Data Statistician*) — Verifica la equivalencia numérica antes vs. después del pipeline vectorizado, el cumplimiento del *Datasheet* (Gebru et al.) y la ausencia total de PII en `data/publicado/`.

---

## 1. Evaluación de Calidad del Producto de Software — Norma ISO/IEC 25010 (Con Benchmark E3)

En la etapa **E3**, el foco central sobre **ISO/IEC 25010** recae en demostrar cuantitativamente la mejora en **Eficiencia de Desempeño** (tiempo de respuesta, utilización de memoria RAM y reducción de operaciones I/O y almacenamiento) sin degradar la **Fiabilidad**, **Seguridad** ni **Mantenibilidad** logradas en E1 y E2.

| Característica ISO/IEC 25010 | Subcaracterística Evaluada | Métrica / Indicador Objetivo | Meta SQA (E3) | Resultado Medido en E3 | Evidencia Reproducible | Dictamen |
| :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **1. Eficiencia de Desempeño** | Comportamiento temporal | Reducción medible del tiempo total del pipeline (`time.perf_counter`, media de $5$ corridas) | Mejora $> 15\%$ | **$1,952.67\text{ ms} \rightarrow 1,422.36\text{ ms}$ ($+27.16\%$ más rápido; Limpieza $+68.43\%$)** | [`pipeline/benchmark_e3.py`](../../pipeline/benchmark_e3.py), [`calidad/benchmark_e3.csv`](../../calidad/benchmark_e3.csv) | **CUMPLE** |
| **2. Eficiencia de Desempeño** | Utilización de recursos (RAM, I/O y Disco) | Pico de RAM (`tracemalloc`), lecturas de disco por corrida y compresión columnar Parquet | Mejora medible en los $3$ rubros | **RAM: $-5.67\%$ ($3,981.63\text{ KB}$); I/O: $-76.92\%$ ($13 \rightarrow 3$); Disco: $-81.67\%$ ($73.72\text{ KB}$)** | [`calidad/benchmark_e3.csv`](../../calidad/benchmark_e3.csv), [`dataset_analitico.parquet`](../../data/oro/dataset_analitico.parquet) | **CUMPLE** |
| **3. Adecuación Funcional** | Exactitud e integridad funcional | Equivalencia numérica al $100\%$ tras vectorización + generación del paquete abierto `data/publicado/` | $0$ discrepancias numéricas | **$100\%$ idéntico** (`assert_series_equal` aprobado) + $27$ cols curadas | [`pipeline/publicacion.py`](../../pipeline/publicacion.py), [`tests/test_pipeline_e3.py`](../../tests/test_pipeline_e3.py) | **CUMPLE** |
| **4. Compatibilidad** | Interoperabilidad multi-OS y multiformato | Archivos CSV con saltos puros `LF` (`\n`) + formato Apache Parquet + GeoJSON RFC 7946 | $0$ bytes `CRLF` en CSVs | **$0$ ocurrencias `\r\n`** verificadas en binario + lectura nativa PyArrow | [`.gitattributes`](../../.gitattributes), [`agropulse_colima_curado.parquet`](../../data/publicado/agropulse_colima_curado.parquet) | **CUMPLE** |
| **5. Fiabilidad** | Disponibilidad operativa acumulada | $A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$ sobre el historial real de [`bitacora_captura.csv`](../../calidad/bitacora_captura.csv) | $\ge 95.0\%$ | **$99.91\%$** ($28$ ejecuciones consecutivas `EXITOSO` registradas) | [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) | **CUMPLE** |
| **6. Seguridad** | Integridad criptográfica y dependencias limpias | $0$ secretos (`gitleaks`), $0$ CVEs (`pip-audit`) y linaje `SHA-256` intacto hasta `data/publicado/` | $0$ CVEs / $100\%$ SHA-256 | **$0$ vulnerabilidades (`pip-audit`), $0$ PII y $100\%$ match SHA-256** | [`requirements.txt`](../../requirements.txt), [`tests/test_pipeline_e3.py`](../../tests/test_pipeline_e3.py) | **CUMPLE** |
| **7. Mantenibilidad** | Modularidad, estilo y cobertura de pruebas | Funciones $\le 30$ líneas, `ruff check .` limpio y suite acumulada `pytest` E0–E3 en verde | $0$ warnings / $100\%$ tests | **$0$ errores `ruff` / $13/13$ pruebas unitarias aprobadas** | [`tests/test_pipeline_e3.py`](../../tests/test_pipeline_e3.py) | **CUMPLE** |
| **8. Usabilidad y Portabilidad** | Facilidad de reutilización por terceros | Documentación abierta con `LICENSE` (`CC BY 4.0`), `README.md` y *Datasheet* estandarizado | Paquete autoexplicativo completo | **Paquete completo en `data/publicado/` + [`docs/E3/datasheet.md`](../E3/datasheet.md)** | [`data/publicado/README.md`](../../data/publicado/README.md), [`data/publicado/LICENSE`](../../data/publicado/LICENSE) | **CUMPLE** |

### 1.1 Evidencia Cuantitativa del Benchmark Antes vs. Después (`calidad/benchmark_e3.csv`)

El script reproducible [`pipeline/benchmark_e3.py`](../../pipeline/benchmark_e3.py) ejecuta una corrida previa de calentamiento (*warm-up*) y promedia $5$ iteraciones completas en igualdad estricta de entradas y salidas:

| Métrica Evaluada | Unidad | Antes (Arquitectura E2) | Después (Optimizado E3) | Mejora Medida (%) | Técnica Aplicada |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `tiempo_puerta_calidad_ms` | `ms` | `450.80` | `444.31` | **`+1.44%`** | Caché en memoria de esquemas `DataFrameSchema` de Pandera |
| `tiempo_limpieza_plata_ms` | `ms` | `775.45` | `244.81` | **`+68.43%`** | Vectorización matricial NumPy en IQR/Min-Max y salto de interpolación sin nulos |
| `tiempo_geoespacial_utm_ms` | `ms` | `137.37` | `134.39` | **`+2.17%`** | Producto cartesiano `how="cross"` + `np.hypot` eliminando `.iterrows()` + caché SHA-256 |
| `tiempo_integracion_oro_ms` | `ms` | `589.05` | `598.85` | `-1.66%` | Incluye escritura adicional del archivo comprimido `.parquet` en Oro |
| **`tiempo_total_pipeline_ms`** | **`ms`** | **`1,952.67`** | **`1,422.36`** | **`+27.16%`** | Paso de DataFrames en memoria entre etapas sin relecturas CSV intermedias |
| **`pico_memoria_ram_kb`** | **`KB`** | **`4,220.80`** | **`3,981.63`** | **`+5.67%`** | Transformaciones en sitio (`en_sitio=True`) evitando copias duplicadas |
| **`lecturas_disco_por_corrida`** | `operaciones_io` | `13.00` | `3.00` | **`+76.92%`** | Lectura única de Bronce + caché `_CACHE_META_BRONCE` de hashes SHA-256 |
| **`almacenamiento_capa_oro_kb`** | `KB` | `402.21` (CSV) | `73.72` (Parquet) | **`+81.67%`** | Compresión columnar PyArrow con tipos compactos `category` y `float32` |

### 1.2 Actualización de Fiabilidad Operativa (MTBF, MTTR y Disponibilidad E3)
Desde el inicio de la bitácora [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) (`2026-11-07T00:53:54Z`) hasta el corte de auditoría E3 (`2026-11-25T21:30:00Z`, equivalente a **$452.60\text{ horas}$** de monitoreo continuo con **$28$ corridas automatizadas exitosas** en `api_open_meteo_clima`, `web_sniim_precios` y `api_osm_geoespacial`, manteniendo un único incidente histórico de red reparado en $0.40\text{ horas}$):

$$\text{MTBF} = \frac{452.60 - 0.40}{1} = 452.20\text{ horas}, \qquad \text{MTTR} = 0.40\text{ horas}, \qquad A = \frac{452.20}{452.20 + 0.40} = \mathbf{99.91\%}$$

---

## 2. Certificación de Calidad del Dataset Publicado — Norma ISO/IEC 25012 (`data/publicado/`)

Se auditó el paquete público [`data/publicado/agropulse_colima_curado.csv`](../../data/publicado/agropulse_colima_curado.csv) ($768\text{ filas} \times 27\text{ columnas}$, $305.98\text{ KB}$) y su contraparte columnar [`agropulse_colima_curado.parquet`](../../data/publicado/agropulse_colima_curado.parquet) ($44.81\text{ KB}$, **$85.35\%$ de ahorro en disco**):

| Dimensión ISO/IEC 25012 | Criterio Auditado sobre `agropulse_colima_curado` | Valor Verificado | Evidencia Automatizada | Dictamen |
| :--- | :--- | :---: | :--- | :---: |
| **Exactitud y Consistencia** | Igualdad exacta frente a Capa Oro tras optimizaciones matriciales | **$100.0\%$ exacto** | `pd.testing.assert_series_equal` en [`test_pipeline_e3.py`](../../tests/test_pipeline_e3.py) | **CUMPLE** |
| **Completitud** | Celdas vacías o `NaN` en las $27$ columnas ($20,736$ celdas totales) | **$0$ nulos ($100.0\%$)** | `assert int(df_pub.isna().sum().sum()) == 0` | **CUMPLE** |
| **Credibilidad y Trazabilidad** | Preservación del hash `SHA-256` en formato `LF` hasta `data/bronce/*.meta.json` | **$100.0\%$ verificable** | Validación criptográfica binaria en `test_pipeline_e3.py` | **CUMPLE** |
| **Confidencialidad y Conformidad** | Escaneo por expresiones regulares de correos/teléfonos, columnas PII y licencia abierta | **$0$ PII + Licencia `CC BY 4.0`** | [`data/publicado/LICENSE`](../../data/publicado/LICENSE), [`docs/E3/datasheet.md`](../E3/datasheet.md) | **CUMPLE** |
| **Portabilidad y Accesibilidad** | Saltos `LF` multiplataforma + formato abierto CSV/Parquet + guía de carga rápida | **$100\%$ interoperable** | [`data/publicado/README.md`](../../data/publicado/README.md) | **CUMPLE** |

---

## 3. Dictamen Final hacia la Obtención del Sello TDL

Habiendo verificado `0` infracciones en `ruff check .`, `13/13` pruebas aprobadas en `pytest tests/ -v`, `0` vulnerabilidades conocidas en `pip-audit`, disponibilidad operativa de **$99.91\%$**, reducción del **$27.16\%$** en tiempo total de procesamiento y publicación íntegra bajo licencia **CC BY 4.0** con su *Datasheet* oficial, el *Quality Lead* emite **DICTAMEN APROBATORIO DE CALIDAD CERTIFICADA (ETAPA E3)**, dejando al observatorio **AgroPulse TDL** listo para la evaluación final del **Sello TDL**.
