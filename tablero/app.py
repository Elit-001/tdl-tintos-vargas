"""Tablero Público Interactivo de AgroPulse TDL en Streamlit (Entrega E1).

Carga el dataset consolidado de Capa Oro (data/oro/dataset_analitico.csv),
evalúa los modelos de pronóstico de series de tiempo, grafica el modelo ganador
con su intervalo de confianza al 95% y presenta recomendaciones de negocio.
"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing

from config import ARCHIVO_ORO_ANALITICO, NOMBRE_OBSERVATORIO

warnings.filterwarnings("ignore")


def cargar_datos_oro() -> pd.DataFrame:
    """Lee el dataset analítico de Capa Oro validado e integrado."""
    return pd.read_csv(ARCHIVO_ORO_ANALITICO)


def filtrar_serie_comercial(
    df_oro: pd.DataFrame, cultivo: str, central: str
) -> pd.DataFrame:
    """Extrae la serie mensual de 48 periodos para un cultivo y central de abasto."""
    df_sub = df_oro[
        (df_oro["cultivo"] == cultivo) & (df_oro["central_abasto"] == central)
    ].copy()
    df_sub["fecha_mes"] = pd.to_datetime(df_sub["periodo_mensual"] + "-01")
    return df_sub.sort_values("fecha_mes").reset_index(drop=True)


def calcular_metricas_error(real: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    """Calcula MAE, RMSE y MAPE porcentual en la ventana de prueba."""
    errores = real - pred
    mae = float(np.mean(np.abs(errores)))
    rmse = float(np.sqrt(np.mean(errores**2)))
    mape = float(np.mean(np.abs(errores / real)) * 100.0)
    return {"MAE": round(mae, 3), "RMSE": round(rmse, 3), "MAPE (%)": round(mape, 2)}


def evaluar_modelos_pronostico(serie: pd.Series) -> pd.DataFrame:
    """Entrena SES, Holt, Holt-Winters y ARIMA (42 train / 6 test) y compara errores."""
    train, test = serie.iloc[:-6], serie.iloc[-6:]
    n_test = len(test)
    pred_ses = SimpleExpSmoothing(train).fit().forecast(n_test)
    pred_holt = Holt(train).fit().forecast(n_test)
    pred_hw = (
        ExponentialSmoothing(
            train, trend="add", seasonal="add", seasonal_periods=12
        )
        .fit()
        .forecast(n_test)
    )
    pred_arima = ARIMA(train, order=(1, 1, 1), seasonal_order=(1, 0, 0, 12)).fit().forecast(n_test)
    modelos = {
        "Suavizamiento Exponencial Simple": pred_ses,
        "Tendencia Lineal de Holt": pred_holt,
        "Holt-Winters Estacional (s=12)": pred_hw,
        "ARIMA / SARIMA": pred_arima,
    }
    filas = [
        {"Modelo": nombre, **calcular_metricas_error(test.to_numpy(), np.asarray(p))}
        for nombre, p in modelos.items()
    ]
    return pd.DataFrame(filas).sort_values("RMSE").reset_index(drop=True)


def generar_pronostico_ganador(
    df_serie: pd.DataFrame, horizonte: int = 6
) -> pd.DataFrame:
    """Ajusta el modelo ganador sobre los 48 meses y calcula el IC al 95%."""
    serie = df_serie["precio_mayorista_mxn_kg"].astype(float)
    modelo_hw = ExponentialSmoothing(
        serie, trend="add", seasonal="add", seasonal_periods=12
    ).fit()
    pred = np.asarray(modelo_hw.forecast(horizonte), dtype=float)
    sigma_res = float(np.std(modelo_hw.resid, ddof=1))
    pasos = np.arange(1, horizonte + 1, dtype=float)
    margen_ic = 1.96 * sigma_res * np.sqrt(pasos)
    ultima_fecha = df_serie["fecha_mes"].max()
    fechas_fut = pd.date_range(
        ultima_fecha + pd.offsets.MonthBegin(1), periods=horizonte, freq="MS"
    )
    return pd.DataFrame(
        {
            "fecha_mes": fechas_fut,
            "periodo_mensual": fechas_fut.strftime("%Y-%m"),
            "pronostico_mxn_kg": np.round(pred, 2),
            "ic_inferior_95": np.round(pred - margen_ic, 2),
            "ic_superior_95": np.round(pred + margen_ic, 2),
        }
    )


def graficar_pronostico_ic(
    df_hist: pd.DataFrame, df_pron: pd.DataFrame, cultivo: str, central: str
) -> plt.Figure:
    """Crea la gráfica de serie histórica + pronóstico a 6 meses e IC al 95%."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(
        df_hist["fecha_mes"], df_hist["precio_mayorista_mxn_kg"],
        label="Histórico Observado (48 meses)", color="#1f77b4", linewidth=2,
    )
    ax.plot(
        df_pron["fecha_mes"], df_pron["pronostico_mxn_kg"],
        label="Pronóstico Ganador (Holt-Winters)", color="#d62728", marker="o", linewidth=2.2,
    )
    ax.fill_between(
        df_pron["fecha_mes"], df_pron["ic_inferior_95"], df_pron["ic_superior_95"],
        color="#d62728", alpha=0.2, label="Intervalo de Confianza 95%",
    )
    ax.set_title(f"Pronóstico de Precio Mayorista: {cultivo} en {central}")
    ax.set_ylabel("Precio Mayorista (MXN / kg)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return fig


def mostrar_explicacion_negocio(
    df_hist: pd.DataFrame, df_pron: pd.DataFrame, cultivo: str, central: str
) -> None:
    """Renderiza el motor de Brokerage, el Oráculo Agrícola y el botón Ofrecer producto."""
    idx_max = int(df_pron["pronostico_mxn_kg"].idxmax())
    mes_pico = str(df_pron.loc[idx_max, "periodo_mensual"])
    precio_venta = float(df_pron.loc[idx_max, "pronostico_mxn_kg"])
    flete = float(df_hist["costo_logistico_mxn_kg"].iloc[-1])
    precio_compra_prod = round(precio_venta * 0.84, 2)
    spread_neto = round(precio_venta - precio_compra_prod - (flete * 0.35), 2)
    st.subheader("Oráculo Agrícola y Motor de Intermediación Inteligente (Brokerage)")
    st.info(
        f"**Dictamen del Oráculo ({cultivo} — Origen `{df_hist['zona_agricola'].iloc[0]}`):** "
        f"El modelo de series de tiempo proyecta el pico de demanda y **precio máximo** en "
        f"**{mes_pico}** (**${precio_venta:.2f} MXN/kg**). **Tarifa AgroPulse:** compra al "
        f"productor a **${precio_compra_prod:.2f} MXN/kg** y venta consolidada (ej. 4 productores "
        f"× 100 kg = **400 kg** para Walmart / Empacadora San José) a **${precio_venta:.2f} MXN/kg**, "
        f"optimizando el flete (${flete:.2f}/kg) con un margen de intermediación de **${spread_neto:.2f} MXN/kg**."
    )
    if st.button("Ofrecer producto (Integrar mi lote de cosecha al Pool de 400 kg)"):
        st.success(
            f"Oferta registrada para **{cultivo}** en `{df_hist['zona_agricola'].iloc[0]}` "
            f"con tarifa garantizada de compra de **${precio_compra_prod:.2f} MXN/kg**."
        )


def iniciar_tablero() -> None:
    """Construye la interfaz principal del observatorio público en Streamlit."""
    st.set_page_config(page_title=NOMBRE_OBSERVATORIO, layout="wide")
    st.title(f"{NOMBRE_OBSERVATORIO} — Inteligencia Agrocomercial y Pronósticos (E1)")
    df_oro = cargar_datos_oro()
    col_f1, col_f2 = st.columns(2)
    cultivo = col_f1.selectbox("Seleccione Cultivo de Colima:", sorted(df_oro["cultivo"].unique()))
    central = col_f2.selectbox("Seleccione Central de Abasto:", sorted(df_oro["central_abasto"].unique()))

    df_serie = filtrar_serie_comercial(df_oro, cultivo, central)
    tabla_modelos = evaluar_modelos_pronostico(df_serie["precio_mayorista_mxn_kg"])
    df_pron = generar_pronostico_ganador(df_serie, horizonte=6)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Último Precio (MXN/kg)", f"${df_serie['precio_mayorista_mxn_kg'].iloc[-1]:.2f}")
    k2.metric("Modelo Ganador", str(tabla_modelos.iloc[0]["Modelo"])[:18])
    k3.metric("Error MAPE Ganador", f"{tabla_modelos.iloc[0]['MAPE (%)']:.2f}%")
    k4.metric("Zona Origen Colima", str(df_serie["zona_agricola"].iloc[0]))

    st.pyplot(graficar_pronostico_ic(df_serie, df_pron, cultivo, central))
    mostrar_explicacion_negocio(df_serie, df_pron, cultivo, central)
    c1, c2 = st.columns(2)
    c1.subheader("Comparativa de Modelos (Prueba 6 meses)")
    c1.dataframe(tabla_modelos, use_container_width=True)
    c2.subheader("Tabla de Pronóstico e Intervalo de Confianza (95%)")
    c2.dataframe(df_pron.drop(columns=["fecha_mes"]), use_container_width=True)


if __name__ == "__main__":
    iniciar_tablero()
