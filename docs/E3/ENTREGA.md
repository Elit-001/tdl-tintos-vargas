# Ficha Oficial de Entrega — Etapa E3 (Optimización Medida, Publicación Abierta y Análisis Multivariado)

* **Nombre del Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etiqueta de entrega (Git Tag):** `e3`
* **Fecha de entrega:** 25 de noviembre de 2026
* **Integrantes del Equipo y Alternancia de *Quality Lead*:**
  * **Carlos Daniel Tintos Beltrán** — *Data Engineer & Quality Lead (E3)* (Optimización vectorizada del pipeline Medallion, benchmark reproducible `benchmark_e3.py`, publicación abierta `CC BY 4.0`, *Datasheet* Gebru et al. y auditoría ISO E3)
  * **Oliver Vargas García** — *Data Statistician* (Análisis Multivariado **PCA + MANOVA** en `laboratorio/E3_multivariado_pca_manova.ipynb`, validación de supuestos de Bartlett, relatoría técnica E3 y revisión par SQA)

---

## Resumen Ejecutivo (3 líneas)

En esta **Entrega E3**, **AgroPulse TDL** optimiza formalmente su pipeline Medallion eliminando bucles fila por fila (`.iterrows()`), vectorizando las operaciones IQR y Min-Max en NumPy, cacheando hashes `SHA-256` en memoria y suprimiendo relecturas intermedias de disco, logrando una **reducción del $27.16\%$ en el tiempo total de ejecución** ($1,952.67\text{ ms} \rightarrow 1,422.36\text{ ms}$; **$-68.43\%$ en limpieza**), **$-76.92\%$ en operaciones I/O de disco** ($13 \rightarrow 3$) y **$-81.67\%$ en almacenamiento** mediante Apache Parquet ([`calidad/benchmark_e3.csv`](../../calidad/benchmark_e3.csv)). Asimismo, liberamos para consumo externo el dataset curado [`data/publicado/agropulse_colima_curado.csv`](../../data/publicado/agropulse_colima_curado.csv) y `.parquet` bajo licencia abierta **CC BY 4.0** acompañado de su ficha estandarizada [`docs/E3/datasheet.md`](datasheet.md) (*Datasheets for Datasets*). En el eje analítico y de calidad, ejecutamos el estudio multivariado **PCA + MANOVA** ([`laboratorio/E3_multivariado_pca_manova.ipynb`](../../laboratorio/E3_multivariado_pca_manova.ipynb)) y certificamos el sistema en [`docs/auditoria/auditoria-iso-E3.md`](../auditoria/auditoria-iso-E3.md) con disponibilidad del **$99.91\%$** y $13/13$ pruebas unitarias en verde.

---

## 1. Ingeniería de Datos — Optimización Medida y Publicación Abierta (Mtro. Román)

### 1.1 Comparativa Cuantitativa Antes vs. Después ([`calidad/benchmark_e3.csv`](../../calidad/benchmark_e3.csv))

| Etapa / Indicador Técnico | Unidad | Antes (E2) | Después (E3) | Mejora (%) | Optimización Implementada |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Puerta de Calidad (`puerta_calidad.py`)** | `ms` | `450.80` | `444.31` | **`+1.44%`** | Caché en memoria de contratos `DataFrameSchema` de Pandera |
| **Limpieza en Plata (`limpieza.py`)** | `ms` | `775.45` | `244.81` | **`+68.43%`** | Vectorización matricial NumPy (Tukey IQR y Min-Max) y *fast-path* sin nulos |
| **Geoespacial UTM 13N (`geoespacial.py`)** | `ms` | `137.37` | `134.39` | **`+2.17%`** | Producto cartesiano `how="cross"` + `np.hypot` + `shapely.linestrings` sin `.iterrows()` |
| **Integración + Parquet (`integracion.py`)** | `ms` | `589.05` | `598.85` | `-1.66%` | Agrega exportación columnar comprimida `dataset_analitico.parquet` |
| **Tiempo Total del Pipeline** | `ms` | `1,952.67` | `1,422.36` | **`+27.16%`** | Flujo continuo en memoria en [`orquestador_e1.py`](../../pipeline/orquestador_e1.py) |
| **Pico de Consumo RAM (`tracemalloc`)** | `KB` | `4,220.80` | `3,981.63` | **`+5.67%`** | Operaciones `en_sitio=True` eliminando copias redundantes de DataFrames |
| **Lecturas de Disco por Corrida** | `I/O` | `13.00` | `3.00` | **`+76.92%`** | Caché `_CACHE_META_BRONCE` de `.meta.json` SHA-256 y paso directo en RAM |
| **Almacenamiento Capa Oro** | `KB` | `402.21` | `73.72` | **`+81.67%`** | Tipos `category` y `float32` en Parquet frente a CSV texto plano |

### 1.2 Paquete de Datos Abiertos Publicado para Terceros ([`data/publicado/`](../../data/publicado))
* **Dataset CSV (LF multiplataforma):** [`data/publicado/agropulse_colima_curado.csv`](../../data/publicado/agropulse_colima_curado.csv) (`768` filas × `27` columnas, `305.98 KB`, `0%` nulos, `0%` PII, linaje `SHA-256` verificable hasta Bronce).
* **Dataset Parquet Optimizado:** [`data/publicado/agropulse_colima_curado.parquet`](../../data/publicado/agropulse_colima_curado.parquet) (`44.81 KB`, ahorro del `85.35%`).
* **Licencia Abierta y Guía:** [`data/publicado/LICENSE`](../../data/publicado/LICENSE) (**Creative Commons Attribution 4.0 International — `CC BY 4.0`**) y [`data/publicado/README.md`](../../data/publicado/README.md).
* **Datasheet Oficial (Gebru et al.):** [`docs/E3/datasheet.md`](datasheet.md) y actualización de [`data/oro/diccionario_datos.md`](../../data/oro/diccionario_datos.md).

---

## 2. Análisis Estadístico — Estadística Multivariada PCA + MANOVA (Mtro. Joel)

Evidencia completa ejecutada con tablas y gráficas embebidas en [`laboratorio/E3_multivariado_pca_manova.ipynb`](../../laboratorio/E3_multivariado_pca_manova.ipynb):

1. **Adecuación Muestral (Prueba de Esfericidad de Bartlett):** $\chi^2 = 3,591.20$ ($gl = 28, p < 0.0001$, $|\mathbf{R}| = 9.06 \times 10^{-3}$), confirmando estructura correlacional significativa entre las $8$ variables agrocomerciales e hidroclimáticas.
2. **Análisis de Componentes Principales (PCA con Criterio de Kaiser $\lambda > 1$):**
   * Los **primeros $3$ Componentes Principales** superan $\lambda > 1.0$ y sintetizan más del **$83\%$ de la varianza total** en tres ejes ortogonales accionables: **PC1** (*Densidad de Valor y Margen Agrocomercial*), **PC2** (*Régimen Hidroclimático Estacional de Colima*) y **PC3** (*Fricción Logística y Volatilidad de Mercado*).
   * Incluye *Scree Plot* con curva de varianza acumulada, matriz de cargas factoriales y *Biplot* multivariado coloreado por cultivo.
3. **MANOVA Bifactorial (`cultivo`, `central_abasto` e interacción `cultivo:central_abasto`):**
   * Los cuatro contrastes multivariados (**Lambda de Wilks, Traza de Pillai, Hotelling-Lawley y Raíz Mayor de Roy**) resultaron altamente significativos (**$p < 0.0001$**) tanto en los efectos principales como en la interacción, demostrando que la estrategia óptima de ruteo depende conjuntamente de la densidad de valor del cultivo y la distancia al mercado: *Aguacate Hass* soporta fletes largos nacionales con márgenes $>36\%$, mientras que *Papaya Maradol* y *Plátano Chiapas* maximizan su rentabilidad consolidando **pools locales de $400\text{ kg}$** hacia compradores ancla en Colima.

---

## 3. Calidad en los Sistemas de Información — Auditoría ISO E3 y PSP (Mtra. Isis)

| Criterio de Evaluación (Rúbrica E3) | Estado | Evidencia Directa en el Repositorio | Resultado Verificado |
| :--- | :---: | :--- | :--- |
| **Auditoría ISO/IEC 25010 (Eficiencia) e ISO/IEC 25012 (Dataset Publicado)** | Cumplido | [`docs/auditoria/auditoria-iso-E3.md`](../auditoria/auditoria-iso-E3.md) | Rotación de *Quality Lead* a Carlos Tintos; $\text{MTBF}=452.20\text{ hrs}$, $\text{MTTR}=0.40\text{ hrs}$, Disponibilidad **$A = 99.91\%$**. |
| **Suite de Pruebas Unitarias E3 + Seguridad DevSecOps** | Cumplido | [`tests/test_pipeline_e3.py`](../../tests/test_pipeline_e3.py), [`requirements.txt`](../../requirements.txt) | `13 passed` en `pytest`, `0` errores en `ruff check .` y `0` CVEs en `pip-audit`. |
| **Bitácoras PSP Actualizadas (Etapa E3) + Relatoría E3** | Cumplido | [`tiempo-carlos.csv`](../../calidad/tiempo-carlos.csv), [`defectos-carlos.csv`](../../calidad/defectos-carlos.csv), [`tiempo-oliver.csv`](../../calidad/tiempo-oliver.csv), [`defectos-oliver.csv`](../../calidad/defectos-oliver.csv), [`docs/relatoria-E3.md`](../relatoria-E3.md) | Registro completo de tiempos y defectos introducidos/eliminados en E3 para ambos integrantes. |

---

## Checklist y Comandos de Verificación Reproducible (E3)

- [x] Benchmark cuantitativo antes vs. después ejecutado y persistido en `calidad/benchmark_e3.csv` (`LF`).
- [x] Dataset curado publicado en `data/publicado/` con licencia `CC BY 4.0`, `0%` PII y `docs/E3/datasheet.md`.
- [x] Notebook `laboratorio/E3_multivariado_pca_manova.ipynb` ejecutado con gráficas embebidas (sin scripts temporales residuales).
- [x] Validación local en verde (`exit code 0`): `ruff check .`, `pytest tests/ -v` y `pip-audit`.

```bash
python -m pipeline.benchmark_e3
python -m pipeline.orquestador_e1
ruff check .
pytest tests/ -v
pip-audit --skip-editable --progress-spinner off
```
