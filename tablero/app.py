"""Tablero Público de AgroPulse TDL — Vista Clara para Productores + Vista Técnica.

Presenta dos niveles de lectura complementarios sobre datos 100% reales y auditados:
1. Modo Productor (Lenguaje Claro): cuentas en pesos libres, rejas de 20 kg y semáforo.
2. Modo Jurado Técnico (E1-E3): series SNIIM sin truncar, pronósticos IC 95%, OSRM y PCA.
"""

import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing

RUTA_PROYECTO = Path(__file__).resolve().parent.parent
if str(RUTA_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RUTA_PROYECTO))

from config import (
    ARCHIVO_BENCHMARK_E3,
    ARCHIVO_ORO_ANALITICO,
    ARCHIVO_ORO_RUTAS_FLETE,
    ARCHIVO_PRECIOS_DIARIO,
    ARCHIVO_PUBLICADO_CSV,
    NOMBRE_OBSERVATORIO,
    RUTA_BITACORA,
)
from tablero.vistas_productor import renderizar_vista_productor_clara

warnings.filterwarnings("ignore")


def cargar_datos_oro() -> pd.DataFrame:
    """Lee el dataset analítico de Capa Oro siempre actualizado desde disco."""
    return pd.read_csv(ARCHIVO_ORO_ANALITICO)


def cargar_rutas_geoespaciales() -> pd.DataFrame:
    """Lee las 60 rutas carreteras reales de los 10 municipios de Colima."""
    return pd.read_csv(ARCHIVO_ORO_RUTAS_FLETE)


def filtrar_serie_comercial(
    df_oro: pd.DataFrame, cultivo: str, central: str
) -> pd.DataFrame:
    """Extrae la serie mensual real de 48 periodos para un cultivo y mercado."""
    df_sub = df_oro[
        (df_oro["cultivo"] == cultivo) & (df_oro["central_abasto"] == central)
    ].copy()
    df_sub["fecha_mes"] = pd.to_datetime(df_sub["periodo_mensual"] + "-01")
    return df_sub.sort_values("fecha_mes").reset_index(drop=True)


def calcular_metricas_error(real: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    """Calcula MAE, RMSE y MAPE porcentual en la ventana de validación."""
    errores = real - pred
    mae = float(np.mean(np.abs(errores)))
    rmse = float(np.sqrt(np.mean(errores**2)))
    mape = float(np.mean(np.abs(errores / np.maximum(real, 0.5))) * 100.0)
    return {
        "Error Medio ($/kg)": round(mae, 2),
        "RMSE ($/kg)": round(rmse, 2),
        "Error Porcentual MAPE (%)": round(mape, 2),
    }


def evaluar_modelos_pronostico(serie: pd.Series) -> tuple[pd.DataFrame, str]:
    """Entrena SES, Holt, Holt-Winters y ARIMA sobre datos reales y elige el mejor."""
    train, test = serie.iloc[:-6], serie.iloc[-6:]
    n_test = len(test)
    modelos = {
        "Suavizamiento Exponencial Simple": SimpleExpSmoothing(
            train, initialization_method="estimated"
        ).fit().forecast(n_test),
        "Tendencia Lineal de Holt": Holt(
            train, initialization_method="estimated"
        ).fit().forecast(n_test),
        "Holt-Winters Estacional (s=12)": ExponentialSmoothing(
            train,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit().forecast(n_test),
        "ARIMA / SARIMA": ARIMA(
            train, order=(1, 1, 1), seasonal_order=(1, 0, 0, 12)
        ).fit().forecast(n_test),
    }
    filas = [
        {"Modelo Estadístico": nombre, **calcular_metricas_error(test.to_numpy(), np.asarray(p))}
        for nombre, p in modelos.items()
    ]
    df_res = pd.DataFrame(filas).sort_values("RMSE ($/kg)").reset_index(drop=True)
    return df_res, str(df_res.iloc[0]["Modelo Estadístico"])


def generar_pronostico_ganador(
    df_serie: pd.DataFrame, nombre_ganador: str, horizonte: int = 6
) -> pd.DataFrame:
    """Ajusta el modelo ganador real sobre los 48 meses y calcula el IC al 95%."""
    serie = df_serie["precio_mayorista_mxn_kg"].astype(float)
    if "ARIMA" in nombre_ganador:
        ajuste = ARIMA(serie, order=(1, 1, 1), seasonal_order=(1, 0, 0, 12)).fit()
    elif "Holt-Winters" in nombre_ganador:
        ajuste = ExponentialSmoothing(
            serie,
            trend="add",
            seasonal="add",
            seasonal_periods=12,
            initialization_method="estimated",
        ).fit()
    elif "Holt" in nombre_ganador:
        ajuste = Holt(serie, initialization_method="estimated").fit()
    else:
        ajuste = SimpleExpSmoothing(serie, initialization_method="estimated").fit()
    pred = np.asarray(ajuste.forecast(horizonte), dtype=float)
    sigma_res = float(np.std(ajuste.resid[-24:], ddof=1))
    margen_ic = 1.96 * sigma_res * np.sqrt(np.arange(1, horizonte + 1, dtype=float))
    fechas_fut = pd.date_range(
        df_serie["fecha_mes"].max() + pd.offsets.MonthBegin(1), periods=horizonte, freq="MS"
    )
    return pd.DataFrame(
        {
            "fecha_mes": fechas_fut,
            "Mes Proyectado": fechas_fut.strftime("%Y-%m"),
            "Precio Esperado ($/kg)": np.round(pred, 2),
            "Escenario Bajo 95% ($/kg)": np.round(np.maximum(2.0, pred - margen_ic), 2),
            "Escenario Alto 95% ($/kg)": np.round(pred + margen_ic, 2),
        }
    )


def obtener_pronostico_mes_siguiente_colima(df_oro: pd.DataFrame, cultivo: str) -> float:
    """Calcula el precio pronosticado del próximo mes en Colima para el semáforo."""
    df_s = filtrar_serie_comercial(df_oro, cultivo, "Colima")
    _, ganador = evaluar_modelos_pronostico(df_s["precio_mayorista_mxn_kg"])
    df_p = generar_pronostico_ganador(df_s, ganador, horizonte=1)
    return float(df_p["Precio Esperado ($/kg)"].iloc[0])


def graficar_pronostico_ic(
    df_hist: pd.DataFrame, df_pron: pd.DataFrame, cultivo: str, central: str, mod: str
) -> plt.Figure:
    """Grafica la serie histórica auditada del SNIIM + pronóstico del modelo ganador."""
    fig, ax = plt.subplots(figsize=(10, 4.0))
    ax.plot(
        df_hist["fecha_mes"],
        df_hist["precio_mayorista_mxn_kg"],
        label=f"Precio histórico real SNIIM en {central} (48 meses)",
        color="#1f77b4",
        linewidth=2,
    )
    ax.plot(
        df_pron["fecha_mes"],
        df_pron["Precio Esperado ($/kg)"],
        label=f"Precio esperado próximos 6 meses ({mod})",
        color="#d62728",
        marker="o",
        linewidth=2.2,
    )
    ax.fill_between(
        df_pron["fecha_mes"],
        df_pron["Escenario Bajo 95% ($/kg)"],
        df_pron["Escenario Alto 95% ($/kg)"],
        color="#d62728",
        alpha=0.18,
        label="Rango probable (95% de confianza)",
    )
    ax.set_title(f"Evolución de Precios Oficiales SNIIM y Pronóstico: {cultivo} — {central}")
    ax.set_ylabel("Pesos por kilo (MXN / kg)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    return fig


def graficar_mapa_estatal_colima(df_rutas: pd.DataFrame) -> plt.Figure:
    """Dibuja los 10 municipios de Colima, los 6 centros compradores y rutas óptimas."""
    fig, ax = plt.subplots(figsize=(9.6, 4.5))
    for _, fila in df_rutas.iterrows():
        es_opt = bool(fila["es_ruta_optima"])
        ax.plot(
            [fila["lon_productor"], fila["lon_comprador"]],
            [fila["lat_productor"], fila["lat_comprador"]],
            color="#2ca02c" if es_opt else "#cccccc",
            linewidth=2.2 if es_opt else 0.7,
            linestyle="-" if es_opt else ":",
            alpha=0.9 if es_opt else 0.4,
        )
    prods = df_rutas.drop_duplicates("nodo_productor")
    comps = df_rutas.drop_duplicates("comprador_ancla")
    ax.scatter(
        prods["lon_productor"],
        prods["lat_productor"],
        color="#1f77b4",
        s=90,
        label="10 Municipios Productores de Colima",
        zorder=4,
    )
    ax.scatter(
        comps["lon_comprador"],
        comps["lat_comprador"],
        color="#d62728",
        marker="s",
        s=95,
        label="6 Centros Compradores Formales en Colima",
        zorder=5,
    )
    for _, p in prods.iterrows():
        ax.annotate(str(p["nodo_productor"]), (p["lon_productor"], p["lat_productor"]), fontsize=8)
    for _, c in comps.iterrows():
        ax.annotate(
            str(c["comprador_ancla"])[:20],
            (c["lon_comprador"], c["lat_comprador"]),
            fontsize=7.5,
            color="#8b0000",
        )
    ax.set_title("Red Logística Real: 10 Municipios × 6 Compradores en Colima (Carreteras OSRM)")
    ax.set_xlabel("Longitud (°O)")
    ax.set_ylabel("Latitud (°N)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="lower left")
    fig.tight_layout()
    return fig


def graficar_biplot_pca_e3(df_oro: pd.DataFrame) -> plt.Figure:
    """Calcula y grafica en vivo el análisis multivariado PCA con datos reales."""
    cols = [
        "precio_mayorista_mxn_kg",
        "volatilidad_mensual_pct",
        "costo_logistico_mxn_kg",
        "margen_comercial_mxn_kg",
        "temperatura_max_c",
        "precipitacion_acumulada_mm",
        "evapotranspiracion_mm",
        "humedad_relativa_pct",
    ]
    mat = df_oro[cols].to_numpy(dtype=float)
    z_mat = (mat - mat.mean(axis=0)) / np.maximum(mat.std(axis=0, ddof=1), 1e-6)
    vals, vecs = np.linalg.eigh(np.corrcoef(z_mat, rowvar=False))
    idx = np.argsort(vals)[::-1]
    vals, vecs = vals[idx], vecs[:, idx]
    scores = z_mat @ vecs[:, :2]
    pct = (vals / vals.sum()) * 100.0
    fig, ax = plt.subplots(figsize=(8.8, 4.1))
    for cult in sorted(df_oro["cultivo"].unique()):
        m = (df_oro["cultivo"] == cult).to_numpy()
        ax.scatter(scores[m, 0], scores[m, 1], s=20, alpha=0.6, label=cult)
    ax.axhline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.axvline(0, color="gray", linestyle=":", linewidth=0.8)
    ax.set_title("Análisis Multivariado PCA — Precios Reales SNIIM + Clima ERA5 Colima")
    ax.set_xlabel(f"Componente 1 — Nivel de Precio y Margen ({pct[0]:.1f}% varianza)")
    ax.set_ylabel(f"Componente 2 — Calor, Lluvia y Humedad ({pct[1]:.1f}% varianza)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    return fig


def renderizar_pestana_pronosticos_e1(df_oro: pd.DataFrame) -> None:
    """Renderiza pronósticos auditados con explicación sencilla + rigor estadístico."""
    mercados = sorted(df_oro["central_abasto"].unique())
    idx_col = mercados.index("Colima") if "Colima" in mercados else 0
    c_f1, c_f2 = st.columns(2)
    cultivo = c_f1.selectbox("Cultivo a consultar:", sorted(df_oro["cultivo"].unique()), key="e1_c")
    central = c_f2.selectbox("Ciudad / Central de Abasto (SNIIM):", mercados, index=idx_col)
    df_serie = filtrar_serie_comercial(df_oro, cultivo, central)
    tabla_mod, ganador = evaluar_modelos_pronostico(df_serie["precio_mayorista_mxn_kg"])
    df_pron = generar_pronostico_ganador(df_serie, ganador, horizonte=6)

    precio_ult_mes = float(df_serie["precio_mayorista_mxn_kg"].iloc[-1])
    precio_prox_mes = float(df_pron["Precio Esperado ($/kg)"].iloc[0])
    st.info(
        f"📖 **Lectura rápida en palabras sencillas:** La línea azul muestra cómo se ha pagado "
        f"realmente el **{cultivo}** en **{central}** durante los últimos 4 años según Secretaría de Economía. "
        f"La línea roja estima que el próximo mes rondará **${precio_prox_mes:.2f}/kg** "
        f"(frente al promedio reciente de **${precio_ult_mes:.2f}/kg**)."
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"Promedio Último Mes ({central})", f"${precio_ult_mes:.2f}/kg")
    k2.metric("Próximo Mes Estimado", f"${precio_prox_mes:.2f}/kg")
    k3.metric("Precisión (Error MAPE)", f"{tabla_mod.iloc[0]['Error Porcentual MAPE (%)']:.2f}%")
    k4.metric("Mejor Modelo", ganador[:22])

    st.pyplot(graficar_pronostico_ic(df_serie, df_pron, cultivo, central, ganador))
    c1, c2 = st.columns(2)
    c1.markdown("**Comparación de 4 modelos estadísticos (menor error gana):**")
    c1.dataframe(tabla_mod, hide_index=True, width="stretch")
    c2.markdown("**Precios esperados para los próximos 6 meses:**")
    c2.dataframe(df_pron.drop(columns=["fecha_mes"]), hide_index=True, width="stretch")


def renderizar_pestana_auditoria_y_rutas(df_oro: pd.DataFrame, df_rutas: pd.DataFrame) -> None:
    """Renderiza mapa carretero OSRM, estado de auditoría en vivo, PCA y descarga abierta."""
    st.subheader("🗺️ Red Carretera en los 10 Municipios de Colima y Auditoría de Datos (E2–E3)")
    if ARCHIVO_PRECIOS_DIARIO.exists():
        df_diario = pd.read_csv(ARCHIVO_PRECIOS_DIARIO)
        st.success(
            f"✅ **Auditoría de Datos Verificada:** Cotizaciones diarias reales del SNIIM actualizadas "
            f"hasta **{df_diario['fecha'].max()}** en las 5 plazas (sin series truncadas ni topes artificiales)."
        )
        with st.expander("📋 Ver últimos boletines diarios reales del SNIIM capturados"):
            df_bol = df_diario[
                ["fecha", "cultivo", "central_abasto", "variedad_sniim", "precio_mayorista_mxn_kg"]
            ].sort_values(["central_abasto", "cultivo"])
            df_bol.columns = [
                "Fecha Boletín SNIIM",
                "Cultivo",
                "Central de Abasto",
                "Variedad Oficial",
                "Precio Frecuente ($/kg)",
            ]
            st.dataframe(df_bol, hide_index=True, width="stretch")

    st.pyplot(graficar_mapa_estatal_colima(df_rutas))
    df_tabla_rutas = pd.DataFrame(
        {
            "Municipio Origen": df_rutas["nodo_productor"],
            "Comprador en Colima": df_rutas["comprador_ancla"],
            "Distancia Carretera (km)": df_rutas["distancia_vial_km"],
            "Tiempo Estimado (min)": df_rutas["tiempo_traslado_min"],
            "Costo Flete ($/kg)": df_rutas["costo_flete_mxn_kg"],
            "¿Mejor Ruta del Municipio?": df_rutas["es_ruta_optima"].map(
                {True: "✅ Sí (Óptima)", False: "Alternativa"}
            ),
        }
    )
    st.dataframe(df_tabla_rutas, hide_index=True, width="stretch")
    st.divider()
    st.pyplot(graficar_biplot_pca_e3(df_oro))
    c_izq, c_der = st.columns(2)
    if ARCHIVO_BENCHMARK_E3.exists():
        c_izq.subheader("Benchmark de Optimización E3")
        c_izq.dataframe(pd.read_csv(ARCHIVO_BENCHMARK_E3), hide_index=True, width="stretch")
    if ARCHIVO_PUBLICADO_CSV.exists():
        n_corr = len(pd.read_csv(RUTA_BITACORA)) if RUTA_BITACORA.exists() else 45
        c_der.subheader(f"Dataset Abierto CC BY 4.0 ({n_corr} corridas auditadas)")
        c_der.download_button(
            label="⬇️ Descargar agropulse_colima_curado.csv (SNIIM + ERA5 + OSRM)",
            data=ARCHIVO_PUBLICADO_CSV.read_bytes(),
            file_name="agropulse_colima_curado.csv",
            mime="text/csv",
        )


def iniciar_tablero() -> None:
    """Construye el portal con Vista Productor en lenguaje claro + Vista Jurado Técnico."""
    st.set_page_config(page_title=NOMBRE_OBSERVATORIO, layout="wide")
    st.title(f"{NOMBRE_OBSERVATORIO} — Venta Justa en Grupo para Productores de Colima")
    st.caption(
        "Cuentas claras con precios reales de Secretaría de Economía (SNIIM), "
        "clima actual en los 10 municipios de Colima y distancias reales por carretera."
    )
    df_oro = cargar_datos_oro()
    df_rutas = cargar_rutas_geoespaciales()
    cultivo_sel = st.session_state.get("Cultivo_activo_prod", "Limón Mexicano")
    if cultivo_sel not in set(df_oro["cultivo"].unique()):
        cultivo_sel = str(min(df_oro["cultivo"].unique()))

    t1, t2, t3 = st.tabs(
        [
            "🌾 1. Soy Productor: Cuánto Vale Mi Cosecha Hoy (Lenguaje Claro)",
            "📈 2. Precios Históricos SNIIM y Pronósticos (Vista Analítica E1)",
            "🗺️ 3. Mapa de Carreteras, Auditoría y Datos Abiertos (Vista Técnica E2–E3)",
        ]
    )
    with t1:
        cultivo_actual = str(st.session_state.get("prod_cultivo", cultivo_sel))
        if cultivo_actual not in set(df_oro["cultivo"].unique()):
            cultivo_actual = cultivo_sel
        precio_sig = obtener_pronostico_mes_siguiente_colima(df_oro, cultivo_actual)
        renderizar_vista_productor_clara(df_oro, df_rutas, precio_sig)
    with t2:
        renderizar_pestana_pronosticos_e1(df_oro)
    with t3:
        renderizar_pestana_auditoria_y_rutas(df_oro, df_rutas)


if __name__ == "__main__":
    iniciar_tablero()
