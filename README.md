# AgroPulse TDL — Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico

**Proyecto Integrador: Trusted Data Lab (TDL) | Ingeniería en Sistemas Computacionales / Ciencia de Datos — Semestre 7**

**AgroPulse TDL** es un observatorio de datos auditado que integra series hidroclimáticas de las regiones agroproductoras de **Colima** (*Tecomán, Armería y Manzanillo*) con precios mayoristas, volatilidad y costos logísticos hacia cuatro **Centrales de Abasto** estratégicas de México (*CDMX-Iztapalapa, Guadalajara, Monterrey y Occidente*) para cuatro cultivos clave: **Limón Mexicano, Papaya Maradol, Plátano Chiapas y Aguacate Hass**.

Su propósito de negocio es erradicar la venta "a ciegas" ante intermediarios, permitiendo a productores, empacadoras y aseguradoras rurales proteger entre un **$12\%$ y un $25\%$ de margen comercial por embarque** con datos trazables y certificados.

---

## Equipo de Desarrollo

| Integrante | Rol Principal | Responsabilidades Clave | Gobernanza PSP / Calidad |
| :--- | :--- | :--- | :--- |
| **Carlos Daniel Tintos Beltrán** | *Data Engineer* | Extracción ética multifuente (`ExtractorEtico`), almacén Medallion (`bronce` $\rightarrow$ `plata` $\rightarrow$ `oro` + `cuarentena`), automatización GitHub Actions y contratos `pandera`. | Bitácoras [`defectos-carlos.csv`](calidad/defectos-carlos.csv) y [`tiempo-carlos.csv`](calidad/tiempo-carlos.csv) (*Quality Lead* en E1 y E3) |
| **Oliver Vargas García** | *Data Statistician* | Pronósticos de Series de Tiempo (E1), Diseño de Experimentos Factorial $2^3$ y $2^{4-1}$ (E2), Estadística Multivariada PCA + MANOVA (E3) y validación con usuarios. | Bitácoras [`defectos-oliver.csv`](calidad/defectos-oliver.csv) y [`tiempo-oliver.csv`](calidad/tiempo-oliver.csv) (*Quality Lead* en E0 y E2) |

---

## Integración Curricular en un Solo Producto

| Materia | Docente | Eje TDL | Entregables Técnicos en el Repositorio |
| :--- | :--- | :---: | :--- |
| **Ingeniería de Datos** | Mtro. Román | *OBTENER* | Extractores éticos (`Open-Meteo API` + `SNIIM Web`), workflow diario en GitHub Actions y almacén Medallion. |
| **Análisis Estadístico para Ciencia de Datos** | Mtro. Joel | *DEMOSTRAR* | Series históricas de **48 meses** (`2022-11` a `2026-10`) listas para Series de Tiempo, Diseño Factorial y PCA/MANOVA. |
| **Calidad en los Sistemas de Información** | Mtra. Isis | *CERTIFICAR* | Disciplina PSP individual, bitácora activa para MTBF/MTTR/Disponibilidad, `pytest`, `ruff` y estándares ISO 25010/25012. |

---

## Arquitectura Medallion y Estructura del Repositorio

El proyecto aplica **Arquitectura Modular por Capas + Clean Code** (funciones con responsabilidad única $\le 30$ líneas, tipado explícito, cero rutas hardcodeadas fuera de [`config.py`](config.py) y política estricta de **Cero Datos Personales**):

```text
tdl-agropulse/
├── README.md                          # Documentación general e instrucciones reproducibles
├── requirements.txt                   # Dependencias limpias del entorno Python
├── config.py                          # Rutas centralizadas (pathlib.Path), coordenadas y constantes
├── docs/
│   └── E0/
│       ├── ENTREGA.md                 # Ficha ejecutiva y matriz de evidencias de la rúbrica E0
│       └── propuesta.md               # Propuesta formal (ficha, entrevista, preguntas E1-E3, ética y calidad)
├── calidad/
│   ├── defectos-carlos.csv            # Registro PSP de defectos - Carlos Tintos
│   ├── defectos-oliver.csv            # Registro PSP de defectos - Oliver Vargas
│   ├── tiempo-carlos.csv              # Registro PSP de tiempos - Carlos Tintos
│   ├── tiempo-oliver.csv              # Registro PSP de tiempos - Oliver Vargas
│   └── bitacora_captura.csv           # Bitácora automática de ejecuciones (insumo MTBF/MTTR)
├── extractores/
│   ├── base.py                        # Clase oficial ExtractorEtico + registrar_ejecucion_bitacora()
│   ├── extractor_api_clima.py         # Fuente 1: API Open-Meteo (48 meses + captura diaria Colima)
│   ├── extractor_web_precios.py       # Fuente 2: Web scraping ético SNIIM (48 meses, 768 filas + diario)
│   └── ejecutar_captura.py            # Orquestador y validador de Capa Bronce
├── data/
│   ├── bronce/                        # Datos crudos con metadatos fecha_captura y fuente_origen
│   ├── plata/                         # Datos limpios, tipados e integrados (E1+)
│   ├── oro/                           # Tablas analíticas listas para modelado y tablero (E1+)
│   └── cuarentena/                    # Registros rechazados con motivo explícito, 0% borrado silencioso (E1+)
├── pipeline/                          # Transformaciones Medallion y puertas de calidad (E1+)
├── laboratorio/                       # Notebooks reproducibles de Análisis Estadístico (E1-E3)
├── tablero/                           # Observatorio público interactivo en Streamlit (E1-E4)
├── tests/
│   └── test_extractores.py            # Suite de pruebas unitarias con pytest
└── .github/
    └── workflows/
        └── captura_diaria.yml         # Ejecución automática diaria (08:00 UTC) y commit a Bronce
```

---

## Inventario de Datos Activos en Capa Bronce (Etapa E0)

| Archivo en `data/bronce/` | Fuente | Granularidad | Cobertura / Volumen | Variables Principales |
| :--- | :--- | :--- | :--- | :--- |
| [`clima_historico_mensual.csv`](data/bronce/clima_historico_mensual.csv) | Open-Meteo Archive API | Mensual por zona | **48 periodos** (`2022-11` a `2026-10`, $144$ registros) | Temp. máxima, Temp. media, Precipitación acumulada, Evapotranspiración y Humedad relativa en Tecomán, Armería y Manzanillo. |
| [`clima_captura_diaria.csv`](data/bronce/clima_captura_diaria.csv) | Open-Meteo Forecast API | Diaria por zona | Ventana móvil acumulativa diaria | Variables hidroclimáticas diarias + `fecha_captura` y `fuente_origen`. |
| [`precios_agro_historico_mensual.csv`](data/bronce/precios_agro_historico_mensual.csv) | Portal SNIIM (`ExtractorEtico`) | Mensual por cultivo y central | **48 periodos** (`2022-11` a `2026-10`, $768$ registros) | Precio mayorista ($\text{MXN/kg}$), Volatilidad mensual ($\%$), Costo logístico y Margen comercial ($4$ cultivos $\times 4$ centrales). |
| [`precios_captura_diaria.csv`](data/bronce/precios_captura_diaria.csv) | Portal SNIIM (`ExtractorEtico`) | Diaria por cultivo y central | Corte diario acumulativo ($16$ registros/día) | Cotización mayorista diaria, flete estimado, margen y metadatos de captura. |

---

## Instalación y Ejecución Reproducible

### 1. Preparar el entorno virtual e instalar dependencias

```bash
python -m venv .venv
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Ejecutar la captura multifuente hacia Capa Bronce

```bash
python -m extractores.ejecutar_captura
```

Este comando ejecuta en orden los extractores de clima y precios, verifica que ambas fuentes cuenten con al menos **48 periodos históricos** (superando el requisito mínimo de $36$ periodos de la rúbrica), actualiza los cuatro archivos en `data/bronce/` y registra la telemetría de ejecución en [`calidad/bitacora_captura.csv`](calidad/bitacora_captura.csv).

### 3. Ejecutar pruebas unitarias y auditoría de estilo

```bash
ruff check .
pytest -v
```

---

## Navegación Rápida de Entregables

* **Entrega activa (`E0 - Arranque`):**
  * [Ficha de Entrega y Rúbrica E0 (`docs/E0/ENTREGA.md`)](docs/E0/ENTREGA.md)
  * [Propuesta Extensa del Observatorio (`docs/E0/propuesta.md`)](docs/E0/propuesta.md)
* **Tablero Público (Streamlit Cloud):** *En preparación para despliegue continuo en etapas E1–E4 (`tablero/app.py`).*

