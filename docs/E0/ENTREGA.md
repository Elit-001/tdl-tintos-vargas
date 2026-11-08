# Ficha Oficial de Entrega — Etapa E0 (Arranque)

* **Nombre del Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Etiqueta de entrega (Git Tag):** `e0`
* **Fecha de entrega:** 6 de noviembre de 2026
* **Integrantes del Equipo:**
  * **Carlos Daniel Tintos Beltrán** — *Data Engineer* (Captura multifuente ética, arquitectura Medallion y automatización CI/CD)
  * **Oliver Vargas García** — *Data Statistician & Quality Lead (E0)* (Diseño analítico E1–E3, entrevista de campo y métricas PSP)

---

## Resumen Ejecutivo (3 líneas)

**AgroPulse TDL** integra el monitoreo hidroclimático de las zonas agroproductoras de Colima (Tecomán, Armería y Manzanillo) con las cotizaciones mayoristas y costos logísticos de cuatro cultivos líderes hacia cuatro Centrales de Abasto nacionales para eliminar pérdidas de margen de hasta $25\%$ por asimetría informativa. En esta **Entrega E0**, dejamos operando la captura multifuente ética y resiliente en Capa Bronce con **48 periodos históricos mensuales (2022–2026)** y cortes diarios automatizados mediante GitHub Actions. Asimismo, formalizamos la entrevista de campo, la hoja de ruta estadística (Series de Tiempo, Diseño Factorial $2^3/2^{4-1}$ y PCA/MANOVA) y el arranque verificable del sistema de calidad PSP y bitácora de fiabilidad.

---

## Evidencias por Materia y Criterios de la Rúbrica E0

### 1. Ingeniería de Datos — Mtro. Román (*OBTENER*)

| Criterio de Evaluación (Rúbrica E0) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Arquitectura modular y estructura Medallion** | Cumplido | [`config.py`](../../config.py), [`README.md`](../../README.md) | Rutas centralizadas con `pathlib.Path` (`bronce`, `plata`, `oro`, `cuarentena`), SRP estricto ($\le 28$ líneas por función) y `requirements.txt` limpio. |
| **Extractor ético base (`robots.txt`, `User-Agent`, pausa y backoff)** | Cumplido | [`extractores/base.py`](../../extractores/base.py) | Implementa `ExtractorEtico` con `urllib.robotparser`, `User-Agent` académico institucional, pausa $\ge 1.5\text{ s}$ y reintentos con espera exponencial. |
| **Fuente 1: API abierta climática + histórico $\ge 36$ periodos** | Cumplido | [`extractores/extractor_api_clima.py`](../../extractores/extractor_api_clima.py), [`clima_historico_mensual.csv`](../../data/bronce/clima_historico_mensual.csv), [`clima_captura_diaria.csv`](../../data/bronce/clima_captura_diaria.csv) | Conexión a Open-Meteo Archive y Forecast; **48 periodos mensuales** (`2022-11` a `2026-10`, $144$ registros) + captura diaria con metadatos `fecha_captura` y `fuente_origen`. |
| **Fuente 2: Web scraping ético + histórico $\ge 36$ periodos** | Cumplido | [`extractores/extractor_web_precios.py`](../../extractores/extractor_web_precios.py), [`precios_agro_historico_mensual.csv`](../../data/bronce/precios_agro_historico_mensual.csv), [`precios_captura_diaria.csv`](../../data/bronce/precios_captura_diaria.csv) | Uso obligatorio de `ExtractorEtico` sobre portal SNIIM con respaldo resiliente; **48 periodos mensuales** ($768$ registros: $4$ cultivos $\times 4$ centrales) y captura diaria. |
| **Orquestación y automatización diaria en GitHub Actions** | Cumplido | [`extractores/ejecutar_captura.py`](../../extractores/ejecutar_captura.py), [`captura_diaria.yml`](../../.github/workflows/captura_diaria.yml) | Cron programado diario (`08:00 UTC`) + `workflow_dispatch`, `permissions: contents: write` y `commit/push` automático a `data/bronce/` y `calidad/bitacora_captura.csv`. |
| **Análisis técnico, ético y legal (`robots.txt` y LFPDPPP)** | Cumplido | [`propuesta.md` (Sección 4)](./propuesta.md#4-plan-de-recopilación-de-datos-y-análisis-ético-legal) | Auditoría real de `robots.txt` del SNIIM, licencias CC BY 4.0 / Datos Abiertos y cumplimiento estricto de Cero Datos Personales. |

---

### 2. Análisis Estadístico para Ciencia de Datos — Mtro. Joel (*DEMOSTRAR*)

| Criterio de Evaluación (Rúbrica E0) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Definición del problema de valor, cliente y monetización** | Cumplido | [`propuesta.md` (Sección 1)](./propuesta.md#1-ficha-técnica-y-de-negocio-del-observatorio) | Delimitación económica del corredor Colima $\rightarrow$ Centrales de Abasto, pregunta central detonadora y esquema SaaS/DaaS con disposición de pago validada. |
| **Entrevista de campo ($\ge 15\text{ min}$) con actor real del sector** | Cumplido | [`propuesta.md` (Sección 2)](./propuesta.md#2-entrevista-de-campo-con-actor-real-del-sector) | Entrevista de $22$ minutos a comercializador/productor en Valle de Tecomán–Villa de Álvarez con transcripción íntegra de $5$ preguntas y hallazgos accionables. |
| **Pregunta E1 — Series de Tiempo ($\ge 36$ periodos)** | Cumplido | [`propuesta.md` (Sección 3.1)](./propuesta.md#31-pregunta-analítica-e1--series-de-tiempo-y-pronósticos-unidad-3), [`precios_agro_historico_mensual.csv`](../../data/bronce/precios_agro_historico_mensual.csv) | Pronóstico a $6$ meses de precio mayorista y margen comercial comparando SES, Holt, Holt-Winters ($s=12$) y ARIMA/SARIMA sobre **48 meses** disponibles en Bronce. |
| **Pregunta E2 — Diseño Factorial $2^3$ y Fraccionado $2^{4-1}$** | Cumplido | [`propuesta.md` (Sección 3.2)](./propuesta.md#32-pregunta-analítica-e2--diseño-de-experimentos-factorial-23-y-24-1-unidad-4--ruta-ingeniería) | Ruta Ingeniería sobre el pipeline: Concurrencia ($1$ vs $4$), Parser (`html.parser` vs `lxml`), Persistencia (`CSV` vs `Parquet`) y Validación ($D=ABC$), midiendo $\text{ms}$ y tasa de éxito. |
| **Pregunta E3 — Análisis Multivariado (PCA + MANOVA)** | Cumplido | [`propuesta.md` (Sección 3.3)](./propuesta.md#33-pregunta-analítica-e3--estadística-multivariada-pca-y-manova-unidad-5), [`clima_historico_mensual.csv`](../../data/bronce/clima_historico_mensual.csv) | Comparación simultánea de $4$ Centrales de Abasto y $4$ cultivos en $6$ variables continuas (Precio/kg, Volatilidad, Margen, Temp. máx., Precipitación y Humedad relativa). |

---

### 3. Calidad en los Sistemas de Información — Mtra. Isis (*CERTIFICAR*)

| Criterio de Evaluación (Rúbrica E0) | Estado | Evidencia Directa en el Repositorio | Descripción Verificable |
| :--- | :---: | :--- | :--- |
| **Bitácoras PSP de defectos por integrante** | Cumplido | [`calidad/defectos-carlos.csv`](../../calidad/defectos-carlos.csv), [`calidad/defectos-oliver.csv`](../../calidad/defectos-oliver.csv) | Encabezado oficial PSP con $4$ defectos técnicos reales detectados y corregidos en E0 por cada integrante. |
| **Bitácoras PSP de tiempos por integrante** | Cumplido | [`calidad/tiempo-carlos.csv`](../../calidad/tiempo-carlos.csv), [`calidad/tiempo-oliver.csv`](../../calidad/tiempo-oliver.csv) | Encabezado oficial PSP con $6$ sesiones detalladas por integrante ejecutadas del $2$ al $6$ de noviembre de 2026. |
| **Bitácora automatizada de fiabilidad desde E0** | Cumplido | [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv), [`extractores/base.py`](../../extractores/base.py) | Función `registrar_ejecucion_bitacora()` activa en cada corrida con las $7$ columnas requeridas para calcular MTBF, MTTR y Disponibilidad en E1. |
| **Definición de 3 objetivos de calidad medibles** | Cumplido | [`propuesta.md` (Sección 5.2)](./propuesta.md#52-definición-formal-de-los-3-objetivos-de-calidad-medibles-del-proyecto) | Metas cuantitativas bajo ISO 25010 / 25012: Disponibilidad $\ge 95\%$, Completitud en Oro $\ge 98\%$ sin borrado silencioso, y Cobertura $\ge 60\%$ con $0$ secretos expuestos. |
| **Pruebas unitarias e higiene de código verificables** | Cumplido | [`tests/test_extractores.py`](../../tests/test_extractores.py), [`requirements.txt`](../../requirements.txt) | Suite `pytest` ($5/5$ pruebas en verde) y verificación estática `ruff check .` ($0$ errores) integradas en local y en GitHub Actions. |

---

## Verificación Rápida de Reproducibilidad

```bash
pip install -r requirements.txt
python -m extractores.ejecutar_captura
ruff check .
pytest -v
```

