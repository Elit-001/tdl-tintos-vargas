# Propuesta Formal del Observatorio de Datos — Entrega E0 (Arranque)

**Proyecto Integrador: Trusted Data Lab (TDL) — Semestre 7**  
**Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)  
**Fecha de entrega:** 6 de noviembre de 2026  
**Versión del documento:** `1.0.0` (Etiqueta de lanzamiento: `e0`)

---

## 1. Ficha Técnica y de Negocio del Observatorio

### 1.1 Identidad Institucional y Equipo de Desarrollo

| Atributo | Especificación Oficial |
| :--- | :--- |
| **Nombre del Observatorio** | **AgroPulse TDL** — Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico |
| **Sector Económico** | Agroindustria Hortofrutícola y Comercialización Mayorista de Perecederos |
| **Región de Estudio** | Corredor Agroproductor Costero de Colima (*Tecomán, Armería y Manzanillo*) con destino a cuatro nodos mayoristas nacionales (*CDMX-Iztapalapa, Guadalajara, Monterrey y Occidente*) |
| **Cultivos Monitoreados** | Limón Mexicano (*Citrus aurantifolia*), Papaya Maradol (*Carica papaya*), Plátano Chiapas (*Musa paradisiaca*) y Aguacate Hass (*Persea americana*) |
| **Integrante 1 (Data Engineer)** | **Carlos Daniel Tintos Beltrán** — Responsable de arquitectura Medallion (`bronce` $\rightarrow$ `plata` $\rightarrow$ `oro` + `cuarentena`), extracción multifuente ética, orquestación CI/CD y puertas de calidad automatizadas |
| **Integrante 2 (Data Statistician)** | **Oliver Vargas García** — Responsable de modelado de series de tiempo, diseño experimental factorial, análisis multivariado (PCA y MANOVA) y validación inferencial (*Quality Lead* en E0) |

### 1.2 Problema Económico y Pregunta Central Detonadora

En el corredor agroindustrial del Valle de Tecomán, Armería y la franja costera de Manzanillo (estado de Colima), cientos de productores medianos y empacadoras regionales toman decisiones semanales de corte y embarque bajo condiciones de **asimetría severa de información**. La asignación de destino comercial suele definirse por llamadas informales con intermediarios (*coyotes* o comisionistas en bodega), sin cruzar de manera sistemática las anomalías agroclimáticas en las huertas de origen —golpes de calor que aceleran la maduración del fruto, lluvias torrenciales que frenan el corte o estrés hídrico por alta evapotranspiración— con los diferenciales reales de precios mayoristas y costos logísticos hacia las principales Centrales de Abasto del país.

Esta desconexión informativa provoca saturación de plazas cercanas (como Guadalajara u Occidente) mientras otras plazas distantes (como Monterrey o CDMX-Iztapalapa) presentan ventanas de escasez y sobreprecio, ocasionando pérdidas estimadas de entre **$12\%$ y $25\%$ del margen comercial neto por embarque** debido a castigos de precio en destino, mermas por espera en andén y fletes subóptimos.

> **Pregunta Central Detonadora del Observatorio:**  
> *¿En qué medida la integración automatizada y auditada del régimen hidroclimático de las zonas productoras de Colima con la dinámica histórica de precios mayoristas y costos logísticos en cuatro Centrales de Abasto nacionales permite anticipar ventanas de precio, optimizar el rendimiento técnico del pipeline de captura y discriminar estadísticamente las plazas de mayor margen ajustado por volatilidad para los cuatro cultivos estratégicos de la región?*

### 1.3 Cliente Potencial, Modelo de Monetización y Disposición de Pago

* **Segmento de Clientes Primarios (B2B):**
  1. **Empacadoras y comercializadoras hortofrutícolas** del Valle de Tecomán, Armería y Villa de Álvarez que despachan de $8$ a $40$ camiones mensuales hacia mercados nacionales.
  2. **Uniones de productores y cooperativas citrícolas/frutícolas** de Colima que negocian precios piso de compra en báscula.
  3. **Financieras rurales, fondos de aseguramiento agrícola y empresas de transporte refrigerado**, interesadas en evaluar riesgo climático-comercial antes de otorgar créditos de avío o coberturas paramétricas.
* **Modelo de Monetización Propuesto:** Esquema **SaaS escalonado + Datos como Servicio (DaaS)**:
  * *Nivel Abierto (Público / Productor Social):* Acceso gratuito al tablero interactivo semanal en Streamlit con promedios históricos mensuales y semáforo agroclimático regional.
  * *Nivel Profesional Empacadora (Suscripción Mensual):* $\$2,490\text{ MXN/mes}$ por empacadora (equivalente a recuperar apenas $\$0.14\text{ MXN/kg}$ en un solo embarque de $18$ toneladas), incluyendo alertas diarias de diferencial de margen neto por Central de Abasto, pronósticos a $6$ meses y descarga certificada con Sello TDL.
  * *Nivel Corporativo / Financiero (API REST Oro):* $\$6,900\text{ MXN/mes}$ para aseguradoras e intermediarios financieros con acceso programático a las tablas analíticas limpias (`data/oro/`) y diccionarios auditados bajo ISO/IEC 25012.
* **Disposición de Pago Validada:** En la entrevista exploratoria de campo (Sección 2), el actor comercial confirmó que un error de elección de plaza en un solo camión tipo *rabón* o *tráiler* representa entre $\$18,000$ y $\$45,000\text{ MXN}$ de diferencia en liquidación neta, validando plena disposición a cubrir una membresía mensual de entre $\$2,000$ y $\$3,000\text{ MXN}$ siempre que el dato sea puntual, transparente y libre de manipulación por comisionistas.

---

## 2. Entrevista de Campo con Actor Real del Sector

### 2.1 Contexto Metodológico y Resguardo Ético de Identidad

* **Fecha y hora de realización:** Martes 3 de noviembre de 2026, de 10:35 a 10:57 hrs (**duración efectiva: 22 minutos**, superando el mínimo requerido de 15 minutos).
* **Modalidad y ubicación:** Entrevista semiestructurada presencial realizada en oficinas operativas de acopio en el corredor agrocomercial **Villa de Álvarez – Valle de Tecomán, Colima**.
* **Perfil del entrevistado (Anonimizado por cumplimiento LFPDPPP):** `Actor Clave ID-ENT-01` — Socio operativo y coordinador de embarques en comercializadora regional de limón mexicano y papaya maradol con $14$ años de trayectoria en acopio en huerta, selección en banda y envío mayorista hacia Guadalajara, CDMX y Monterrey (volumen promedio de $20$ embarques mensuales). *En estricto apego a la política de Cero Datos Personales del proyecto, se omiten nombre propio, razón social individualizable, teléfono y correo particular.*
* **Entrevistadores:** Oliver Vargas García (conducción y registro analítico) y Carlos Daniel Tintos Beltrán (indagación sobre flujos de datos y tiempos de decisión).

### 2.2 Transcripción de las 5 Preguntas Clave y Respuestas Completas

**Pregunta 1. ¿Cómo deciden hoy a qué Central de Abasto mandar la fruta cada semana y qué información revisan antes de cerrar el flete?**  
> **Respuesta (`ID-ENT-01`):** *"Siendo sinceros, casi todo se decide por teléfono y WhatsApp entre las seis y las nueve de la mañana del día de corte. Hablamos con dos o tres bodegueros de confianza en Guadalajara y en Iztapalapa; ellos nos dicen 'mándame el limón del número 2, anda sobre veinticuatro pesos', pero ese precio es de palabra y cuando el camión llega doce o dieciséis horas después te salen con que entraron diez carros de Michoacán o Veracruz y te liquidan tres o cuatro pesos abajo. A veces revisamos la página del SNIIM en la computadora, pero es tediosa de consultar producto por producto, a ratos no carga y no te junta cuánto te cuesta el flete ni cómo viene la temporada respecto a otros años."*

**Pregunta 2. ¿De qué manera les pega el clima aquí en Tecomán, Armería o la costa en el volumen de corte, la calidad de la fruta y el precio al que logran vender?**  
> **Respuesta (`ID-ENT-01`):** *"El clima manda todo el calendario, aunque casi nadie lo mide con números. Cuando se vienen dos o tres días seguidos de lluvia fuerte en Tecomán o Armería, la cuadrilla no puede entrar a cortar limón porque si lo cortas mojado se mancha de oleocelosis en el viaje; eso frena la salida dos o tres días y en las centrales sube el precio de golpe. Al revés, cuando pega el calorón seco arriba de treinta y tres grados con mucha evaporación y poca humedad, el limón se amarillea más rápido en el árbol y la papaya acelera madurez: tienes que sacar la fruta sí o sí a plazas cercanas como Guadalajara aunque el precio esté castigado, porque no te aguanta el viaje largo hasta Monterrey sin merma."*

**Pregunta 3. Entre vender en mercados cercanos como Guadalajara u Occidente frente a plazas lejanas como CDMX o Monterrey, ¿dónde pierden más margen sin darse cuenta?**  
> **Respuesta (`ID-ENT-01`):** *"El error clásico del productor y de varios empaques es fijarse nada más en el precio bruto por kilo. Escuchan que en Monterrey el kilo de papaya o de limón está cuatro pesos más caro que en Guadalajara y quieren mandar todo para allá, pero no descuentan bien el diésel, las casetas, el termo cuando hace calor y la volatilidad del mercado norteño. Hay meses donde Guadalajara deja mejor margen limpio por kilo con la mitad de riesgo, y otros meses —sobre todo entre enero y marzo en Cuaresma— donde Monterrey e Iztapalapa sí pagan el flete con creces. Hoy ese cálculo lo hacemos en una libreta o a ojo."*

**Pregunta 4. Si tuvieran una plataforma confiable con historial de varios años y pronósticos, ¿con cuánta anticipación necesitarían ver las tendencias y qué indicadores les servirían de verdad?**  
> **Respuesta (`ID-ENT-01`):** *"Necesitamos dos vistas distintas. Una diaria o semanal muy clara que me diga hoy cómo cerró cada central, cuánto es el margen estimado ya quitando flete y cómo estuvo la lluvia y el calor en la semana aquí en la costa. Y otra vista de mediano plazo, de tres a seis meses hacia adelante, porque los contratos de compra en huerta a precio fijo o las compras de cajas de plástico y cartón las amarramos con meses de anticipación. Si yo veo con datos de cuatro años atrás en qué meses exactos despega el precio o sube mucho la variación, sé cuándo aguantar inventario o asegurar flete."*

**Pregunta 5. ¿Qué necesitaría tener este observatorio para que ustedes confíen en sus números e incluso estuvieran dispuestos a pagar una suscripción mensual por usarlo?**  
> **Respuesta (`ID-ENT-01`):** *"Primero, que no me mienta cuando falle un dato: si un día el gobierno no subió precios, prefiero que el sistema me ponga claramente la fecha real de captura y de dónde salió, en lugar de inventar cosas raras sin avisar. Segundo, que sea rapidísimo de leer en una sola pantalla comparando Limón, Papaya, Plátano y Aguacate en las cuatro plazas. Si una herramienta así nos evita aunque sea mandar mal un solo camión al mes, pagar dos mil o dos mil quinientos pesos mensuales sale regalado comparado con perder treinta mil pesos en una mala liquidación."*

### 2.3 Aprendizajes Clave que Moldearon el Diseño de AgroPulse TDL

1. **Prioridad del Margen Comercial sobre el Precio Bruto:** Se incorporaron explícitamente en `extractor_web_precios.py` las variables `costo_logistico_mxn_kg`, `margen_comercial_mxn_kg` y `margen_comercial_pct` diferenciadas por distancia logística hacia cada Central de Abasto.
2. **Acoplamiento Físico Clima–Corte–Destino:** Se seleccionaron en `extractor_api_clima.py` exactamente las cinco variables agronómicas mencionadas empíricamente en campo: `temperatura_max_c`, `temperatura_media_c`, `precipitacion_acumulada_mm`, `evapotranspiracion_mm` y `humedad_relativa_pct` en Tecomán, Armería y Manzanillo.
3. **Doble Horizonte Temporal (Operativo Diario + Táctico de 48 Meses):** La Capa Bronce separa desde E0 las tablas diarias (`*_captura_diaria.csv`) para seguimiento inmediato y las series históricas consolidadas de **48 periodos mensuales** (`2022-11` a `2026-10`, superando en $33\%$ el mínimo de $36$ periodos de la rúbrica) para modelado estacional robusto.
4. **Transparencia de Linaje y Resiliencia ante Caídas Gubernamentales:** Cada fila persiste metadatos explícitos (`fecha_captura`, `fuente_origen`) y bitácora operativa (`bitacora_captura.csv`) para auditar la disponibilidad real del sistema.

---

## 3. Las 3 Preguntas Analíticas del Proyecto (Hoja de Ruta Estadística E1–E3)

### 3.1 Pregunta Analítica E1 — Series de Tiempo y Pronósticos (Unidad 3)

* **Enunciado Formal:**  
  *¿Qué modelo de pronóstico univariado —Suavizamiento Exponencial Simple (SES), Tendencia Lineal de Holt, Holt-Winters Estacional (aditivo/multiplicativo con $s = 12$) o modelos Box-Jenkins $\text{ARIMA}(p,d,q)$ / $\text{SARIMA}(p,d,q)(P,D,Q)_{12}$— minimiza el error de predicción fuera de muestra ($\text{RMSE}$ y $\text{MAPE}$) al proyectar con un horizonte de $h = 6$ meses el precio mayorista mensual ($\text{MXN/kg}$) y el margen comercial de los cultivos líderes de Colima sobre la serie histórica de $T = 48$ meses (`2022-11` a `2026-10`)?*
* **Diseño Metodológico y Matemático:**
  * **Unidad observacional:** Serie mensual regular de longitud $T = 48$ observaciones por combinación cultivo–central ($4 \times 12$ ciclos anuales completos, superando el umbral $T \ge 36$ requerido para estimar estacionalidad de orden $12$).
  * **Partición temporal estricta (sin fuga de datos):** Conjunto de entrenamiento $T_{\text{train}} = 42$ meses (`2022-11` a `2026-04`) y conjunto de prueba $T_{\text{test}} = 6$ meses (`2026-05` a `2026-10`), para posteriormente reentrenar sobre los $48$ meses y emitir el pronóstico operativo `2026-11` a `2027-04`.
  * **Pruebas diagnósticas:** Descomposición STL (tendencia, estacionalidad $S_t$ y residuo $R_t$), pruebas de estacionariedad Augmented Dickey-Fuller (ADF) y KPSS, selección por $\text{AIC}_c/\text{BIC}$, y verificación de ruido blanco en residuos mediante prueba de Ljung-Box ($p > 0.05$) y normalidad de Jarque-Bera.
  * **Valor de negocio:** Permite a las empacadoras pactar precios forward de cajas, transporte y contratos de acopio semestrales identificando anticipadamente la ventana invernal-Cuaresma de máximo margen neto.

### 3.2 Pregunta Analítica E2 — Diseño de Experimentos Factorial $2^3$ y $2^{4-1}$ (Unidad 4 — Ruta Ingeniería)

* **Enunciado Formal:**  
  *¿Cuál es el efecto principal y de interacción de tres factores técnicos de ingeniería del pipeline de AgroPulse TDL —Concurrencia de extracción ($A$), Motor de parseo HTML ($B$) y Formato de persistencia en disco ($C$)— sobre el tiempo total de ejecución extremo a extremo ($Y_1$, en $\text{ms}$) y la tasa efectiva de procesamiento sin fallos ($Y_2$, en $\text{registros/s}$), y cómo se comporta una extensión fraccionada $2^{4-1}$ al incorporar la estrategia de validación de esquemas ($D$)?*
* **Matriz de Factores y Niveles Experimentales:**

| Factor | Nombre Técnico en el Pipeline | Nivel Bajo ($-1$) | Nivel Alto ($+1$) | Justificación de Ingeniería |
| :---: | :--- | :--- | :--- | :--- |
| **$A$** | Nivel de concurrencia de captura | `1` trabajador (secuencial) | `4` trabajadores (`ThreadPoolExecutor`) | Evalúa ganancia en espera I/O respetando límites de cortesía por dominio |
| **$B$** | Motor de parseo DOM en `BeautifulSoup` | `html.parser` (estándar Python) | `lxml` (parser compilado en C) | Cuantifica aceleración al procesar catálogos y tablas HTML de $67\text{ KB}$ del SNIIM |
| **$C$** | Formato de almacenamiento analítico | `CSV` (texto plano UTF-8) | `Parquet` (`pyarrow` + Snappy) | Contrasta velocidad de serialización I/O y tamaño en disco entre capas |
| **$D$** *(en $2^{4-1}$)* | Estrategia de validación de calidad | Validación iterativa por fila | Validación vectorizada por lote (`pandera`) | Incorporado en fracción $2^{4-1}_{\text{IV}}$ con generador $I = ABCD$ ($D = ABC$) |

* **Rigor Experimental:** Se ejecutará primero el diseño factorial completo $2^3 = 8$ tratamientos con $r = 5$ réplicas independientes ($N = 40$ corridas ejecutadas en orden completamente aleatorizado y con calentamiento previo de caché) y posteriormente la fracción $2^{4-1}_{\text{IV}}$ ($8$ tratamientos $\times 5$ réplicas). Se estimará el modelo lineal con interacciones:
  $$Y_{ijkl} = \mu + \alpha_i + \beta_j + \gamma_k + (\alpha\beta)_{ij} + (\alpha\gamma)_{ik} + (\beta\gamma)_{jk} + (\alpha\beta\gamma)_{ijk} + \varepsilon_{ijkl}$$
  validando normalidad de residuos (Shapiro-Wilk), homocedasticidad (Levene), gráficas de Daniel/Pareto de efectos estandarizados y superficie de respuesta para fijar la configuración óptima del pipeline en producción.

### 3.3 Pregunta Analítica E3 — Estadística Multivariada: PCA y MANOVA (Unidad 5)

* **Enunciado Formal:**  
  *¿Existen diferencias multivariadas estadísticamente significativas ($\alpha = 0.05$) en el vector conjunto de desempeño agrocomercial y exposición climática entre los $g_1 = 4$ nodos mayoristas (`CDMX-Iztapalapa`, `Guadalajara`, `Monterrey`, `Occidente`) y los $g_2 = 4$ cultivos estratégicos de Colima, y cuántas componentes principales ortogonales logran sintetizar al menos el $80\%$ de la varianza total de las $p = 6$ variables continuas del observatorio?*
* **Estructura Multivariada ($p = 6$ Variables Numéricas Continuas, $g = 4$ Grupos):**
  1. $X_1$: `precio_mayorista_mxn_kg` — Precio mayorista mensual promedio ($\text{MXN/kg}$).
  2. $X_2$: `volatilidad_mensual_pct` — Volatilidad mensual de cotización ($\%$).
  3. $X_3$: `margen_comercial_mxn_kg` — Margen comercial neto descontando costo de origen y flete ($\text{MXN/kg}$).
  4. $X_4$: `temperatura_max_c` — Temperatura máxima media mensual en zona productora ($^\circ\text{C}$).
  5. $X_5$: `precipitacion_acumulada_mm` — Precipitación pluvial acumulada mensual ($\text{mm}$).
  6. $X_6$: `humedad_relativa_pct` — Humedad relativa media mensual en el corredor costero ($\%$).
* **Procedimiento Estadístico:**
  * **PCA:** Estandarización $Z = (X - \bar{X})S^{-1/2}$ sobre la matriz integrada Oro ($N = 768$ observaciones mensuales), verificación de adecuación muestral vía índice Kaiser-Meyer-Olkin ($\text{KMO} > 0.60$) y prueba de esfericidad de Bartlett ($p < 0.001$), retención de componentes por criterio de Kaiser ($\lambda_m > 1$) y varianza acumulada $\ge 80\%$, e interpretación geométrica mediante *biplot* de cargas y puntuaciones por cultivo y central.
  * **MANOVA:** Contraste simultáneo del vector de medias $\mathbf{H}_0: \boldsymbol{\mu}_1 = \boldsymbol{\mu}_2 = \boldsymbol{\mu}_3 = \boldsymbol{\mu}_4$ utilizando los cuatro estadísticos canónicos (**Lambda de Wilks** $\Lambda$, **Traza de Pillai**, **Hotelling-Lawley** y **Raíz Máxima de Roy**), evaluación de homogeneidad de matrices de covarianza (prueba $M$ de Box) y contrastes *post-hoc* con corrección de Bonferroni para identificar qué plazas maximizan el binomio margen–estabilidad.

---

## 4. Plan de Recopilación de Datos y Análisis Ético-Legal

### 4.1 Especificación Técnica de las Fuentes en Capa Bronce

| Atributo Técnico | Fuente 1: API Hidroclimática Abierta | Fuente 2: Portal Público de Precios Agrícolas |
| :--- | :--- | :--- |
| **Proveedor Oficial** | Open-Meteo (*Historical Weather API* y *Weather Forecast API*) | Secretaría de Economía — Sistema Nacional de Información e Integración de Mercados (**SNIIM**) |
| **Endpoints Consultados** | `https://archive-api.open-meteo.com/v1/archive` y `https://api.open-meteo.com/v1/forecast` | `http://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx` |
| **Método de Acceso** | Peticiones HTTP `GET` parametrizadas con `requests` y reintentos | Web Scraping ético mediante `ExtractorEtico` (`urllib.robotparser` + `BeautifulSoup`) y consolidación resiliente |
| **Formato de Origen y Destino** | Origen `JSON` $\rightarrow$ Persistencia cruda `CSV` UTF-8 en `data/bronce/` | Origen `HTML` (`text/html`, $\approx 67\text{ KB}$) $\rightarrow$ Persistencia cruda `CSV` UTF-8 en `data/bronce/` |
| **Cobertura Histórica (E0)** | **48 periodos mensuales** (`2022-11` a `2026-10`, $144$ filas: $48 \times 3$ zonas de Colima) | **48 periodos mensuales** (`2022-11` a `2026-10`, $768$ filas: $48 \times 4$ cultivos $\times 4$ centrales) |
| **Frecuencia de Actualización** | Diaria automatizada (`08:00 UTC` vía GitHub Actions `captura_diaria.yml`) | Diaria automatizada (`08:00 UTC` vía GitHub Actions `captura_diaria.yml`) |
| **Archivos Generados en Bronce** | `clima_historico_mensual.csv` y `clima_captura_diaria.csv` | `precios_agro_historico_mensual.csv` y `precios_captura_diaria.csv` |
| **Metadatos Obligatorios** | `fecha_captura` (`YYYY-MM-DD`) y `fuente_origen` | `fecha_captura` (`YYYY-MM-DD`) y `fuente_origen` (`sniim_web_verificado` / `sniim_respaldo_resiliente`) |

### 4.2 Auditoría Puntual de `robots.txt`, `Crawl-delay` y Términos de Uso

1. **Auditoría Técnica de `http://www.economia-sniim.gob.mx/robots.txt` (Verificada el 6 de noviembre de 2026):**  
   Al inspeccionar directamente el archivo `robots.txt` del servidor gubernamental del SNIIM (código HTTP `200 OK`), se identificaron las siguientes directivas exactas para `User-agent: *`:
   * Rutas restringidas (`Disallow`): `/Analisis/`, `/*.xls$`, `/2010/`, `/Sicia/`, `/Sicia2/`, `/SiciaAnt/`.
   * Rutas permitidas: El subdirectorio `/nuevo/Consultas/MercadosNacionales/...` **está explícitamente permitido** y el comentario raíz indica `# Allow: /`. Nuestro módulo [`extractor_web_precios.py`](../../extractores/extractor_web_precios.py) jamás descarga archivos `.xls` ni accede a `/Analisis/` o `/Sicia/`; además, invoca `ExtractorEtico.puede_extraer(url)` antes de cada petición.
   * `Crawl-delay`: El archivo `robots.txt` del SNIIM no fija un `Crawl-delay` explícito; sin embargo, [`ExtractorEtico`](../../extractores/base.py) impone por diseño una **pausa mínima obligatoria de `1.5` segundos** entre peticiones más **espera exponencial** ($1.5\text{ s}, 3.0\text{ s}, 6.0\text{ s}$) ante errores transitorios y un horario nocturno (`02:00 CST` / `08:00 UTC`) para no generar carga sobre la infraestructura pública.
2. **Identificación Académica Transparente (`User-Agent`):**  
   Todas las solicitudes HTTP se identifican con el encabezado institucional verificable:  
   `"TDL-Observatorio/1.0 (proyecto academico; contacto: carlos.tintos@tecnm.mx)"`.
3. **Licenciamiento y Términos de Uso:**
   * **Open-Meteo:** Publica datos meteorológicos basados en reanálisis ERA5 (Copernicus) y modelos NOAA/DWD bajo licencia **Creative Commons Attribution 4.0 International (CC BY 4.0)** para uso académico y no comercial gratuito, permitiendo hasta $10,000$ llamadas diarias (nuestro pipeline consume únicamente $6$ llamadas diarias, equivalente al $0.06\%$ de la cuota).
   * **SNIIM (Secretaría de Economía):** Información pública gubernamental de precios mayoristas divulgada con fines de transparencia e integración de mercados conforme a la política de Datos Abiertos de México, atribuida explícitamente en la columna `fuente_origen`.

### 4.3 Cumplimiento Legal (LFPDPPP) y Particionamiento en Capa Bronce

* **Garantía Estricta de Cero Datos Personales:** Conforme a la **Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)** y la **LGPDPPSO**, AgroPulse TDL procesa exclusivamente magnitudes físicas atmosféricas y cotizaciones agregadas por kilogramo a nivel plaza mayorista. Ninguna tabla en `data/bronce/`, `data/plata/`, `data/oro/` o `data/cuarentena/` almacena nombres de personas físicas, razones sociales individuales, números telefónicos, geolocalización de predios privados ni direcciones de correo de terceros.
* **Estrategia de Persistencia y Consolidación Idempotente en Bronce:** Los archivos históricos constituyen la línea base inmutable de $48$ meses, mientras que los archivos de captura diaria (`clima_captura_diaria.csv` y `precios_captura_diaria.csv`) acumulan cada corte diario particionado lógicamente mediante `fecha` y auditado con `fecha_captura` y `fuente_origen`, eliminando duplicados por clave natural para asegurar idempotencia cuando el flujo de GitHub Actions se ejecuta de forma programada o manual.

---

## 5. Arranque del Sistema de Calidad (PSP y Objetivos Medibles)

### 5.1 Bitácoras Individuales PSP y Registro Activo de Fiabilidad

Desde el día 1 de la etapa E0, ambos integrantes operan bajo disciplina **Personal Software Process (PSP)** y alternan el rol de *Quality Lead* (Oliver Vargas García funge como *Quality Lead* en E0 y Carlos Daniel Tintos Beltrán asumirá el relevo en E1):

* **Bitácoras PSP de Carlos Daniel Tintos Beltrán (*Data Engineer*):**
  * Registro de tiempos (6 sesiones del 2 al 6 de noviembre, $775\text{ min}$ netos): [`calidad/tiempo-carlos.csv`](../../calidad/tiempo-carlos.csv)
  * Registro de defectos (4 defectos técnicos detectados y corregidos en E0, $67\text{ min}$ de corrección): [`calidad/defectos-carlos.csv`](../../calidad/defectos-carlos.csv)
* **Bitácoras PSP de Oliver Vargas García (*Data Statistician & Quality Lead E0*):**
  * Registro de tiempos (6 sesiones del 2 al 6 de noviembre, $755\text{ min}$ netos): [`calidad/tiempo-oliver.csv`](../../calidad/tiempo-oliver.csv)
  * Registro de defectos (4 defectos analíticos/de validación corregidos en E0, $69\text{ min}$ de corrección): [`calidad/defectos-oliver.csv`](../../calidad/defectos-oliver.csv)
* **Bitácora Automatizada de Captura y Fiabilidad:**
  * Archivo activo poblado en cada corrida de extracción: [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv), registrando `timestamp_inicio`, `timestamp_fin`, `fuente`, `estado`, `registros_obtenidos`, `tiempo_segundos` y `mensaje_error`.

### 5.2 Definición Formal de los 3 Objetivos de Calidad Medibles del Proyecto

Para certificar el observatorio bajo los estándares **ISO/IEC 25010** (Calidad del Producto de Software), **ISO/IEC 25012** (Calidad de Datos) e **IEEE 730** (Plan SQA en E1), el equipo establece tres compromisos cuantitativos verificables desde E0 hasta E4:

| ID | Dimensión ISO | Objetivo Cuantitativo (Meta) | Fórmula / Regla de Medición | Instrumento de Evidencia |
| :---: | :--- | :--- | :--- | :--- |
| **OBJ-C1** | **Fiabilidad Operativa** *(ISO 25010: Disponibilidad)* | **Disponibilidad $A \ge 95.0\%$** en las ejecuciones diarias automatizadas de los extractores | $$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} \times 100$$ donde $\text{MTBF}$ es el tiempo medio entre fallos y $\text{MTTR}$ el tiempo medio de recuperación | Cálculo automático sobre [`calidad/bitacora_captura.csv`](../../calidad/bitacora_captura.csv) y historial de GitHub Actions |
| **OBJ-C2** | **Integridad de Datos** *(ISO 25012: Completitud y Exactitud)* | **Completitud $\ge 98.0\%$ en Capa Oro** con **$0\%$ de borrado silencioso** de registros | $$\text{Completitud} = \left(1 - \frac{\text{Celdas nulas en Oro}}{\text{Celdas totales en Oro}}\right) \times 100$$ Todo registro fuera de rango se desvía con motivo a `data/cuarentena/` | Contratos de datos `pandera`, conteo cruzado `Bronce = Oro + Cuarentena` y auditorías E2/E3 |
| **OBJ-C3** | **Mantenibilidad y Seguridad** *(ISO 25010: Analizabilidad y Confidencialidad)* | **Cobertura de pruebas $\ge 60.0\%$**, **$0$ errores de estilo** y **$0$ secretos o vulnerabilidades críticas** | Funciones modulares $\le 30$ líneas, validación continua en cada `push` y escaneo estático de credenciales y dependencias | Suite [`tests/test_extractores.py`](../../tests/test_extractores.py) (`pytest`), `ruff check .`, `gitleaks` y `pip-audit` |

