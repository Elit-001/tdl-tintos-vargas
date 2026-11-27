"""Vista en Lenguaje Claro para Productores Agrícolas de los 10 Municipios de Colima.

Traduce cotizaciones oficiales SNIIM, pronósticos estadísticos, clima satelital y
ruteo carretero OSRM a cuentas claras en pesos, kilos y rejas de 20 kg sin tecnicismos.
"""

import pandas as pd
import streamlit as st

from config import (
    ARCHIVO_CLIMA_DIARIO,
    ARCHIVO_PRECIOS_DIARIO,
    COMISION_BROKERAGE_PCT,
    COMPRADORES_ANCLA_COLIMA,
    FLETE_NACIONAL_DESDE_COLIMA_MXN_KG,
    NODOS_PRODUCTORES_COLIMA,
)
from pipeline.motor_brokerage import liquidar_pool_multiproductor

OFERTAS_VECINOS_EJEMPLO: list[dict[str, str | float]] = [
    {"id_oferta": "Vecino 1", "municipio": "Tecomán", "calidad": "Primera", "kilos_ofrecidos": 180.0},
    {"id_oferta": "Vecino 2", "municipio": "Coquimatlán", "calidad": "Primera", "kilos_ofrecidos": 60.0},
    {"id_oferta": "Vecino 3", "municipio": "Armería", "calidad": "Extra", "kilos_ofrecidos": 300.0},
    {"id_oferta": "Vecino 4", "municipio": "Ixtlahuacán", "calidad": "Primera", "kilos_ofrecidos": 120.0},
    {"id_oferta": "Vecino 5", "municipio": "Comala", "calidad": "Extra", "kilos_ofrecidos": 220.0},
]


def obtener_cotizacion_actual_plaza(
    df_oro: pd.DataFrame, cultivo: str, central: str = "Colima"
) -> tuple[float, str]:
    """Obtiene el precio real más reciente (diario SNIIM si existe) y su fecha."""
    if ARCHIVO_PRECIOS_DIARIO.exists():
        df_d = pd.read_csv(ARCHIVO_PRECIOS_DIARIO)
        sub_d = df_d[(df_d["cultivo"] == cultivo) & (df_d["central_abasto"] == central)]
        if not sub_d.empty:
            fila = sub_d.sort_values("fecha").iloc[-1]
            return float(fila["precio_mayorista_mxn_kg"]), str(fila["fecha"])
    sub_m = df_oro[(df_oro["cultivo"] == cultivo) & (df_oro["central_abasto"] == central)]
    fila_m = sub_m.sort_values("periodo_mensual").iloc[-1]
    return float(fila_m["precio_mayorista_mxn_kg"]), str(fila_m["periodo_mensual"])


def obtener_clima_reciente_municipio(
    df_oro: pd.DataFrame, municipio: str
) -> tuple[float, float, str]:
    """Devuelve temperatura máxima, lluvia reciente y fecha para el municipio."""
    if ARCHIVO_CLIMA_DIARIO.exists():
        df_c = pd.read_csv(ARCHIVO_CLIMA_DIARIO)
        sub_c = df_c[df_c["zona_agricola"] == municipio]
        if not sub_c.empty:
            fila = sub_c.sort_values("fecha").iloc[-1]
            return (
                float(fila["temperatura_max_c"]),
                float(fila["precipitacion_acumulada_mm"]),
                str(fila["fecha"]),
            )
    fila_o = df_oro.iloc[-1]
    return float(fila_o["temperatura_max_c"]), 0.0, str(fila_o["periodo_mensual"])


def generar_semaforo_cosecha(
    precio_hoy: float, precio_mes_sig: float, temp_c: float, lluvia_mm: float, muni: str
) -> tuple[str, str, str]:
    """Traduce el pronóstico y el clima a una recomendación sencilla de campo."""
    cambio_pct = ((precio_mes_sig - precio_hoy) / max(precio_hoy, 1.0)) * 100.0
    if cambio_pct >= 7.0:
        titulo = "🟡 CONSEJO: Si tu fruta aún aguanta en árbol, conviene esperar un poco"
        detalle = (
            f"Hoy se paga alrededor de ${precio_hoy:.2f}/kg en Colima, pero se espera que "
            f"suba cerca de ${precio_mes_sig:.2f}/kg el próximo mes (+{cambio_pct:.0f}%)."
        )
        tipo = "warning"
    elif cambio_pct <= -5.0:
        titulo = "🟢 CONSEJO: ¡Conviene cortar y vender hoy mismo en grupo!"
        detalle = (
            f"Hoy el precio está firme (${precio_hoy:.2f}/kg) y suele bajar el próximo mes "
            f"(hacia ${precio_mes_sig:.2f}/kg). Asegura tu venta de una vez."
        )
        tipo = "success"
    else:
        titulo = "🟢 CONSEJO: Buen momento para vender juntando carga con tus vecinos"
        detalle = (
            f"El precio se mantiene estable (${precio_hoy:.2f}/kg). Tu mayor ganancia hoy "
            "está en compartir camión para no regalar tu cosecha al coyote."
        )
        tipo = "success"
    aviso_clima = (
        f"En {muni} hace {temp_c:.1f}°C hoy: embarca temprano para que el calor no le reste peso a tu fruta."
        if temp_c >= 30.5
        else f"Clima favorable en {muni} ({temp_c:.1f}°C y {lluvia_mm:.1f} mm de lluvia): buen traslado sin castigo por calor."
    )
    return tipo, titulo, f"{detalle} {aviso_clima}"


def _inicializar_camion_vecinos() -> None:
    """Carga el listado inicial de vecinos anotados en el camión compartido."""
    if "libro_ofertas_pool" not in st.session_state:
        st.session_state["libro_ofertas_pool"] = [dict(x) for x in OFERTAS_VECINOS_EJEMPLO]


def _renderizar_tarjetas_dinero(
    kilos_mios: float, res: dict[str, str | float | bool], comprador: str, fecha_sniim: str
) -> None:
    """Muestra en números grandes cuánto recibe el productor en mano vs el coyote."""
    pago_kg = float(res["pago_neto_productor_kg"])
    coyote_kg = float(res["pago_coyote_referencia_kg"])
    mi_pago_total = round(kilos_mios * pago_kg, 2)
    mi_coyote_total = round(kilos_mios * coyote_kg, 2)
    mi_extra = round(mi_pago_total - mi_coyote_total, 2)
    cajas_eq = round(kilos_mios / 20.0, 1)

    st.markdown(f"### 💰 Tus cuentas claras por **{kilos_mios:,.0f} kilos** (*{cajas_eq} rejas de 20 kg*)")
    c1, c2, c3 = st.columns(3)
    c1.metric(
        "✅ Recibes LIBRE en tu mano (AgroPulse)",
        f"${mi_pago_total:,.0f} pesos",
        f"Te queda a ${pago_kg:.2f} pesos el kilo",
    )
    c2.metric(
        "🐺 Lo que te daría el coyote en huerta",
        f"${mi_coyote_total:,.0f} pesos",
        f"Paga aprox. ${coyote_kg:.2f} pesos el kilo",
        delta_color="off",
    )
    c3.metric(
        "🎉 Dinero EXTRA que ganas para tu familia",
        f"+${mi_extra:,.0f} pesos",
        f"Vendiendo directo a {comprador}",
    )
    st.caption(
        f"📌 Cálculo respaldado con el precio real del boletín oficial SNIIM Colima ({fecha_sniim}). "
        "Ya viene descontado el flete compartido y el servicio."
    )


def _renderizar_explicacion_peso_por_peso(
    precio_b2b: float, res: dict[str, str | float | bool]
) -> None:
    """Explica renglón por renglón adónde va cada peso sin jerga financiera."""
    merma_pesos = round(precio_b2b * (float(res["merma_estimada_pct"]) / 100.0), 2)
    flete_kg = float(res["flete_unitario_mxn_kg"])
    ingreso_ef = round(precio_b2b - merma_pesos, 2)
    cuota_kg = round(ingreso_ef * (COMISION_BROKERAGE_PCT / 100.0), 2)
    libre_kg = float(res["pago_neto_productor_kg"])

    with st.expander("🔍 Ver cuenta clara peso por peso: ¿por qué recibo esa cantidad?", expanded=False):
        st.markdown(
            f"- **1. Lo que paga el comprador formal por kilo:** `${precio_b2b:.2f} pesos`\n"
            f"- **2. Menos pérdida natural de peso en el camino ({res['merma_estimada_pct']}%):** `-${merma_pesos:.2f} pesos`\n"
            f"- **3. Menos tu parte del camión compartido ({res['vehiculo_asignado']}):** `-${flete_kg:.2f} pesos`\n"
            f"- **4. Menos cuota de servicio AgroPulse ({COMISION_BROKERAGE_PCT}% solo si vendes):** `-${cuota_kg:.2f} pesos` "
            "*(cubre buscar comprador, coordinar el camión y asegurar tu pago)*\n"
            f"- **✅ LO QUE RECIBES LIBRE EN TU MANO POR CADA KILO:** **`${libre_kg:.2f} pesos`**"
        )


def _renderizar_comparador_ciudades_sencillo(df_oro: pd.DataFrame, cultivo: str) -> None:
    """Muestra en tabla sencilla cuánto pagan hoy otras ciudades descontando el viaje."""
    filas: list[dict[str, str | float]] = []
    for plaza, flete_nac in FLETE_NACIONAL_DESDE_COLIMA_MXN_KG.items():
        precio_plaza, fecha_p = obtener_cotizacion_actual_plaza(df_oro, cultivo, plaza)
        libre_aprox = round(precio_plaza - flete_nac, 2)
        filas.append(
            {
                "Ciudad donde se vende": plaza,
                "Precio en central ($/kg)": round(precio_plaza, 2),
                "Costo aprox. de viaje ($/kg)": round(flete_nac, 2),
                "Precio descontando viaje ($/kg)": libre_aprox,
                "Último reporte oficial": fecha_p,
            }
        )
    df_ciudades = pd.DataFrame(filas).sort_values(
        "Precio descontando viaje ($/kg)", ascending=False
    )
    mejor_plaza = str(df_ciudades.iloc[0]["Ciudad donde se vende"])
    st.markdown(f"#### 🚚 ¿Dónde pagan mejor tu **{cultivo}** hoy fuera y dentro de Colima?")
    st.info(
        f"💡 Descontando lo que cuesta llevar la fruta, hoy la plaza que mejor rinde es **{mejor_plaza}**."
    )
    st.dataframe(df_ciudades, hide_index=True, width="stretch")


def renderizar_vista_productor_clara(
    df_oro: pd.DataFrame, df_rutas: pd.DataFrame, precio_pronosticado_colima: float
) -> None:
    """Renderiza la calculadora principal en lenguaje sencillo para el productor."""
    _inicializar_camion_vecinos()
    st.subheader("🌾 Calculadora Sencilla para el Productor: ¿Cuánto Vale Tu Cosecha Hoy?")
    st.write(
        "Aquí no necesitas leer gráficas complicadas. Elige tu cultivo, tu municipio en Colima "
        "y cuántas rejas o kilos tienes para ver **cuánto dinero libre recibes hoy**."
    )

    p1, p2, p3, p4 = st.columns([1.4, 1.4, 1.3, 1.5])
    cultivo = p1.selectbox(
        "1. ¿Qué cosechaste?", sorted(df_oro["cultivo"].unique()), key="prod_cultivo"
    )
    municipio = p2.selectbox("2. ¿En qué municipio estás?", list(NODOS_PRODUCTORES_COLIMA.keys()))
    modo_unidad = p3.radio("3. ¿Cómo cuentas tu fruta?", ["Rejas de 20 kg", "Kilos sueltos"], horizontal=False)
    if modo_unidad == "Rejas de 20 kg":
        rejas = p4.number_input("¿Cuántas rejas de 20 kg tienes?", min_value=1, max_value=250, value=10, step=1)
        kilos_mios = float(rejas * 20.0)
    else:
        kilos_mios = float(
            p4.number_input("¿Cuántos kilos tienes?", min_value=15.0, max_value=5000.0, value=200.0, step=10.0)
        )

    comprador = st.selectbox(
        "🏪 Comprador formal en Colima al que irá el camión compartido:",
        list(COMPRADORES_ANCLA_COLIMA.keys()),
        index=1,
    )
    precio_colima, fecha_sniim = obtener_cotizacion_actual_plaza(df_oro, cultivo, "Colima")
    temp_muni, lluvia_muni, _ = obtener_clima_reciente_municipio(df_oro, municipio)

    tipo_sem, tit_sem, txt_sem = generar_semaforo_cosecha(
        precio_colima, precio_pronosticado_colima, temp_muni, lluvia_muni, municipio
    )
    if tipo_sem == "warning":
        st.warning(f"**{tit_sem}**\n\n{txt_sem}")
    else:
        st.success(f"**{tit_sem}**\n\n{txt_sem}")

    info_comp = COMPRADORES_ANCLA_COLIMA[comprador]
    rutas_sub = df_rutas[df_rutas["comprador_ancla"] == comprador]
    ofertas_simuladas = [
        *st.session_state["libro_ofertas_pool"],
        {"id_oferta": "👉 TU COSECHA", "municipio": municipio, "calidad": "Primera", "kilos_ofrecidos": kilos_mios},
    ]
    df_liq, res = liquidar_pool_multiproductor(
        ofertas_simuladas,
        precio_colima,
        float(info_comp["prima_comercial_pct"]),
        float(info_comp["demanda_lote_kg"]),
        rutas_sub,
        temp_muni,
    )

    _renderizar_tarjetas_dinero(kilos_mios, res, comprador, fecha_sniim)
    _renderizar_explicacion_peso_por_peso(float(res["precio_venta_comprador_kg"]), res)

    st.markdown("#### 🚛 Camión compartido con otros productores de Colima")
    faltan_kg = max(0.0, float(info_comp["demanda_lote_kg"]) - float(res["peso_consolidado_kg"]))
    texto_barra = (
        f"Llevamos {res['peso_consolidado_kg']:,.0f} kg de {info_comp['demanda_lote_kg']:,.0f} kg "
        f"que pide {comprador} ({res['porcentaje_llenado_pedido']}%) — Vehículo: {res['vehiculo_asignado']}"
    )
    if faltan_kg > 0:
        texto_barra += f" (Faltan {faltan_kg:,.0f} kg para llenar el pedido)"
    st.progress(min(1.0, float(res["porcentaje_llenado_pedido"]) / 100.0), text=texto_barra)

    b1, b2 = st.columns([1, 1])
    if b1.button("➕ Dejar anotada mi cosecha en este camión", type="primary"):
        num_v = len(st.session_state["libro_ofertas_pool"]) + 1
        st.session_state["libro_ofertas_pool"].append(
            {"id_oferta": f"Productor {num_v}", "municipio": municipio, "calidad": "Primera", "kilos_ofrecidos": kilos_mios}
        )
        st.rerun()
    if b2.button("🔄 Reiniciar ejemplo de vecinos"):
        st.session_state["libro_ofertas_pool"] = [dict(x) for x in OFERTAS_VECINOS_EJEMPLO]
        st.rerun()

    df_amigable = pd.DataFrame(
        {
            "Quién aporta": df_liq["id_oferta"],
            "Municipio": df_liq["municipio"],
            "Kilos en el camión": df_liq["kilos_asignados"],
            "Equivalente en rejas (20 kg)": (df_liq["kilos_asignados"] / 20.0).round(1),
            "Distancia carretera (km)": df_liq["distancia_km"],
            "Con el coyote recibiría ($)": df_liq["pago_coyote_total_mxn"],
            "Libre con AgroPulse recibe ($)": df_liq["pago_agropulse_total_mxn"],
            "Ganancia extra ($)": df_liq["ganancia_extra_productor_mxn"],
        }
    )
    st.dataframe(df_amigable, hide_index=True, width="stretch")
    st.divider()
    _renderizar_comparador_ciudades_sencillo(df_oro, cultivo)
