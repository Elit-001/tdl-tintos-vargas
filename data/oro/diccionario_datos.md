# Diccionario de Datos — Capa Oro (`dataset_analitico.csv` y `rutas_flete_colima.csv`)

* **Total de registros analíticos (E1-E2):** `768` filas (`48` meses × `4` cultivos × `4` centrales)
* **Total de atributos en `dataset_analitico.csv`:** `41` columnas (incluye 5 columnas de linaje SHA-256)
* **Estándar de calidad aplicado:** ISO/IEC 25012 (Completitud, Exactitud, Consistencia y Trazabilidad)

## 1. Tabla Principal: `dataset_analitico.csv`

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `periodo_mensual` | `str` | Año-Mes ISO (YYYY-MM) | 100.0% | Valores: 2022-11, 2022-12, 2023-01 | Clave temporal de integración |
| `cultivo` | `str` | Texto categórico | 100.0% | Valores: Aguacate Hass, Limón Mexicano, Papaya Maradol | Cultivo agrocomercial de Colima |
| `central_abasto` | `str` | Texto categórico | 100.0% | Valores: CDMX-Iztapalapa, Guadalajara, Monterrey | Mercado mayorista nacional de destino |
| `variedad_sniim` | `str` | Texto | 100.0% | Valores: Aguacate Hass - Primera, Limón c/semilla # 2 - Primera, Papaya M | Denominación comercial oficial en catálogo SNIIM |
| `precio_mayorista_mxn_kg` | `float64` | MXN / kg | 100.0% | [11.61, 94.59] (media=32.61) | Precio mayorista mensual limpio |
| `volatilidad_mensual_pct` | `float64` | Porcentaje (%) | 100.0% | [6.18, 20.89] (media=13.88) | Coeficiente de variación mensual |
| `costo_logistico_mxn_kg` | `float64` | MXN / kg | 100.0% | [1.35, 6.64] (media=3.61) | Flete refrigerado/ventilado estimado |
| `margen_comercial_mxn_kg` | `float64` | MXN / kg | 100.0% | [1.32, 50.49] (media=12.79) | Margen neto descontando origen y flete |
| `margen_comercial_pct` | `float64` | Porcentaje (%) | 100.0% | [8.06, 54.09] (media=35.99) | Margen comercial neto relativo |
| `fecha_captura_precios` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-20 | Indicador o atributo (fecha_captura_precios) |
| `fuente_origen_precios` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: sniim_web_verificado | Indicador o atributo (fuente_origen_precios) |
| `es_atipico_precio` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_atipico_precio) |
| `precio_mayorista_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.43) | Indicador o atributo (precio_mayorista_mxn_kg_norm) |
| `volatilidad_mensual_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador o atributo (volatilidad_mensual_pct_norm) |
| `costo_logistico_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.43) | Indicador o atributo (costo_logistico_mxn_kg_norm) |
| `margen_comercial_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.46) | Indicador o atributo (margen_comercial_mxn_kg_norm) |
| `margen_comercial_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.58) | Indicador o atributo (margen_comercial_pct_norm) |
| `categoria_precio` | `str` | Ordinal (Bajo/Medio/Alto) | 100.0% | Valores: Bajo, Medio, Alto | Discretización por terciles |
| `nivel_volatilidad` | `str` | Ordinal (Estable/Moderada/Alta) | 100.0% | Valores: Moderada, Alta, Estable | Riesgo de cotización |
| `zona_agricola` | `str` | Texto categórico | 100.0% | Valores: Tecomán, Armería, Manzanillo | Región agroproductora de origen en Colima |
| `latitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.91, 19.05] (media=18.95) | Indicador o atributo (latitud) |
| `longitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.31, -103.87] (media=-104.00) | Indicador o atributo (longitud) |
| `temperatura_max_c` | `float64` | Grados Celsius (°C) | 100.0% | [28.06, 33.56] (media=30.43) | Temperatura máxima media mensual |
| `temperatura_media_c` | `float64` | Grados Celsius (°C) | 100.0% | [22.85, 29.57] (media=26.16) | Temperatura promedio mensual |
| `precipitacion_acumulada_mm` | `float64` | Milímetros (mm) | 100.0% | [0.00, 385.91] (media=74.64) | Lluvia acumulada mensual |
| `evapotranspiracion_mm` | `float64` | Milímetros (mm) | 100.0% | [102.23, 171.73] (media=132.93) | Evapotranspiración FAO ET0 acumulada |
| `humedad_relativa_pct` | `float64` | Porcentaje (%) | 100.0% | [61.68, 90.10] (media=77.52) | Humedad relativa media mensual |
| `fecha_captura_clima` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-20 | Indicador o atributo (fecha_captura_clima) |
| `fuente_origen_clima` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: open_meteo_archive_api | Indicador o atributo (fuente_origen_clima) |
| `es_atipico_clima` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_atipico_clima) |
| `temperatura_max_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.42) | Indicador o atributo (temperatura_max_c_norm) |
| `temperatura_media_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador o atributo (temperatura_media_c_norm) |
| `precipitacion_acumulada_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.23) | Indicador o atributo (precipitacion_acumulada_mm_norm) |
| `evapotranspiracion_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.44) | Indicador o atributo (evapotranspiracion_mm_norm) |
| `humedad_relativa_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.51) | Indicador o atributo (humedad_relativa_pct_norm) |
| `linaje_sha256_clima_bronce` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: 8b48c8a747c725d760c066c8d9ef9b3c64ec4d05c2fb9ccc58aa40fe2b48c546 | Indicador o atributo (linaje_sha256_clima_bronce) |
| `linaje_id_registro` | `str` | Identificador único | 100.0% | Valores: ORO-ANL-00001, ORO-ANL-00002, ORO-ANL-00003 | ID determinista del registro en Oro |
| `linaje_archivo_bronce` | `str` | Nombre de archivo | 100.0% | Valores: precios_agro_historico_mensual.csv | Archivo origen en data/bronce/ |
| `linaje_sha256_bronce` | `str` | Hash SHA-256 (64 hex) | 100.0% | Valores: fefd83ebc139afc1948b73a9b03cc2b63ef09880bc6fb60671af32f463ecbff9 | Firma criptográfica desde .meta.json |
| `linaje_fecha_ingesta_utc` | `str` | ISO-8601 UTC | 100.0% | Valores: 2026-11-20T16:46:05.673760+00:00 | Timestamp de captura en Capa Bronce |
| `linaje_fuente` | `str` | Texto identificador | 100.0% | Valores: sniim_web_verificado | Fuente de extracción verificada |

## 2. Tabla Geoespacial y Logística (E2): `rutas_flete_colima.csv`

* **Total de rutas productor-comprador ancla:** `16` rutas (`4` productores × `4` compradores en Colima, reproyección `EPSG:4326` -> `EPSG:32613` UTM Zona 13N)

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id_ruta` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: PROD-01_COMP-01, PROD-01_COMP-02, PROD-01_COMP-03 | Indicador o atributo (id_ruta) |
| `nodo_productor` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: Tecomán, Armería, Manzanillo | Indicador o atributo (nodo_productor) |
| `municipio_origen` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: Tecomán, Armería, Manzanillo | Indicador o atributo (municipio_origen) |
| `cultivo_origen` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: Limón Mexicano, Papaya Maradol, Plátano Chiapas | Indicador o atributo (cultivo_origen) |
| `lat_productor` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.91, 19.21] (media=19.03) | Indicador o atributo (lat_productor) |
| `lon_productor` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.32, -103.81] (media=-103.99) | Indicador o atributo (lon_productor) |
| `comprador_ancla` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: Walmart Colima, Empacadora San José, Agroindustriales de Colima | Indicador o atributo (comprador_ancla) |
| `municipio_destino` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: Colima, Tecomán, Villa de Álvarez | Indicador o atributo (municipio_destino) |
| `lat_comprador` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.92, 19.26] (media=19.09) | Indicador o atributo (lat_comprador) |
| `lon_comprador` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-103.96, -103.72] (media=-103.83) | Indicador o atributo (lon_comprador) |
| `lote_consolidado_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [400.00, 400.00] (media=400.00) | Indicador o atributo (lote_consolidado_kg) |
| `distancia_lineal_km` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.80, 67.26] (media=30.48) | Indicador o atributo (distancia_lineal_km) |
| `distancia_vial_km` | `float64` | Escala [0, 1] / Metadato | 100.0% | [1.20, 83.40] (media=37.81) | Indicador o atributo (distancia_vial_km) |
| `costo_flete_lote_400kg_mxn` | `float64` | Escala [0, 1] / Metadato | 100.0% | [242.20, 1762.90] (media=919.49) | Indicador o atributo (costo_flete_lote_400kg_mxn) |
| `costo_flete_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.61, 4.41] (media=2.30) | Indicador o atributo (costo_flete_mxn_kg) |
| `precio_compra_productor_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [12.94, 48.72] (media=24.51) | Indicador o atributo (precio_compra_productor_mxn_kg) |
| `precio_venta_comprador_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [16.09, 61.77] (media=30.76) | Indicador o atributo (precio_venta_comprador_mxn_kg) |
| `spread_neto_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-0.95, 11.83] (media=3.96) | Indicador o atributo (spread_neto_mxn_kg) |
| `margen_lote_400kg_mxn` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-380.00, 4732.00] (media=1583.25) | Indicador o atributo (margen_lote_400kg_mxn) |
| `es_ruta_optima` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_ruta_optima) |
| `linaje_id_registro` | `str` | Identificador único | 100.0% | Valores: GEO-E2-00001, GEO-E2-00002, GEO-E2-00003 | ID determinista del registro en Oro |
| `linaje_archivo_bronce` | `str` | Nombre de archivo | 100.0% | Valores: nodos_geoespaciales_colima.csv | Archivo origen en data/bronce/ |
| `linaje_sha256_bronce` | `str` | Hash SHA-256 (64 hex) | 100.0% | Valores: 7125029199332d6737fa089c00755dfe9882e827376df4d060ef684747fbc251 | Firma criptográfica desde .meta.json |
| `linaje_fecha_ingesta_utc` | `str` | ISO-8601 UTC | 100.0% | Valores: 2026-11-20T16:46:06.242856+00:00 | Timestamp de captura en Capa Bronce |
| `linaje_fuente` | `str` | Texto identificador | 100.0% | Valores: osm_catalogo_referencia_colima | Fuente de extracción verificada |
