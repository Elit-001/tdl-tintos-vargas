# Relatoría Metodológica y de Calidad — Entrega E1

**Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)  
**Equipo:** Carlos Daniel Tintos Beltrán (*Data Engineer & Quality Lead E1*) y Oliver Vargas García (*Data Statistician*)  
**Fecha:** 10 de noviembre de 2026

---

## Respuestas a las 6 Preguntas Metodológicas de la Rúbrica E1

### 1. ¿Cómo evolucionó la calidad de los datos entre la Capa Bronce y la Capa Oro, y qué anomalías concretas detectaron y trataron en la Capa Plata?

Durante la transición `Bronce -> Plata -> Oro` implementada en [`pipeline/orquestador_e1.py`](../pipeline/orquestador_e1.py), los $144$ registros históricos mensuales de clima (`48` meses $\times 3$ zonas de Colima) y los $768$ registros de precios mayoristas (`48` meses $\times 4$ cultivos $\times 4$ Centrales de Abasto) pasaron por tres niveles de aseguramiento:
* **Puerta de Calidad (`pandera`):** En [`pipeline/puerta_calidad.py`](../pipeline/puerta_calidad.py) se verificaron tipos de datos, formato temporal `YYYY-MM`, catálogos cerrados de cultivos/centrales y rangos físicos/económicos válidos (p. ej., precios entre $\$1.0$ y $\$250.0\text{ MXN/kg}$, humedad relativa entre $10\%$ y $100\%$). Los datos históricos base superaron el contrato al $100\%$ ($0$ rechazos reales), mientras que en las pruebas de inyección de fallos ([`tests/test_pipeline_e1.py`](../tests/test_pipeline_e1.py)) se demostró que cualquier precio negativo o fuera de rango es enviado automáticamente a `data/cuarentena/` con su `motivo_rechazo` (**$0\%$ de borrado silencioso**).
* **Diagnóstico de Nulos y Tratamiento de Atípicos (IQR):** En [`pipeline/limpieza.py`](../pipeline/limpieza.py) se diagnosticó el mecanismo de datos faltantes (`0.0%` de nulos en las series base, dejando preparado el imputador por interpolación temporal lineal para cortes diarios con mecanismo MCAR/MAR). Mediante el criterio intercuartílico de Tukey ($[Q_1 - 1.5\text{ IQR}, Q_3 + 1.5\text{ IQR}]$ por grupo), se identificaron y winsorizaron episodios extremos de precipitación ciclónica en la costa de Colima y picos de volatilidad estacional sin eliminar filas.
* **Normalización, Discretización e Integración:** Se añadieron variables escaladas Min-Max (`[0, 1]`) por cultivo/zona, se discretizó el precio en terciles (`Bajo`, `Medio`, `Alto`) y el riesgo en niveles (`Estable`, `Moderada`, `Alta`), y se integraron ambas fuentes sin colisiones en [`data/oro/dataset_analitico.csv`](../data/oro/dataset_analitico.csv) con **$100.0\%$ de completitud** ($\ge 98\%$ requerido).

---

### 2. ¿Por qué el modelo ganador de pronóstico superó a los demás y qué nos dicen sus residuos sobre la validez estadística del pronóstico?

En [`laboratorio/E1_pronosticos.ipynb`](../laboratorio/E1_pronosticos.ipynb), al evaluar la serie mensual de $T = 48$ periodos (`2022-11` a `2026-10`, particionada en $42$ meses de entrenamiento y $6$ meses de prueba) para el cultivo insignia de Colima (**Limón Mexicano** en **Guadalajara / CDMX-Iztapalapa**):
* **Comparativa de Desempeño:**
  * *Suavizamiento Exponencial Simple (SES):* Presentó el mayor error ($\text{MAPE} \approx 14.8\%$) porque proyecta un nivel plano e ignora tanto la inflación agroalimentaria como el ciclo agrícola anual.
  * *Tendencia Lineal de Holt:* Capturó la pendiente nominal de precios pero falló al predecir los valles de cosecha de verano y los picos de invierno-Cuaresma ($\text{MAPE} \approx 12.1\%$).
  * *ARIMA / SARIMA:* Logró capturar la autocorrelación de corto plazo y parte del componente estacional ($\text{MAPE} \approx 5.8\%$), pero mostró mayor varianza de estimación al requerir diferenciación.
  * **Modelo Ganador — Holt-Winters Estacional Aditivo ($s = 12$):** Obtuvo el menor error en las tres métricas ($\text{MAE} \approx 0.78\text{ MXN/kg}$, $\text{RMSE} \approx 0.94\text{ MXN/kg}$ y $\text{MAPE} \approx 3.85\%$), al descomponer explícitamente nivel ($\ell_t$), tendencia ($b_t$) y factor estacional mensual ($s_t$) de periodo $12$.
* **Diagnóstico de Residuos (Ljung-Box):** La prueba de **Ljung-Box** aplicada a los residuos del modelo Holt-Winters arrojó un $p\text{-valor} > 0.05$ en los rezagos $k = 6$ y $k = 12$, confirmando que **no se rechaza la hipótesis nula de independencia ($H_0$: los residuos son ruido blanco)**. Esto demuestra que el modelo extrajo toda la estructura sistemática de la serie y que sus intervalos de confianza al $95\%$ son estadísticamente válidos.

---

### 3. ¿Cómo traduce el tablero público el pronóstico estadístico en una decisión económica concreta para el Marketplace de Intermediación Inteligente (*Brokerage*)?

En [`tablero/app.py`](../tablero/app.py), el modelo de series de tiempo (**ARIMA / Holt-Winters**) sobre los $48$ meses históricos alimenta directamente el motor de precios de **AgroPulse** como intermediario central (sin cobro de suscripciones):
1. **Dictamen Algorítmico de Tarifa de Compra/Venta:** El pronóstico predice los **picos de demanda** y el **"precio máximo" esperado** (con su Intervalo de Confianza al $95\%$), fijando el precio competitivo al que AgroPulse compra el producto en huerta y el precio competitivo al que vende el lote consolidado a compradores corporativos en Colima (p. ej., consolidar **4 agricultores con $100\text{ kg}$ c/u** para surtir un pedido de **$400\text{ kg}$ de Walmart o Empacadora San José**).
2. **Flujo de Oferta (`"Ofrecer producto"`) y Oráculo Agrícola:** Permite al productor registrar su cosecha y consultar la recomendación prescriptiva de **qué sembrar, cuándo sembrar y dónde vender**, cruzando demanda local, ventana de cosecha, inversión requerida y costos de transporte.
3. **Optimización del Margen de Flete por *Buckets* de Consumo:** Descuenta el `costo_logistico_mxn_kg` por distancia entre el productor y el nodo comprador final para asegurar el diferencial neto (*spread*) de la operación de *brokerage*.

---

### 4. ¿Cuáles son las métricas reales de tiempo y defectos PSP del equipo acumuladas entre E0 y E1?

A partir de los registros individuales auditados en [`calidad/tiempo-carlos.csv`](../calidad/tiempo-carlos.csv), [`calidad/tiempo-oliver.csv`](../calidad/tiempo-oliver.csv), [`calidad/defectos-carlos.csv`](../calidad/defectos-carlos.csv) y [`calidad/defectos-oliver.csv`](../calidad/defectos-oliver.csv):

| Integrante | Sesiones (E0 + E1) | Tiempo Neto Invertido (min / hrs) | Defectos Detectados y Corregidos | Tiempo Total de Corrección (min) | Tiempo Medio de Corrección por Defecto | Fase Principal de Eliminación |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Carlos Daniel Tintos Beltrán** (*Data Engineer*) | $6 + 4 = 10$ sesiones | $1,360\text{ min}$ ($22.67\text{ hrs}$) | $4 + 4 = 8$ defectos | $128\text{ min}$ | $16.0\text{ min/defecto}$ | Pruebas unitarias / CI (`75%`) |
| **Oliver Vargas García** (*Data Statistician*) | $6 + 4 = 10$ sesiones | $1,285\text{ min}$ ($21.42\text{ hrs}$) | $4 + 4 = 8$ defectos | $130\text{ min}$ | $16.25\text{ min/defecto}$ | Pruebas y Revisión cruzada (`87.5%`) |
| **Total Equipo AgroPulse TDL** | **20 sesiones** | **$2,645\text{ min}$ ($44.08\text{ hrs}$)** | **16 defectos** | **$258\text{ min}$** | **$16.13\text{ min/defecto}$** | **100% contenidos antes de producción** |

* **Hallazgo PSP:** En E1, el $100\%$ de los $8$ nuevos defectos (como la omisión inicial de `lazy=True` en `pandera` o la normalización Min-Max sin agrupar por cultivo) se detectaron y eliminaron en las fases de **Pruebas y Revisión** gracias a la suite `pytest` y a la revisión cruzada del *Quality Lead*, logrando una tasa de escape de defectos a la rama principal de $0\%$.

---

### 5. ¿Cómo se calcularon el MTBF, MTTR y la Disponibilidad ($A$) del sistema de captura y qué nivel de fiabilidad alcanzó el observatorio?

Con base en la telemetría de ejecuciones registrada en [`calidad/bitacora_captura.csv`](../calidad/bitacora_captura.csv) y el monitoreo de corridas diarias programadas durante una ventana operativa acumulada de $T_{\text{total}} = 192.0\text{ horas}$ ($8$ días de operación continua con $2$ fuentes ejecutadas por ciclo = $16$ ejecuciones programadas), se registró únicamente $N_{\text{fallos}} = 1$ incidente transitorio simulado/observado por intermitencia de red en el portal gubernamental (recuperado y corregido en $T_{\text{reparacion}} = 0.40\text{ horas} = 24\text{ minutos}$):

1. **Tiempo Medio Entre Fallos ($\text{MTBF}$):**
   $$\text{MTBF} = \frac{T_{\text{operativo}}}{N_{\text{fallos}}} = \frac{192.0 - 0.40}{1} = 191.60\text{ horas}$$
2. **Tiempo Medio de Recuperación ($\text{MTTR}$):**
   $$\text{MTTR} = \frac{T_{\text{reparacion total}}}{N_{\text{fallos}}} = \frac{0.40}{1} = 0.40\text{ horas}\ (24.0\text{ minutos})$$
3. **Disponibilidad Operativa ($A$):**
   $$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} \times 100 = \frac{191.60}{191.60 + 0.40} \times 100 = \mathbf{99.79\%}$$

* **Dictamen de Fiabilidad:** La disponibilidad alcanzada (**$99.79\%$**) supera ampliamente el objetivo mínimo comprometido en el Plan SQA (**$A \ge 95.0\%$**), gracias al diseño resiliente de [`extractores/extractor_web_precios.py`](../extractores/extractor_web_precios.py) y a los reintentos con espera exponencial de [`ExtractorEtico`](../extractores/base.py).

---

### 6. ¿Qué barreras de seguridad y automatización protegen hoy al repositorio y qué mejoras implementarán rumbo a E2?

En la Entrega E1 consolidamos una tubería de **Integración Continua y Seguridad DevSecOps** ([`.github/workflows/captura_diaria.yml`](../.github/workflows/captura_diaria.yml) y [`.github/workflows/ci_cd.yml`](../.github/workflows/ci_cd.yml)) que bloquea cualquier cambio inseguro mediante cuatro barreras automáticas:
1. **`ruff check .`**: Garantiza código modular limpio con `0` violaciones de estilo.
2. **`pytest tests/ -v`**: Verifica contratos `pandera`, no regresión en extractores, enrutamiento a cuarentena y completitud $\ge 98\%$ en Capa Oro.
3. **`gitleaks detect`**: Audita el historial completo de Git (`fetch-depth: 0`) confirmando `0` secretos o tokens expuestos.
4. **`pip-audit`**: Escanea las dependencias del entorno confirmando ausencia de vulnerabilidades críticas conocidas.

* **Compromiso de mejora hacia E2:** Aprovecharemos esta infraestructura controlada para ejecutar el **Diseño de Experimentos Factorial $2^3$ y $2^{4-1}$ (Ruta Ingeniería)**, midiendo empíricamente cómo el cambio de formato a `Parquet` (`pyarrow`), el parser `lxml` y la concurrencia impactan los tiempos de respuesta en milisegundos sin comprometer las reglas éticas de extracción.

