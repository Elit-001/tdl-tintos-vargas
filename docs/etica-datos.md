# Declaración de Ética, Legalidad, Gobernanza y Mitigación de Sesgos de Datos (E2)

* **Observatorio:** **AgroPulse TDL** (*Observatorio de Inteligencia Agrocomercial y Riesgo Climático del Pacífico*)
* **Equipo Responsable:** Carlos Daniel Tintos Beltrán (*Data Engineer*) y Oliver Vargas García (*Data Statistician & Quality Lead E2*)
* **Fecha de actualización:** 19 de noviembre de 2026

---

## 1. Marco de Legalidad y Licenciamiento por Fuente de Datos

**AgroPulse TDL** opera exclusivamente sobre fuentes públicas y de datos abiertos, respetando los términos de servicio, las directivas de exclusión de robots (`robots.txt`) y las licencias de atribución de cada proveedor. Ningún extractor realiza evasión de controles de acceso, *bypass* de CAPTCHAs ni recolección de información privada.

| Fuente del Observatorio | Dominio / Endpoint Oficial | Naturaleza Técnica | Licencia y Marco Legal | Cumplimiento Técnico en AgroPulse TDL |
| :--- | :--- | :--- | :--- | :--- |
| **Fuente 1: API Hidroclimática Open-Meteo** | `archive-api.open-meteo.com/v1/archive` y `api.open-meteo.com/v1/forecast` | API REST JSON abierta (Copernicus ERA5 / NOAA) | **Creative Commons Attribution 4.0 International (CC BY 4.0)** — Uso académico y de investigación permitido con atribución | Peticiones identificadas con `User-Agent` académico, pausa de cortesía y atribución explícita en `fuente_origen` y documentación. |
| **Fuente 2: Portal Público de Precios Mayoristas SNIIM-SE** | `economia-sniim.gob.mx` (Secretaría de Economía de México) | Catálogo y cotizaciones públicas mayoristas agrícolas | **Datos Abiertos del Gobierno de México (Libre Uso MX)** — Información estadística pública de interés nacional | Uso obligatorio de `ExtractorEtico` ([`extractores/base.py`](../extractores/base.py)) con lectura previa de `robots.txt`, pausa $\ge 1.5\text{ s}$ y *backoff* exponencial. |
| **Fuente 3: Red Geoespacial OpenStreetMap (E2)** | `overpass-api.de/api/interpreter` (Nodos de Colima) | API abierta Overpass QL de datos geoespaciales colaborativos | **Open Data Commons Open Database License (ODbL 1.0)** — Libre uso y derivación citando a `© OpenStreetMap contributors` | Consulta acotada al *bounding box* de Colima (`18.80,-104.45,19.35,-103.60`), `timeout` de $12\text{ s}$, un solo intento por corrida y catálogo de respaldo local para no saturar servidores comunitarios. |

---

## 2. Verificación Técnica de `robots.txt` y Extracción Ética (`ExtractorEtico`)

El módulo central [`extractores/base.py`](../extractores/base.py) implementa la clase `ExtractorEtico`, la cual impone cuatro salvaguardas técnicas antes de efectuar cualquier descarga HTTP:

1. **Identificación Académica Transparente (`User-Agent`):**
   * Todas las solicitudes envían la cabecera declarada en [`config.py`](../config.py):
     `TDL-Observatorio/1.0 (proyecto academico; contacto: carlos.tintos@tecnm.mx)`.
   * Jamás se suplanta la identidad de navegadores comerciales (*spoofing*) ni se rotan agentes falsos.
2. **Inspección Automática de `robots.txt` (`RobotFileParser`):**
   * Al instanciar `ExtractorEtico`, el método `_cargar_robots()` descarga `<url_base>/robots.txt` y evalúa `can_fetch(user_agent, url)`.
   * Si el portal declara la directiva `Crawl-delay`, el extractor ajusta automáticamente `self.pausa_efectiva = max(self.pausa_minima, float(demora_sitio))`. Si una ruta está restringida (`Disallow`), el método `obtener_pagina()` aborta inmediatamente lanzando `PermissionError`.
3. **Limitación de Tasa (*Rate-Limiting*) y Espera Exponencial (*Exponential Backoff*):**
   * Se respeta una pausa mínima obligatoria de **$1.5\text{ segundos}$** entre peticiones consecutivas.
   * Ante errores transitorios ($5\text{xx}$ o *timeout*), el sistema ejecuta un máximo de $3$ intentos con espera exponencial ($1.5\text{ s} \rightarrow 3.0\text{ s} \rightarrow 6.0\text{ s}$) y en caso de indisponibilidad externa activa el respaldo determinista sin bombardear al servidor origen.
4. **Inmutabilidad y Trazabilidad Criptográfica (`SHA-256`):**
   * Cada archivo depositado en [`data/bronce/`](../data/bronce) genera de forma automática su ficha `<archivo>.meta.json` con su firma `SHA-256` y `timestamp_captura` en UTC, propagando dicho hash hasta las $5$ columnas `linaje_*` de la Capa Oro.

---

## 3. Privacidad y Protección de Datos Personales (Cero PII)

En estricto apego a la **Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)** y a las reglas del proyecto integrador:

* **Ausencia Total de PII (*Personally Identifiable Information*):** Ninguna tabla de las capas `bronce`, `plata`, `cuarentena` u `oro` almacena nombres de personas físicas, razones sociales privadas de agricultores individuales, números telefónicos, correos electrónicos particulares, CURP, RFC ni coordenadas de domicilios privados.
* **Anonimización y Agregación Espacial:**
  * Los nodos productores en [`data/bronce/nodos_geoespaciales_colima.csv`](../data/bronce/nodos_geoespaciales_colima.csv) representan **centroides municipales públicos** de las zonas agroproductoras de Colima (`Tecomán`, `Armería`, `Manzanillo` y `Coquimatlán`).
  * Los nodos compradores representan **puntos logísticos corporativos públicos** (*Walmart Colima*, *Empacadora San José*, *Agroindustriales de Colima* y *Limones Prolim*) identificados mediante códigos genéricos (`COMP-01` a `COMP-04`).
  * La entrevista de campo documentada en E0 se realizó bajo consentimiento informado y anonimización completa del productor entrevistado.

---

## 4. Análisis y Mitigación de Sesgos en los Datos

Un observatorio agrocomercial responsable debe reconocer y mitigar los sesgos estructurales presentes en los datos públicos del sector primario:

1. **Sesgo de Cobertura Geográfica Rural vs. Urbana:**
   * *Riesgo:* Las estaciones meteorológicas físicas y los nodos registrados en OpenStreetMap suelen concentrarse en zonas urbanas (Colima capital y puerto de Manzanillo), subrepresentando microclimas agrícolas como Coquimatlán o el valle agrícola de Armería.
   * *Mitigación en AgroPulse TDL:* Combinamos la malla satelital continua de reanálisis ERA5 de Open-Meteo (resolución espacial en coordenadas exactas de cada valle agrícola) con la reproyección métrica **`EPSG:32613` (UTM Zona 13N)** y un factor de sinuosidad vial ($1.24$) calibrado para las carreteras estatales de Colima.
2. **Sesgo de Asimetría de Escala (Grandes Empacadoras vs. Pequeños Productores):**
   * *Riesgo:* Los precios reportados en el SNIIM reflejan cotizaciones de bodegas mayoristas por tonelada; si un pequeño productor de $100\text{ kg}$ intenta vender individualmente a ese precio, el costo fijo de maniobra y flete ($\approx \$220\text{ MXN}$ fijos + $\$18.50/\text{km}$) absorbe su utilidad, empujándolo hacia el *coyotaje* local.
   * *Mitigación en AgroPulse TDL:* El modelo de negocio de **Marketplace de Intermediación Inteligente (*Brokerage*)** y el diseño experimental factorial $2^3$ / $2^{4-1}$ ([`laboratorio/E2_diseno_experimentos.ipynb`](../laboratorio/E2_diseno_experimentos.ipynb)) demuestran cuantitativamente cómo la **consolidación en pools de $400\text{ kg}$ ($4$ agricultores $\times 100\text{ kg}$)** diluye el costo fijo de maniobra en un $75\%$ y democratiza el acceso a tarifas de comprador ancla para el pequeño productor colimense.
3. **Sesgo de Supervivencia y Datos Faltantes:**
   * *Mitigación:* La puerta de calidad [`pipeline/puerta_calidad.py`](../pipeline/puerta_calidad.py) prohíbe el borrado silencioso ($0\%$ pérdida de registros), aislando cualquier anomalía en `data/cuarentena/` con su `motivo_rechazo` auditable bajo la norma **ISO/IEC 25012**.

