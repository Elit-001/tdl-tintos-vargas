# Dataset Público Curado — AgroPulse TDL (Entrega E3)

* **Archivo CSV (multiplataforma LF):** `agropulse_colima_curado.csv` (`960` filas × `27` columnas)
* **Archivo Columnar Optimizado:** `agropulse_colima_curado.parquet`
* **Licencia Abierta:** Creative Commons Attribution 4.0 International (`CC BY 4.0` — ver `LICENSE`)
* **Ficha Técnica Completa (Datasheet):** [`docs/E3/datasheet.md`](../../docs/E3/datasheet.md)
* **Privacidad:** `0%` Datos Personales Identificables (PII).

## Ejemplo Rápido de Carga en Python
```python
import pandas as pd

df = pd.read_csv('data/publicado/agropulse_colima_curado.csv')
print(df[['periodo_mensual', 'cultivo', 'precio_mayorista_mxn_kg', 'spread_brokerage_colima_mxn_kg']].head())
```
