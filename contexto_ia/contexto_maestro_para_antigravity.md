# CONTEXTO MAESTRO DEL PROYECTO: TRUSTED DATA LAB (TDL)

> **INSTRUCCIÓN PARA ANTIGRAVITY:** Lee y mantén este archivo como tu regla principal de contexto durante todo el desarrollo del proyecto. Nunca alteres la arquitectura de carpetas ni las reglas de estilo de código definidas aquí.

## 1. Identidad del Observatorio y del Equipo
* **Nombre del Observatorio:** **AgroPulse TDL** – Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico.
* **Equipo de Desarrollo:**
  * **Carlos Daniel Tintos Beltrán** – *Data Engineer* (Líder de captura multifuente, almacén Medallion, limpieza, integración y puertas de calidad).
  * **Oliver Vargas García** – *Data Statistician* (Líder de pronósticos de series de tiempo, diseño de experimentos factorial y análisis multivariado PCA/MANOVA).
  * *Nota de Calidad:* Ambos llevan registro individual PSP y alternan el rol de *Quality Lead* en cada entrega.
* **Sector y Región:** Agroindustria y Comercialización Mayorista (Valle de Tecomán/Armería/Manzanillo en Colima hacia compradores corporativos locales y nodos mayoristas).
* **Problema de Dinero que Resuelve:** Pequeños y medianos productores de limón, papaya, plátano y aguacate en Colima venden pulverizados y "a ciegas" ante intermediarios tradicionales (*coyotes*), sin volumen individual para surtir pedidos directos de compradores ancla (como Walmart o Empacadora San José) y sin cruzar clima, inversión, tiempos de cosecha ni costos de flete. Esto les cuesta entre un $12\%$ y un $25\%$ de margen por lote.
* **Quién Paga (Modelo de Negocio — Marketplace de Intermediación Inteligente / Brokerage):**
  1. **El Sistema como Intermediario Central (Cero Suscripciones):** AgroPulse no cobra suscripciones; gana dinero mediante el **margen de intermediación comercial (*spread*)**. Consolida la oferta de pequeños productores (ej. $4$ agricultores con $100\text{ kg}$ c/u) para satisfacer grandes pedidos de compradores en Colima (ej. Walmart o Empacadora San José pidiendo $400\text{ kg}$), comprando al productor a precio competitivo y vendiendo al comprador a precio competitivo.
  2. **Valor para el Productor (Flujo de Oferta y Oráculo Agrícola):** Incluye el botón clave **"Ofrecer producto"** y opera como **oráculo agrícola** que recomienda qué sembrar, cuándo sembrar y dónde vender cruzando demanda local, tiempo de cosecha, inversión del productor y costos de transporte.

## 2. Las 3 Materias en un Solo Producto
1. **Ingeniería de Datos (Mtro. Román - OBTENER):** Extracción multifuente ética (Web Scraping con `ExtractorEtico` + APIs abiertas), automatización con GitHub Actions, arquitectura Medallion (`bronce` $\rightarrow$ `plata` $\rightarrow$ `oro` + `cuarentena`), validación automática con `pandera` y cálculo geoespacial de costos logísticos por distancia entre productor y comprador final (*buckets* de consumo en E2) para optimizar el margen del flete.
2. **Análisis Estadístico para Ciencia de Datos (Mtro. Joel - DEMOSTRAR):** Notebooks reproducibles con Series de Tiempo ARIMA/Holt-Winters en E1 (para predecir picos de demanda y el "precio máximo" que dictamina la tarifa de compra/venta del *broker*), Diseño de Experimentos Factorial $2^3$ y $2^{4-1}$ (E2), y Estadística Multivariada PCA + MANOVA (E3).
3. **Calidad en los Sistemas de Información (Mtra. Isis - CERTIFICAR):** Registro PSP (defectos y tiempos en CSV), métricas de fiabilidad ($A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$), seguridad (`gitleaks`, `pip-audit`), Plan SQA (IEEE 730), CI/CD con `pytest` y `ruff`, evaluación ISO/IEC 25010 e ISO/IEC 25012, y obtención del Sello TDL.

## 3. Metodología de Desarrollo (Cero Código Espagueti)
Aplicamos **Arquitectura Modular por Capas + Clean Code + DataOps Medallion**:
1. **Principio de Responsabilidad Única (SRP):**
   * Un archivo `config.py` centraliza rutas, URLs y constantes (prohibido repetir rutas hardcodeadas en varios scripts).
   * Cada función hace **una sola cosa** y tiene máximo 25–30 líneas de código.
   * Cada script tiene un punto de entrada limpio: `if __name__ == "__main__":`.
2. **Tipado Básico y Docstrings Claros:** Usa *Type Hints* sencillos de Python (`def extraer_datos(url: str) -> pd.DataFrame:`) y un comentario breve al inicio de cada función explicando qué hace y qué punto de la rúbrica cumple.
3. **Idioma 100% Español:** Todos los nombres de variables, funciones, columnas de datos, commits y comentarios deben estar en español claro.
4. **Prohibido sobre-ingenierizar:** NO uses metaclases, decoradores complejos personalizados, `asyncio` avanzado, ni patrones empresariales oscuros. El código debe verse hecho por estudiantes universitarios sobresalientes y ordenados.
5. **Uso obligatorio del Extractor Base:** Todo web scraping debe heredar o utilizar exactamente la clase `ExtractorEtico` oficial en `extractores/base.py`.
6. **Cero Datos Personales:** Nunca guardes nombres de personas físicas, teléfonos ni correos en ninguna capa.

## 4. Estructura Obligatoria del Repositorio
```
tdl-agropulse/
├── README.md                  # Descripción ejecutiva, equipo, arquitectura, cómo ejecutar y URL del tablero
├── requirements.txt           # Dependencias exactas y limpias
├── config.py                  # Rutas centralizadas, coordenadas y constantes del proyecto
├── contexto_ia/               # Archivos .md de contexto e instrucciones para IA
├── docs/                      # Documentación y entregables oficiales
│   ├── E0/                    # ENTREGA.md y propuesta.md (3 a 5 páginas completas)
│   ├── E1/                    # ENTREGA.md
│   ├── E2/                    # ENTREGA.md
│   ├── E3/                    # ENTREGA.md
│   ├── E4/                    # ENTREGA.md, reporte_inteligencia.md, reporte_tecnico.md
│   ├── presentaciones/        # Guiones y material de apoyo para Panel y Demo Day
│   ├── relatoria-E1.md
│   ├── relatoria-E2.md
│   ├── relatoria-E3.md
│   ├── plan-sqa.md            # Basado en IEEE 730 (E1)
│   ├── etica-datos.md         # Análisis legal y ético por fuente (E2)
│   └── auditoria/             # Reportes de auditoría ISO 25010 / 25012 (E2 y E3)
├── calidad/                   # Bitácoras PSP individuales y de fiabilidad
│   ├── defectos-carlos.csv
│   ├── defectos-oliver.csv
│   ├── tiempo-carlos.csv
│   ├── tiempo-oliver.csv
│   └── bitacora_captura.csv   # Registro automático de cada ejecución de los extractores
├── extractores/               # Módulos de captura de datos (Capa Bronce)
│   ├── __init__.py
│   ├── base.py                # Clase ExtractorEtico oficial + función registrar_bitacora()
│   ├── extractor_api_clima.py # Fuente 1: API Open-Meteo (histórico >= 48 meses y diario)
│   ├── extractor_web_precios.py # Fuente 2: Scraping ético de precios mayoristas + serie histórica >= 48 meses
│   └── ejecutar_captura.py    # Script orquestador que corre las fuentes y guarda en bronce
├── pipeline/                  # Procesamiento Medallion y Puertas de Calidad (E1+)
│   └── __init__.py
├── data/                      # Almacén por capas
│   ├── bronce/                # Datos crudos particionados con fecha y origen (>= 36 periodos)
│   ├── plata/                 # Datos limpios e integrados
│   ├── oro/                   # Datos analíticos + diccionario_datos.md
│   └── cuarentena/            # Registros rechazados con motivo
├── laboratorio/               # Notebooks reproducibles de Análisis Estadístico (E1+)
├── tablero/                   # Observatorio público en Streamlit
│   └── app.py
├── tests/                     # Pruebas unitarias con pytest
│   └── test_extractores.py
└── .github/
    └── workflows/
        └── captura_diaria.yml # Cron diario que corre extractores y actualiza bitacora_captura.csv
```

## 5. Regla Crítica de Registro de Fiabilidad (Desde E0)
Cada vez que un extractor se ejecute, debe registrar un renglón en `calidad/bitacora_captura.csv` con las columnas:
`timestamp_inicio,timestamp_fin,fuente,estado,registros_obtenidos,tiempo_segundos,mensaje_error`
Esto es indispensable para calcular en E1 las métricas reales de **MTBF, MTTR y Disponibilidad** ($A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}}$).

## 6. Estado Actual del Proyecto
* **Etapa activa:** `E0 - Arranque` (Fecha límite: Lunes 9 de noviembre, 23:59 hrs).
* **Integrante 1 (Data Engineer):** Carlos Daniel Tintos Beltrán (`carlos`)
* **Integrante 2 (Data Statistician):** Oliver Vargas García (`oliver`)