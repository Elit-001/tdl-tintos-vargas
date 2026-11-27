"""Motor Real de Consolidación de Pools Heterogéneos y Liquidación B2B en Colima.

Resuelve las limitaciones operativas reales del acopio agrícola:
1. Acepta aportes variables de cualquier kilaje por productor (ej. 45 kg, 180 kg, 620 kg).
2. Selecciona automáticamente el vehículo óptimo (Pickup, Rabón 3.5T o Torton Refrigerado).
3. Calcula merma térmica/vial real y compara liquidación AgroPulse vs. pago de coyote.
"""

import pandas as pd

from config import (
    COMISION_BROKERAGE_PCT,
    DESCUENTO_COYOTE_PCT,
    FLOTA_VEHICULAR_COLIMA,
)


def seleccionar_vehiculo_optimo(peso_total_kg: float) -> dict[str, str | float | bool]:
    """Elige la unidad de transporte real más económica según el peso total del pool."""
    for unidad in FLOTA_VEHICULAR_COLIMA:
        if peso_total_kg <= float(unidad["capacidad_max_kg"]):
            return unidad
    return FLOTA_VEHICULAR_COLIMA[-1]


def estimar_merma_transporte_pct(
    distancia_km: float, temp_max_c: float, refrigerado: bool
) -> float:
    """Estima la merma física (%) en tránsito según distancia carretera y calor."""
    exceso_calor = max(0.0, temp_max_c - 27.0) * 0.28
    desgaste_vial = distancia_km * 0.022
    merma_bruta = 1.2 + exceso_calor + desgaste_vial
    factor_frio = 0.45 if refrigerado else 1.0
    return round(min(12.0, merma_bruta * factor_frio), 2)


def liquidar_pool_multiproductor(
    ofertas: list[dict[str, str | float]],
    precio_plaza_colima_kg: float,
    prima_comprador_pct: float,
    demanda_comprador_kg: float,
    rutas_comprador: pd.DataFrame,
    temp_max_c: float = 31.5,
) -> tuple[pd.DataFrame, dict[str, str | float | bool]]:
    """Consolida lotes de distinto kilaje, prorratea flete/merma y liquida por productor."""
    df_of = pd.DataFrame(ofertas)
    peso_bruto = float(df_of["kilos_ofrecidos"].sum())
    peso_aceptado = min(peso_bruto, demanda_comprador_kg)
    factor_cupo = peso_aceptado / max(peso_bruto, 1.0)
    df_of["kilos_asignados"] = (df_of["kilos_ofrecidos"] * factor_cupo).round(1)

    mapa_dist = dict(
        zip(
            rutas_comprador["nodo_productor"],
            rutas_comprador["distancia_vial_km"],
            strict=False,
        )
    )
    df_of["distancia_km"] = df_of["municipio"].map(mapa_dist).fillna(30.0)
    dist_circuito_km = round(
        float(df_of["distancia_km"].max()) + 6.5 * max(0, len(df_of) - 1), 2
    )

    unidad = seleccionar_vehiculo_optimo(peso_aceptado)
    flete_total = round(
        float(unidad["maniobra_fija_mxn"])
        + dist_circuito_km * float(unidad["tarifa_km_mxn"]),
        2,
    )
    flete_por_kg = round(flete_total / max(peso_aceptado, 1.0), 2)
    merma_pct = estimar_merma_transporte_pct(
        dist_circuito_km, temp_max_c, bool(unidad["refrigerado"])
    )

    precio_b2b = round(precio_plaza_colima_kg * (1.0 + prima_comprador_pct / 100.0), 2)
    ingreso_efectivo_kg = round(precio_b2b * (1.0 - merma_pct / 100.0), 2)
    comision_kg = round(ingreso_efectivo_kg * (COMISION_BROKERAGE_PCT / 100.0), 2)
    pago_neto_agropulse_kg = round(ingreso_efectivo_kg - flete_por_kg - comision_kg, 2)
    pago_coyote_kg = round(
        precio_plaza_colima_kg * (1.0 - DESCUENTO_COYOTE_PCT / 100.0), 2
    )

    df_of["pago_coyote_total_mxn"] = (df_of["kilos_asignados"] * pago_coyote_kg).round(2)
    df_of["pago_agropulse_total_mxn"] = (
        df_of["kilos_asignados"] * pago_neto_agropulse_kg
    ).round(2)
    df_of["ganancia_extra_productor_mxn"] = (
        df_of["pago_agropulse_total_mxn"] - df_of["pago_coyote_total_mxn"]
    ).round(2)

    resumen = {
        "peso_ofertado_kg": round(peso_bruto, 1),
        "peso_consolidado_kg": round(peso_aceptado, 1),
        "porcentaje_llenado_pedido": round((peso_aceptado / demanda_comprador_kg) * 100.0, 1),
        "vehiculo_asignado": str(unidad["vehiculo"]),
        "distancia_circuito_recoleccion_km": dist_circuito_km,
        "merma_estimada_pct": merma_pct,
        "flete_total_mxn": flete_total,
        "flete_unitario_mxn_kg": flete_por_kg,
        "precio_venta_comprador_kg": precio_b2b,
        "pago_neto_productor_kg": pago_neto_agropulse_kg,
        "pago_coyote_referencia_kg": pago_coyote_kg,
        "comision_neta_agropulse_lote_mxn": round(comision_kg * peso_aceptado, 2),
        "es_rentable_vs_coyote": bool(pago_neto_agropulse_kg > pago_coyote_kg),
    }
    return df_of, resumen
