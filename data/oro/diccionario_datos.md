# Diccionario de Datos — Capa Oro (`dataset_analitico.csv`)

* **Total de registros consolidados:** `768` filas (`48` meses × `4` cultivos × `4` centrales)
* **Total de atributos:** `35` columnas
* **Estándar de calidad aplicado:** ISO/IEC 25012 (Completitud, Exactitud y Consistencia)

| Columna | Tipo Python | Unidad / Escala | Completitud | Dominio / Rango Observado | Descripción |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `periodo_mensual` | `str` | Año-Mes ISO (YYYY-MM) | 100.0% | Valores: 2022-11, 2022-12, 2023-01 | Clave temporal de integración |
| `cultivo` | `str` | Texto categórico | 100.0% | Valores: Aguacate Hass, Limón Mexicano, Papaya Maradol | Cultivo agrocomercial de Colima |
| `central_abasto` | `str` | Texto categórico | 100.0% | Valores: CDMX-Iztapalapa, Guadalajara, Monterrey | Mercado mayorista nacional de destino |
| `variedad_sniim` | `str` | Texto | 100.0% | Valores: Aguacate Hass - Primera, Limón c/semilla # 2 - Primera, Papaya Maradol - Primera | Denominación comercial oficial en catálogo SNIIM |
| `precio_mayorista_mxn_kg` | `float64` | MXN / kg | 100.0% | [11.61, 94.59] (media=32.61) | Precio mayorista mensual limpio |
| `volatilidad_mensual_pct` | `float64` | Porcentaje (%) | 100.0% | [6.18, 20.89] (media=13.88) | Coeficiente de variación mensual |
| `costo_logistico_mxn_kg` | `float64` | MXN / kg | 100.0% | [1.35, 6.64] (media=3.61) | Flete refrigerado/ventilado estimado |
| `margen_comercial_mxn_kg` | `float64` | MXN / kg | 100.0% | [1.32, 50.49] (media=12.79) | Margen neto descontando origen y flete |
| `margen_comercial_pct` | `float64` | Porcentaje (%) | 100.0% | [8.06, 54.09] (media=35.99) | Margen comercial neto relativo |
| `fecha_captura_precios` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-12 | Indicador derivado (fecha_captura_precios) |
| `fuente_origen_precios` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: sniim_web_verificado | Indicador derivado (fuente_origen_precios) |
| `es_atipico_precio` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador derivado (es_atipico_precio) |
| `precio_mayorista_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.43) | Indicador derivado (precio_mayorista_mxn_kg_norm) |
| `volatilidad_mensual_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador derivado (volatilidad_mensual_pct_norm) |
| `costo_logistico_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.43) | Indicador derivado (costo_logistico_mxn_kg_norm) |
| `margen_comercial_mxn_kg_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.46) | Indicador derivado (margen_comercial_mxn_kg_norm) |
| `margen_comercial_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.58) | Indicador derivado (margen_comercial_pct_norm) |
| `categoria_precio` | `str` | Ordinal (Bajo/Medio/Alto) | 100.0% | Valores: Bajo, Medio, Alto | Discretización por terciles |
| `nivel_volatilidad` | `str` | Ordinal (Estable/Moderada/Alta) | 100.0% | Valores: Moderada, Alta, Estable | Riesgo de cotización |
| `zona_agricola` | `str` | Texto categórico | 100.0% | Valores: Tecomán, Armería, Manzanillo | Región agroproductora de origen en Colima |
| `latitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [18.91, 19.05] (media=18.95) | Indicador derivado (latitud) |
| `longitud` | `float64` | Escala [0, 1] / Metadato | 100.0% | [-104.31, -103.87] (media=-104.00) | Indicador derivado (longitud) |
| `temperatura_max_c` | `float64` | Grados Celsius (°C) | 100.0% | [28.06, 33.56] (media=30.43) | Temperatura máxima media mensual |
| `temperatura_media_c` | `float64` | Grados Celsius (°C) | 100.0% | [22.85, 29.57] (media=26.16) | Temperatura promedio mensual |
| `precipitacion_acumulada_mm` | `float64` | Milímetros (mm) | 100.0% | [0.00, 385.91] (media=74.64) | Lluvia acumulada mensual |
| `evapotranspiracion_mm` | `float64` | Milímetros (mm) | 100.0% | [102.23, 171.73] (media=132.93) | Evapotranspiración FAO ET0 acumulada |
| `humedad_relativa_pct` | `float64` | Porcentaje (%) | 100.0% | [61.68, 90.10] (media=77.52) | Humedad relativa media mensual |
| `fecha_captura_clima` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: 2026-11-12 | Indicador derivado (fecha_captura_clima) |
| `fuente_origen_clima` | `str` | Escala [0, 1] / Metadato | 100.0% | Valores: open_meteo_archive_api | Indicador derivado (fuente_origen_clima) |
| `es_atipico_clima` | `bool` | Escala [0, 1] / Metadato | 100.0% | Valores: False, True | Indicador derivado (es_atipico_clima) |
| `temperatura_max_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.42) | Indicador derivado (temperatura_max_c_norm) |
| `temperatura_media_c_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.52) | Indicador derivado (temperatura_media_c_norm) |
| `precipitacion_acumulada_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.23) | Indicador derivado (precipitacion_acumulada_mm_norm) |
| `evapotranspiracion_mm_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.44) | Indicador derivado (evapotranspiracion_mm_norm) |
| `humedad_relativa_pct_norm` | `float64` | Escala [0, 1] / Metadato | 100.0% | [0.00, 1.00] (media=0.51) | Indicador derivado (humedad_relativa_pct_norm) |
