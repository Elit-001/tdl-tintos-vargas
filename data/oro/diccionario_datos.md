# Diccionario de Datos — Capa Oro y Dataset Publicado (`E1-E3`)

* **Total de registros analíticos:** `960` filas (`48` meses × `4` cultivos × `5` centrales)
* **Atributos en `dataset_analitico.csv`:** `41` columnas (con linaje SHA-256)
* **Estándar de calidad:** ISO/IEC 25012 + Licencia Abierta `CC BY 4.0` en `data/publicado/`

## 1. Tabla Principal: `dataset_analitico.csv`

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `periodo_mensual` | `object` | Año-Mes ISO (YYYY-MM) | 100.0% | Valores: 2022-11, 2022-12, 2023-01 | Clave temporal de integración |
| `cultivo` | `object` | Texto categórico | 100.0% | Valores: Aguacate Hass, Limón Mexicano, Papaya Maradol | Cultivo agrocomercial de Colima |
| `central_abasto` | `object` | Texto categórico | 100.0% | Valores: CDMX-Iztapalapa, Colima, Guadalajara | Mercado mayorista nacional de destino |
| `variedad_sniim` | `object` | Texto | 100.0% | Valores: Aguacate Hass - Primera, Aguacate Hass - Calidad extra, Limón c/ | Denominación comercial oficial en catálogo SNIIM |
| `precio_mayorista_mxn_kg` | `float64` | MXN / kg | 100.0% | [7.71, 104.06] (media=30.37) | Precio mayorista mensual limpio |
| `volatilidad_mensual_pct` | `float64` | Porcentaje (%) | 100.0% | [1.80, 24.68] (media=7.49) | Coeficiente de variación mensual |
| `costo_logistico_mxn_kg` | `float64` | MXN / kg | 100.0% | [0.65, 6.54] (media=3.29) | Flete refrigerado/ventilado estimado |
| `margen_comercial_mxn_kg` | `float64` | MXN / kg | 100.0% | [-5.01, 69.68] (media=14.00) | Margen neto descontando origen y flete |
| `margen_comercial_pct` | `float64` | Porcentaje (%) | 100.0% | [-14.18, 82.40] (media=42.30) | Margen comercial neto relativo |
| `fecha_captura_precios` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-26 | Indicador o atributo (fecha_captura_precios) |
| `fuente_origen_precios` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: sniim_gob_mx_historico_real | Indicador o atributo (fuente_origen_precios) |
| `es_atipico_precio` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_atipico_precio) |
| `precio_mayorista_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.41) | Indicador o atributo (precio_mayorista_mxn_kg_norm) |
| `volatilidad_mensual_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.33) | Indicador o atributo (volatilidad_mensual_pct_norm) |
| `costo_logistico_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.45) | Indicador o atributo (costo_logistico_mxn_kg_norm) |
| `margen_comercial_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.44) | Indicador o atributo (margen_comercial_mxn_kg_norm) |
| `margen_comercial_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.58) | Indicador o atributo (margen_comercial_pct_norm) |
| `categoria_precio` | `object` | Ordinal (Bajo/Medio/Alto) | 100.0% | Valores: Bajo, Medio, Alto | Discretización por terciles |
| `nivel_volatilidad` | `object` | Ordinal (Estable/Moderada/Alta) | 100.0% | Valores: Estable, Alta, Moderada | Riesgo de cotización |
| `zona_agricola` | `object` | Texto categórico | 100.0% | Valores: Comala, Tecomán, Armería | Región agroproductora de origen en Colima |
| `latitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.91, 19.33] (media=19.06) | Indicador o atributo (latitud) |
| `longitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.32, -103.76] (media=-103.98) | Indicador o atributo (longitud) |
| `temperatura_max_c` | `float64` | Grados Celsius (°C) | 100.0% | [27.77, 34.52] (media=30.54) | Temperatura máxima media mensual |
| `temperatura_media_c` | `float64` | Grados Celsius (°C) | 100.0% | [21.66, 29.57] (media=25.67) | Temperatura promedio mensual |
| `precipitacion_acumulada_mm` | `float64` | Milímetros (mm) | 100.0% | [0.00, 385.91] (media=74.62) | Lluvia acumulada mensual |
| `evapotranspiracion_mm` | `float64` | Milímetros (mm) | 100.0% | [102.26, 194.65] (media=134.50) | Evapotranspiración FAO ET0 acumulada |
| `humedad_relativa_pct` | `float64` | Porcentaje (%) | 100.0% | [41.07, 90.10] (media=74.20) | Humedad relativa media mensual |
| `fecha_captura_clima` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-26 | Indicador o atributo (fecha_captura_clima) |
| `fuente_origen_clima` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: open_meteo_archive_api | Indicador o atributo (fuente_origen_clima) |
| `es_atipico_clima` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_atipico_clima) |
| `temperatura_max_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.42) | Indicador o atributo (temperatura_max_c_norm) |
| `temperatura_media_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador o atributo (temperatura_media_c_norm) |
| `precipitacion_acumulada_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.24) | Indicador o atributo (precipitacion_acumulada_mm_norm) |
| `evapotranspiracion_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.42) | Indicador o atributo (evapotranspiracion_mm_norm) |
| `humedad_relativa_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador o atributo (humedad_relativa_pct_norm) |
| `linaje_sha256_clima_bronce` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: 76d0e315c8cfb617c6dbbdf3cc2686d5c1cf810a3d3ad05bbe471ef3a11c7a15 | Indicador o atributo (linaje_sha256_clima_bronce) |
| `linaje_id_registro` | `object` | Identificador único | 100.0% | Valores: ORO-ANL-00001, ORO-ANL-00002, ORO-ANL-00003 | ID determinista del registro en Oro |
| `linaje_archivo_bronce` | `object` | Nombre de archivo | 100.0% | Valores: precios_agro_historico_mensual.csv | Archivo origen en data/bronce/ |
| `linaje_sha256_bronce` | `object` | Hash SHA-256 (64 hex) | 100.0% | Valores: 9479b1f96304c14886392918008d19c18846961f7faae677883dcb4c85054d80 | Firma criptográfica desde .meta.json |
| `linaje_fecha_ingesta_utc` | `object` | ISO-8601 UTC | 100.0% | Valores: 2026-11-26T22:48:42.086708+00:00 | Timestamp de captura en Capa Bronce |
| `linaje_fuente` | `object` | Texto identificador | 100.0% | Valores: sniim_gob_mx_historico_real | Fuente de extracción verificada |

## 2. Tabla Geoespacial y Logística (E2): `rutas_flete_colima.csv`

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id_ruta` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: PROD-01_COMP-01, PROD-01_COMP-02, PROD-01_COMP-03 | Indicador o atributo (id_ruta) |
| `nodo_productor` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: Colima, Villa de Álvarez, Comala | Indicador o atributo (nodo_productor) |
| `municipio_origen` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: Colima, Villa de Álvarez, Comala | Indicador o atributo (municipio_origen) |
| `cultivo_origen` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: Limón Mexicano, Papaya Maradol, Aguacate Hass | Indicador o atributo (cultivo_origen) |
| `lat_productor` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.91, 19.39] (media=19.17) | Indicador o atributo (lat_productor) |
| `lon_productor` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.32, -103.60] (media=-103.86) | Indicador o atributo (lon_productor) |
| `comprador_ancla` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: Mercado Constitución Colima, Walmart Colima, Soriana Híper Villa | Indicador o atributo (comprador_ancla) |
| `municipio_destino` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: Colima, Villa de Álvarez, Tecomán | Indicador o atributo (municipio_destino) |
| `lat_comprador` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.92, 19.27] (media=19.12) | Indicador o atributo (lat_comprador) |
| `lon_comprador` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.33, -103.72] (media=-103.89) | Indicador o atributo (lon_comprador) |
| `lote_consolidado_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [900.00, 1500.00] (media=1125.00) | Indicador o atributo (lote_consolidado_kg) |
| `distancia_lineal_km` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.80, 80.06] (media=33.21) | Indicador o atributo (distancia_lineal_km) |
| `distancia_vial_km` | `float64` | Escala [0, 1] / Metadato | 100.0% | [1.50, 117.75] (media=46.47) | Indicador o atributo (distancia_vial_km) |
| `tiempo_traslado_min` | `float64` | Escala [0, 1] / Metadato | 100.0% | [4.00, 95.30] (media=42.41) | Indicador o atributo (tiempo_traslado_min) |
| `indice_sinuosidad_real` | `float64` | Escala [0, 1] / Metadato | 100.0% | [1.10, 1.99] (media=1.40) | Indicador o atributo (indice_sinuosidad_real) |
| `costo_flete_lote_400kg_mxn` | `float64` | Escala [0, 1] / Metadato | 100.0% | [247.75, 2398.38] (media=1079.76) | Indicador o atributo (costo_flete_lote_400kg_mxn) |
| `costo_flete_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.17, 2.28] (media=0.97) | Indicador o atributo (costo_flete_mxn_kg) |
| `precio_compra_productor_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [14.28, 43.68] (media=24.36) | Indicador o atributo (precio_compra_productor_mxn_kg) |
| `precio_venta_comprador_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [17.60, 55.90] (media=30.63) | Indicador o atributo (precio_venta_comprador_mxn_kg) |
| `spread_neto_mxn_kg` | `float64` | Escala [0, 1] / Metadato | 100.0% | [1.32, 11.83] (media=5.30) | Indicador o atributo (spread_neto_mxn_kg) |
| `margen_lote_400kg_mxn` | `float64` | Escala [0, 1] / Metadato | 100.0% | [1320.00, 11830.00] (media=5300.67) | Indicador o atributo (margen_lote_400kg_mxn) |
| `es_ruta_optima` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador o atributo (es_ruta_optima) |
| `linaje_id_registro` | `object` | Identificador único | 100.0% | Valores: GEO-E2-00001, GEO-E2-00002, GEO-E2-00003 | ID determinista del registro en Oro |
| `linaje_archivo_bronce` | `object` | Nombre de archivo | 100.0% | Valores: nodos_geoespaciales_colima.csv | Archivo origen en data/bronce/ |
| `linaje_sha256_bronce` | `object` | Hash SHA-256 (64 hex) | 100.0% | Valores: 77f9bd4fdd08e14c19b5f8cc0a0ddad0c017ecc232fb7fec95a7fdc83e14a2b8 | Firma criptográfica desde .meta.json |
| `linaje_fecha_ingesta_utc` | `object` | ISO-8601 UTC | 100.0% | Valores: 2026-11-26T22:48:46.338900+00:00 | Timestamp de captura en Capa Bronce |
| `linaje_fuente` | `object` | Texto identificador | 100.0% | Valores: osm_catalogo_estatal_colima | Fuente de extracción verificada |

## 3. Dataset Curado Abierto para Terceros (E3): `data/publicado/agropulse_colima_curado.csv`

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `periodo_mensual` | `object` | Año-Mes ISO (YYYY-MM) | 100.0% | Valores: 2022-11, 2022-12, 2023-01 | Clave temporal de integración |
| `cultivo` | `object` | Texto categórico | 100.0% | Valores: Aguacate Hass, Limón Mexicano, Papaya Maradol | Cultivo agrocomercial de Colima |
| `variedad_sniim` | `object` | Texto | 100.0% | Valores: Aguacate Hass - Primera, Aguacate Hass - Calidad extra, Limón c/ | Denominación comercial oficial en catálogo SNIIM |
| `zona_agricola` | `object` | Texto categórico | 100.0% | Valores: Comala, Tecomán, Armería | Región agroproductora de origen en Colima |
| `central_abasto` | `object` | Texto categórico | 100.0% | Valores: CDMX-Iztapalapa, Colima, Guadalajara | Mercado mayorista nacional de destino |
| `precio_mayorista_mxn_kg` | `float64` | MXN / kg | 100.0% | [7.71, 104.06] (media=30.37) | Precio mayorista mensual limpio |
| `volatilidad_mensual_pct` | `float64` | Porcentaje (%) | 100.0% | [1.80, 24.68] (media=7.49) | Coeficiente de variación mensual |
| `costo_logistico_mxn_kg` | `float64` | MXN / kg | 100.0% | [0.65, 6.54] (media=3.29) | Flete refrigerado/ventilado estimado |
| `margen_comercial_mxn_kg` | `float64` | MXN / kg | 100.0% | [-5.01, 69.68] (media=14.00) | Margen neto descontando origen y flete |
| `margen_comercial_pct` | `float64` | Porcentaje (%) | 100.0% | [-14.18, 82.40] (media=42.30) | Margen comercial neto relativo |
| `categoria_precio` | `object` | Ordinal (Bajo/Medio/Alto) | 100.0% | Valores: Bajo, Medio, Alto | Discretización por terciles |
| `nivel_volatilidad` | `object` | Ordinal (Estable/Moderada/Alta) | 100.0% | Valores: Estable, Alta, Moderada | Riesgo de cotización |
| `temperatura_max_c` | `float64` | Grados Celsius (°C) | 100.0% | [27.77, 34.52] (media=30.54) | Temperatura máxima media mensual |
| `temperatura_media_c` | `float64` | Grados Celsius (°C) | 100.0% | [21.66, 29.57] (media=25.67) | Temperatura promedio mensual |
| `precipitacion_acumulada_mm` | `float64` | Milímetros (mm) | 100.0% | [0.00, 385.91] (media=74.62) | Lluvia acumulada mensual |
| `evapotranspiracion_mm` | `float64` | Milímetros (mm) | 100.0% | [102.26, 194.65] (media=134.50) | Evapotranspiración FAO ET0 acumulada |
| `humedad_relativa_pct` | `float64` | Porcentaje (%) | 100.0% | [41.07, 90.10] (media=74.20) | Humedad relativa media mensual |
| `comprador_ancla_optimo_colima` | `object` | Texto categórico | 100.0% | Valores: Walmart Colima, Bodega Aurrera Tecomán, Soriana Híper Manzanillo | Comprador B2B óptimo en Colima |
| `distancia_vial_optima_km` | `float64` | Kilómetros (km) | 100.0% | [1.84, 13.44] (media=9.78) | Distancia vial UTM 13N óptima |
| `flete_local_400kg_mxn_kg` | `float64` | MXN / kg | 100.0% | [0.17, 0.39] (media=0.30) | Costo logístico local en pool de 400 kg |
| `spread_brokerage_colima_mxn_kg` | `float64` | MXN / kg | 100.0% | [3.48, 11.83] (media=5.77) | Margen neto B2B local optimizado |
| `linaje_sha256_clima_bronce` | `object` | Escala [0, 1] / Metadato | 100.0% | Valores: 76d0e315c8cfb617c6dbbdf3cc2686d5c1cf810a3d3ad05bbe471ef3a11c7a15 | Indicador o atributo (linaje_sha256_clima_bronce) |
| `linaje_id_registro` | `object` | Identificador único | 100.0% | Valores: PUB-E3-00001, PUB-E3-00002, PUB-E3-00003 | ID determinista del registro en Oro |
| `linaje_archivo_bronce` | `object` | Nombre de archivo | 100.0% | Valores: precios_agro_historico_mensual.csv | Archivo origen en data/bronce/ |
| `linaje_sha256_bronce` | `object` | Hash SHA-256 (64 hex) | 100.0% | Valores: 9479b1f96304c14886392918008d19c18846961f7faae677883dcb4c85054d80 | Firma criptográfica desde .meta.json |
| `linaje_fecha_ingesta_utc` | `object` | ISO-8601 UTC | 100.0% | Valores: 2026-11-26T22:48:42.086708+00:00 | Timestamp de captura en Capa Bronce |
| `linaje_fuente` | `object` | Texto identificador | 100.0% | Valores: sniim_gob_mx_historico_real | Fuente de extracción verificada |
