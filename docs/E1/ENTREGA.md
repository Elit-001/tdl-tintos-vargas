# Ficha Oficial de Entrega — Etapa E1 (Fundamentos, Limpieza, Pronósticos y SQA)

* **Nombre del Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etiqueta de entrega (Git Tag):** `e1`
* **Fecha de entrega:** 10 de noviembre de 2026
* **Integrantes del Equipo:**
  * **Carlos Daniel Tintos Beltrán** — *Data Engineer & Quality Lead (E1)* (Puerta de calidad `pandera`, limpieza e integración Medallion, CI/CD DevSecOps y tablero Streamlit)
  * **Oliver Vargas García** — *Data Statistician* (Modelado de series de tiempo en `E1_pronosticos.ipynb`, Plan SQA IEEE 730 y relatoría de métricas PSP / MTBF / MTTR)

---

## Resumen Ejecutivo (3 líneas)

En esta **Entrega E1**, **AgroPulse TDL** implementa el pipeline completo Medallion (`Bronce -> Plata -> Oro + Cuarentena`) validado con contratos estrictos de `pandera` ($0\%$ borrado silencioso), limpieza estadística (diagnóstico MCAR/MAR, imputación temporal, tratamiento IQR, normalización Min-Max y discretización) e integración relacional hacia [`data/oro/dataset_analitico.csv`](../../data/oro/dataset_analitico.csv) y [`data/oro/diccionario_datos.md`](../../data/oro/diccionario_datos.md). En el eje analítico, desarrollamos el laboratorio reproducible [`laboratorio/E1_pronosticos.ipynb`](../../laboratorio/E1_pronosticos.ipynb) comparando cuatro modelos de series de tiempo (SES, Holt, Holt-Winters y ARIMA/SARIMA) con diagnóstico de estacionariedad (ADF) y ruido blanco en residuos (Ljung-Box), desplegando el pronóstico ganador con intervalo de confianza al $95\%$ en [`tablero/app.py`](../../tablero/app.py). Finalmente, certificamos el sistema bajo el **Plan SQA (IEEE 730)** con pruebas `pytest`, `ruff`, `gitleaks` y `pip-audit` en CI/CD, alcanzando una disponibilidad operativa de **$99.79\%$** ($\ge 95\%$ requerido).

---

## Evidencias por Materia y Criterios de la Rúbrica E1

### 1. Ingeniería de Datos — Mtro. Román (*OBTENER Y PROCESAR*)

| Criterio de Evaluación (Rúbrica E1) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Puerta de Calidad con `pandera` y Cuarentena (0% borrado silencioso)** | Cumplido | [`pipeline/puerta_calidad.py`](../../pipeline/puerta_calidad.py), [`clima_rechazados_cuarentena.csv`](../../data/cuarentena/clima_rechazados_cuarentena.csv), [`precios_rechazados_cuarentena.csv`](../../data/cuarentena/precios_rechazados_cuarentena.csv) | Esquemas estrictos `DataFrameSchema` para clima y precios; separa registros válidos a `data/plata/` y desvía fallos con `motivo_rechazo` a `data/cuarentena/`. |
| **Diagnóstico de nulos (MCAR/MAR/MNAR) e imputación** | Cumplido | [`pipeline/limpieza.py`](../../pipeline/limpieza.py) | Funciones `diagnosticar_mecanismo_nulos()` e `imputar_nulos_por_grupo()` mediante interpolación temporal lineal y respaldo por mediana grupal. |
| **Detección de atípicos (IQR), Normalización Min-Max y Discretización** | Cumplido | [`pipeline/limpieza.py`](../../pipeline/limpieza.py), [`precios_limpios_plata.csv`](../../data/plata/precios_limpios_plata.csv), [`clima_limpio_plata.csv`](../../data/plata/clima_limpio_plata.csv) | Criterio de Tukey ($1.5 \times \text{IQR}$) con winsorización y bandera `es_atipico_iqr`, escalado Min-Max `[0, 1]` (`*_norm`) y discretización en `categoria_precio` (`Bajo/Medio/Alto`) y `nivel_volatilidad`. |
| **Integración relacional limpia y Capa Oro documentada** | Cumplido | [`pipeline/integracion.py`](../../pipeline/integracion.py), [`pipeline/orquestador_e1.py`](../../pipeline/orquestador_e1.py), [`dataset_analitico.csv`](../../data/oro/dataset_analitico.csv), [`diccionario_datos.md`](../../data/oro/diccionario_datos.md) | Merge sin colisiones por `periodo_mensual` y `zona_agricola` ($768$ filas consolidadas con $100\%$ de completitud) y generación automática del diccionario de datos. |

---

### 2. Análisis Estadístico para Ciencia de Datos — Mtro. Joel (*DEMOSTRAR*)

| Criterio de Evaluación (Rúbrica E1) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Descomposición de serie temporal, prueba ADF y gráficas ACF/PACF** | Cumplido | [`laboratorio/E1_pronosticos.ipynb`](../../laboratorio/E1_pronosticos.ipynb) | Descomposición en tendencia, estacionalidad ($s=12$) y residuo; contraste formal de raíz unitaria Dickey-Fuller Aumentada (ADF) y correlogramas ACF/PACF interpretados. |
| **Entrenamiento y comparación de 4 modelos (SES, Holt, Holt-Winters, ARIMA)** | Cumplido | [`laboratorio/E1_pronosticos.ipynb`](../../laboratorio/E1_pronosticos.ipynb) | Partición estricta entrenamiento/prueba ($42$ meses train / $6$ meses test) y comparación objetiva mediante **MAE, RMSE y MAPE (%)**. |
| **Selección del modelo ganador y prueba de Ljung-Box en residuos** | Cumplido | [`laboratorio/E1_pronosticos.ipynb`](../../laboratorio/E1_pronosticos.ipynb) | Selección de **Holt-Winters Estacional Aditivo** ($\text{MAPE} = 3.85\%$), verificación de ruido blanco con Ljung-Box ($p > 0.05$) y proyección a $6$ meses con IC al $95\%$. |
| **Tablero público interactivo con pronóstico e interpretación de negocio** | Cumplido | [`tablero/app.py`](../../tablero/app.py) | Aplicación en Streamlit conectada a `data/oro/dataset_analitico.csv` con gráfica del modelo ganador, banda de confianza al $95\%$ y recomendación comercial para empacadoras. |

---

### 3. Calidad en los Sistemas de Información — Mtra. Isis (*CERTIFICAR*)

| Criterio de Evaluación (Rúbrica E1) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Plan SQA estructurado bajo estándar IEEE 730** | Cumplido | [`docs/plan-sqa.md`](../plan-sqa.md) | Cubre Propósito, Roles con rotación de *Quality Lead*, Estándares ISO 25010/25012, Revisiones cruzadas, Pruebas automatizadas y Gestión de defectos. |
| **Automatización CI/CD y Seguridad (`pytest`, `ruff`, `gitleaks`, `pip-audit`)** | Cumplido | [`captura_diaria.yml`](../../.github/workflows/captura_diaria.yml), [`ci_cd.yml`](../../.github/workflows/ci_cd.yml), [`test_pipeline_e1.py`](../../tests/test_pipeline_e1.py) | Ejecución en cada `push` de suite unitaria (`pytest tests/`), linter (`ruff check .`), detección de secretos (`gitleaks detect`) y auditoría de librerías (`pip-audit`). |
| **Relatoría E1 con cálculo de MTBF, MTTR y Disponibilidad** | Cumplido | [`docs/relatoria-E1.md`](../relatoria-E1.md), [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) | Respuesta exhaustiva a las $6$ preguntas metodológicas con $\text{MTBF} = 191.60\text{ hrs}$, $\text{MTTR} = 0.40\text{ hrs}$ y Disponibilidad $A = 99.79\%$. |
| **Actualización de bitácoras PSP individuales (Tiempos y Defectos)** | Cumplido | [`tiempo-carlos.csv`](../../calidad/tiempo-carlos.csv), [`tiempo-oliver.csv`](../../calidad/tiempo-oliver.csv), [`defectos-carlos.csv`](../../calidad/defectos-carlos.csv), [`defectos-oliver.csv`](../../calidad/defectos-oliver.csv) | Se incorporaron $4$ nuevos registros de tiempo y $4$ nuevos defectos técnicos de la etapa E1 en las bitácoras de ambos integrantes. |

---

## Comandos de Ejecución y Verificación Local (E1)

```bash
# 1. Ejecutar el pipeline Medallion E1 (Bronce -> Plata / Cuarentena -> Oro)
python -m pipeline.orquestador_e1

# 2. Verificar estilo y pruebas unitarias (E0 + E1)
ruff check .
pytest tests/ -v

# 3. Lanzar el tablero público en Streamlit
streamlit run tablero/app.py
```

