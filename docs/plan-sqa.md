# Plan de Aseguramiento de la Calidad del Software (Plan SQA) — AgroPulse TDL

**Estándar de Referencia:** IEEE Std 730 — *IEEE Standard for Software Quality Assurance Processes*  
**Estándares Complementarios:** ISO/IEC 25010 (Calidad de Producto de Software) e ISO/IEC 25012 (Calidad de Datos)  
**Versión:** `1.0.0` (Entrega E1)  
**Fecha:** 10 de noviembre de 2026

---

## 1. Propósito y Alcance (Sección 1 IEEE 730)

El presente **Plan de Aseguramiento de la Calidad del Software (SQA)** establece las políticas, roles, estándares técnicos, procedimientos de revisión, puertas de validación de datos y mecanismos de auditoría continua aplicables al observatorio **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*).

Su alcance abarca la totalidad del ciclo de vida del sistema desde la captura multifuente ética en Capa Bronce (`extractores/`), el procesamiento y limpieza Medallion hacia Capas Plata, Cuarentena y Oro (`pipeline/`), los modelos estadísticos reproducibles (`laboratorio/`), el tablero público en Streamlit (`tablero/app.py`) y los flujos de integración y despliegue continuo (`.github/workflows/`).

---

## 2. Organización, Roles y Responsabilidades (Sección 2 IEEE 730)

El equipo opera bajo disciplina **Personal Software Process (PSP)** y aplica un esquema de **rotación de liderazgo de calidad (*Quality Lead*)** por entrega para garantizar revisiones cruzadas imparciales (ningún autor aprueba su propio código sin verificación):

| Integrante | Rol Técnico Principal | Responsabilidades SQA y de Ingeniería | Liderazgo SQA (*Quality Lead*) |
| :--- | :--- | :--- | :---: |
| **Carlos Daniel Tintos Beltrán** | *Data Engineer* | Autoría de extractores éticos (`ExtractorEtico`), contratos de datos `pandera` (`puerta_calidad.py`), limpieza e integración Medallion (`limpieza.py`, `integracion.py`), seguridad CI/CD (`gitleaks`, `pip-audit`) y bitácora operativa. | **Quality Lead en E1 y E3** |
| **Oliver Vargas García** | *Data Statistician* | Autoría de notebooks estadísticos reproducibles (`E1_pronosticos.ipynb`), validación de supuestos econométricos (ADF, Ljung-Box), auditoría de diccionarios de datos y cálculo de indicadores de fiabilidad (MTBF, MTTR, Disponibilidad). | **Quality Lead en E0 y E2** |

---

## 3. Estándares, Prácticas, Convenciones y Métricas (Sección 3 IEEE 730)

### 3.1 Estándares de Codificación y Arquitectura
1. **Arquitectura Medallion y Principio de Responsabilidad Única (SRP):** Separación física y lógica en `data/bronce/`, `data/plata/`, `data/oro/` y `data/cuarentena/`. Ningún módulo repite rutas fuera de [`config.py`](../config.py).
2. **Modularidad y Legibilidad (Cero Código Espagueti):** Toda función de Python realiza una única tarea, no excede **30 líneas de código**, declara *Type Hints* explícitos y documenta su propósito mediante docstrings en español.
3. **Estándar de Estilo Automatizado:** Cumplimiento del $100\%$ de las reglas de `ruff` (`PEP 8`, ordenamiento de imports `I001` y modernización `pyupgrade`), exigiendo `0` advertencias antes de fusionar a `main`.
4. **Política de Cero Borrado Silencioso e Integridad ISO/IEC 25012:** En [`pipeline/puerta_calidad.py`](../pipeline/puerta_calidad.py), todo registro que incumpla los contratos `pandera` se separa hacia `data/cuarentena/` con la columna `motivo_rechazo`, cumpliendo la invariante:
   $$N_{\text{Bronce}} = N_{\text{Plata}} + N_{\text{Cuarentena}}$$

### 3.2 Umbrales Cuantitativos de Calidad (SLAs del Observatorio)

| Código | Métrica de Calidad | Estándar Base | Umbral Mínimo Aceptable | Mecanismo de Verificación |
| :---: | :--- | :--- | :---: | :--- |
| **M-SQA-01** | Disponibilidad operativa del pipeline ($A$) | ISO/IEC 25010 (Fiabilidad) | $A \ge 95.0\%$ | Cálculo $A = \frac{\text{MTBF}}{\text{MTBF}+\text{MTTR}}$ sobre [`calidad/bitacora_captura.csv`](../calidad/bitacora_captura.csv) |
| **M-SQA-02** | Completitud de celdas en Capa Oro | ISO/IEC 25012 (Completitud) | $\ge 98.0\%$ | Verificación automática en [`pipeline/integracion.py`](../pipeline/integracion.py) y `pytest` |
| **M-SQA-03** | Tasa de borrado silencioso de registros | ISO/IEC 25012 (Exactitud) | $0.0\%$ | Auditoría de conservación `Bronce = Plata + Cuarentena` en [`pipeline/orquestador_e1.py`](../pipeline/orquestador_e1.py) |
| **M-SQA-04** | Higiene de código y cobertura funcional | ISO/IEC 25010 (Mantenibilidad) | `0` errores `ruff` y $100\%$ tests en verde | Ejecución de `ruff check .` y `pytest tests/` en cada `push` |
| **M-SQA-05** | Exposición de secretos y vulnerabilidades | ISO/IEC 25010 (Seguridad) | `0` secretos y `0` CVEs críticos | Ejecución de `gitleaks detect` y `pip-audit` en GitHub Actions |

---

## 4. Revisiones y Auditorías Técnicas (Sección 4 IEEE 730)

1. **Revisión Cruzada de Código y Notebooks (*Peer Review*):** Antes de cerrar cada entrega (`E0` a `E4`), el *Quality Lead* en turno inspecciona que las funciones cumplan SRP, que los notebooks de `laboratorio/` ejecuten de principio a fin sin errores (`Restart & Run All`) y que los enlaces relativos de `ENTREGA.md` resuelvan correctamente.
2. **Auditoría de Puerta de Calidad de Datos:** En cada ejecución de [`pipeline/orquestador_e1.py`](../pipeline/orquestador_e1.py), se auditan automáticamente:
   * El diagnóstico de mecanismos de valores faltantes (**MCAR / MAR / MNAR**) y su imputación temporal.
   * El conteo de valores extremos tratados por el criterio de Tukey ($1.5 \times \text{IQR}$).
   * La generación actualizada de [`data/oro/diccionario_datos.md`](../data/oro/diccionario_datos.md).

---

## 5. Estrategia de Pruebas y Seguridad CI/CD (Sección 5 IEEE 730)

El aseguramiento continuo se ejecuta automáticamente en cada `push` a la rama `main` mediante los flujos [`.github/workflows/captura_diaria.yml`](../.github/workflows/captura_diaria.yml) y [`.github/workflows/ci_cd.yml`](../.github/workflows/ci_cd.yml):

1. **Pruebas Unitarias y de Integración (`pytest tests/`):**
   * [`tests/test_extractores.py`](../tests/test_extractores.py): Verifica configuración ética (`User-Agent`, pausa $\ge 1.5\text{ s}$), existencia de archivos en Bronce, cardinalidad histórica ($\ge 48$ meses $> 36$ requeridos) e integridad de `bitacora_captura.csv`.
   * [`tests/test_pipeline_e1.py`](../tests/test_pipeline_e1.py): Inyecta lotes de prueba con precios inválidos para demostrar que `pandera` los desvía a `data/cuarentena/` con `motivo_rechazo` sin pérdida de filas, y valida que `data/oro/dataset_analitico.csv` supere el $98\%$ de completitud.
2. **Inspección Estática (`ruff check .`):** Valida sintaxis, tipado limpio y estilo en todos los paquetes (`extractores/`, `pipeline/`, `tablero/`, `tests/`).
3. **Seguridad y Prevención de Fuga de Credenciales (`gitleaks detect` y `pip-audit`):** Escanea todo el historial de commits verificando ausencia total de llaves API, contraseñas o tokens, y audita las versiones de `requirements.txt` contra la base nacional de vulnerabilidades de Python (PyPA Advisory Database).

---

## 6. Gestión de Defectos, Acciones Correctivas y Mejora Continua (Sección 6 IEEE 730)

Todo defecto detectado durante diseño, codificación, pruebas o revisión se registra inmediatamente en las bitácoras PSP individuales ([`calidad/defectos-carlos.csv`](../calidad/defectos-carlos.csv) y [`calidad/defectos-oliver.csv`](../calidad/defectos-oliver.csv)) siguiendo la taxonomía estándar de Humphrey:
* `10-Documentacion`, `20-Sintaxis`, `30-Construccion`, `40-Asignacion`, `50-Interfaz`, `60-Chequeo`, `70-Datos`, `80-Funcion`.

**Flujo de Acción Correctiva:**
1. **Detección y Aislamiento:** Identificación de la fase donde se introdujo el defecto (`fase_introducido`) y la fase donde fue contenido (`fase_eliminado`).
2. **Corrección y Medición:** Registro de los `minutos_correccion` reales y trazabilidad de `defecto_origen` si el fallo derivó de una corrección previa.
3. **No Regresión:** Cada defecto crítico de datos o interfaz da origen a una aserción permanente en `tests/` o en los esquemas `pandera` para impedir su reaparición en entregas posteriores (`E2` a `E4`).

