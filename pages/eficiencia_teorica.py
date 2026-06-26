import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from st_supabase_connection import SupabaseConnection
from streamlit_echarts import st_echarts
from utils.vars_efiencia import variables_actividades, variables_eficiencia
from utils.funciones_dashboard import calcular_dias_cobertura, filtrar_datos, MEXICO_TZ
from utils.auth import require_login
from utils.tabla_interactiva import render_interactive_table

require_login()

conn = st.connection("supabase", type=SupabaseConnection)

# Vacantes activas (eficiencia teórica)
vacantes_activas_resp = (
    conn.table("vacantes")
    .select("id, vacantes_solicitadas, fecha_autorizacion, estatus_solicitud, fase_proceso")
    .neq("fase_proceso", "CONTRATADO")
    .not_.in_("estatus_solicitud", ["FINALIZADO", "PAUSADO", "CANCELADO", "RECHAZADA"])
    .not_.is_("fecha_autorizacion", None)
    .execute()
)
vacantes_df = pd.DataFrame(vacantes_activas_resp.data)

# Todos los registros de vacantes (igual que el dashboard, sin filtros en Supabase)
todas_vacantes_resp = (
    conn.table("vacantes")
    .select("""
        id, fecha_solicitud, fecha_autorizacion, fecha_cobertura,
        funcion_area_vacante, responsable_vacante, empresa_vacante, puesto_vacante,
        vacantes_solicitadas, vacantes_contratados, estatus_solicitud, fase_proceso
    """)
    .execute()
)
df_todas = pd.DataFrame(todas_vacantes_resp.data)

if not df_todas.empty:
    df_todas["fecha_autorizacion"] = pd.to_datetime(df_todas["fecha_autorizacion"])
    df_todas["fecha_cobertura"]    = pd.to_datetime(df_todas["fecha_cobertura"])
    df_todas["fecha_solicitud"]    = pd.to_datetime(df_todas["fecha_solicitud"])
    df_todas["vacantes_contratados"] = pd.to_numeric(df_todas["vacantes_contratados"], errors="coerce").fillna(0).astype(int)
    df_todas["vacantes_solicitadas"] = pd.to_numeric(df_todas["vacantes_solicitadas"], errors="coerce").fillna(0).astype(int)

# Replicar exactamente el criterio del dashboard: vacantes_contratados > 0
df_sla_raw = df_todas[df_todas["vacantes_contratados"] > 0].copy() if not df_todas.empty else pd.DataFrame()

if not df_sla_raw.empty:
    df_sla_raw["dias"] = df_sla_raw.apply(calcular_dias_cobertura, axis=1)
    df_sla_raw = df_sla_raw[df_sla_raw["dias"].notna() & (df_sla_raw["dias"] >= 0)]

SLA_OPERATIVA      = 15
SLA_ADMINISTRATIVA = 45

_TEAL   = "#14b8a6"
_INDIGO = "#6366f1"
_AMBER  = "#f59e0b"
_TEXT   = "rgba(255,255,255,0.65)"
_GRID   = "rgba(255,255,255,0.06)"

_EJECUTIVOS = ["DIEGO", "YULIANA", "LETICIA", "ELENA"]

def _match_ejecutivo(nombre):
    for palabra in str(nombre).upper().split():
        if palabra in _EJECUTIVOS:
            return palabra
    return None


st.markdown("""
<div class="dash-header">
    <span class="dash-title">Indicador de Eficiencia Teórica</span>
    <span class="dash-badge">Atracción de Talento</span>
</div>
""", unsafe_allow_html=True)

# Filtros para el tab SLA
años_sla = sorted(
    df_todas["fecha_cobertura"].dt.year.dropna().unique().astype(int).tolist(),
    reverse=True
) if not df_todas.empty else [datetime.now(MEXICO_TZ).year]

from utils.funciones_dashboard import meses_es

col_f1, col_f2, col_f3 = st.columns([2, 2, 2])
with col_f1:
    tipo_filtro_sla = st.selectbox(
        ":material/filter_alt: Filtrar SLA por",
        ["Todo el tiempo", "Por año", "Por mes", "Por rango de fechas"],
        key="filtro_sla"
    )

año_sla = mes_sla = fecha_ini_sla = fecha_fin_sla = None

if tipo_filtro_sla in ["Por año", "Por mes"]:
    with col_f2:
        año_sla = st.selectbox("Año", años_sla, key="año_sla")

if tipo_filtro_sla == "Por mes" and año_sla:
    with col_f3:
        mes_nombre = st.selectbox("Mes", list(meses_es.values()), key="mes_sla",
                                  index=datetime.now(MEXICO_TZ).month - 1)
        mes_sla = list(meses_es.keys())[list(meses_es.values()).index(mes_nombre)]

if tipo_filtro_sla == "Por rango de fechas":
    with col_f2:
        fecha_ini_sla = st.date_input("Desde", value=datetime.now(MEXICO_TZ).date() - timedelta(days=90),
                                      format="DD/MM/YYYY", key="fi_sla")
    with col_f3:
        fecha_fin_sla = st.date_input("Hasta", value=datetime.now(MEXICO_TZ).date(),
                                      format="DD/MM/YYYY", key="ff_sla")

df_sla = filtrar_datos(
    df_sla_raw, "fecha_cobertura", tipo_filtro_sla,
    año=año_sla, mes=mes_sla,
    fecha_inicio=fecha_ini_sla, fecha_fin=fecha_fin_sla
)

st.markdown("---")

tab_eficiencia, tab_sla = st.tabs(["Eficiencia Teórica", "SLA de Cobertura"])

# Tab Eficiencia Teórica
with tab_eficiencia:
    revision_requisicion, publicacion_vacante, filtro_candidatos, coordinar_entrevistas, \
    formato_competencias_perfil, entrevistas, seleccion_final, seguimiento, tiempo_total = variables_actividades()
    personas_atraccion, horas_diarias, dias_laborales_mes = variables_eficiencia()

    vacantes_activas = int(vacantes_df['vacantes_solicitadas'].astype(int).sum()) if not vacantes_df.empty else 0

    df_actividades = pd.DataFrame({
        "Actividad": [
            "Revisión requisición", "Publicación vacante", "Filtro de candidatos",
            "Coordinar entrevistas", "Formato de competencias y perfil", "Entrevistas",
            "Selección final", "Envío Admin. de personal / seguimiento",
        ],
        "Tiempo (hrs)": [
            revision_requisicion, publicacion_vacante, filtro_candidatos,
            coordinar_entrevistas, formato_competencias_perfil, entrevistas,
            seleccion_final, seguimiento,
        ],
    })
    render_interactive_table(df_actividades, height=360)

    st.divider()

    horas_trabajador  = personas_atraccion * horas_diarias * dias_laborales_mes
    capacidad_teorica = horas_trabajador / tiempo_total
    eficiencia_teorica = (vacantes_activas / capacidad_teorica) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Horas Trabajador",  f"{horas_trabajador:,} hrs")
    c2.metric("Capacidad Teórica", f"{capacidad_teorica:.2f}")
    c3.metric("Eficiencia Teórica", f"{eficiencia_teorica:.2f}%")

    st.divider()

    indicador = pd.DataFrame({
        "Resultado": [
            ":material/trending_down: Menor a 80%",
            ":material/trending_flat: Entre 80% y 100%",
            ":material/trending_up: Mayor a 100%",
            ":material/arrows_more_up: Mayor a 150%",
        ],
        "Interpretación": [
            ":blue[Capacidad disponible / subutilización]",
            ":green[Operación estable]",
            ":orange[Sobrecarga operativa]",
            ":red[Riesgo de saturación del proceso]",
        ],
    }).set_index("Resultado")
    st.table(indicador)

# Tab SLA
with tab_sla:
    if df_sla.empty:
        st.info("No hay datos de vacantes contratadas para calcular el SLA.")
        st.stop()

    df_op  = df_sla[df_sla["funcion_area_vacante"] == "OPERATIVA"]
    df_adm = df_sla[df_sla["funcion_area_vacante"] == "ADMINISTRATIVA"]

    def _stats(df, meta):
        if df.empty:
            return 0, 0.0, 0.0
        total  = len(df)
        dentro = int((df["dias"] <= meta).sum())
        return total, dentro / total * 100, df["dias"].mean()

    total_op,  pct_op,  avg_op  = _stats(df_op,  SLA_OPERATIVA)
    total_adm, pct_adm, avg_adm = _stats(df_adm, SLA_ADMINISTRATIVA)

    # Métricas
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("SLA Operativas",             f"{pct_op:.1f}%",  delta=f"Meta: {SLA_OPERATIVA} días",      delta_color="off")
    c2.metric("Días prom. Operativas",      f"{avg_op:.1f}",   delta="En meta" if avg_op  <= SLA_OPERATIVA      else "Fuera de meta", delta_color="normal" if avg_op  <= SLA_OPERATIVA      else "inverse")
    c3.metric("SLA Administrativas",        f"{pct_adm:.1f}%", delta=f"Meta: {SLA_ADMINISTRATIVA} días", delta_color="off")
    c4.metric("Días prom. Administrativas", f"{avg_adm:.1f}",  delta="En meta" if avg_adm <= SLA_ADMINISTRATIVA else "Fuera de meta", delta_color="normal" if avg_adm <= SLA_ADMINISTRATIVA else "inverse")

    st.divider()

    # SLA por ejecutivo
    st.write("### Días promedio de cobertura por ejecutivo")

    df_sla["ejecutivo"] = df_sla["responsable_vacante"].fillna("").apply(_match_ejecutivo)
    df_ejec = df_sla[df_sla["ejecutivo"].isin(_EJECUTIVOS)]

    if not df_ejec.empty:
        resumen = df_ejec.groupby(["ejecutivo", "funcion_area_vacante"])["dias"].mean()

        def _val(ejec, area):
            try:
                return round(float(resumen.loc[(ejec, area)]), 1)
            except KeyError:
                return None

        op_vals  = [_val(e, "OPERATIVA")      for e in _EJECUTIVOS]
        adm_vals = [_val(e, "ADMINISTRATIVA") for e in _EJECUTIVOS]

        options_ejec = {
            "color": [_TEAL, _INDIGO],
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "backgroundColor": "rgba(20,20,20,0.92)",
                "borderColor": "rgba(255,255,255,0.08)",
                "textStyle": {"color": "#ffffff"},
            },
            "legend": {"data": ["Operativa", "Administrativa"], "textStyle": {"color": _TEXT}, "top": "4%"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "top": "15%", "containLabel": True},
            "xAxis": {"type": "category", "data": _EJECUTIVOS, "axisLabel": {"color": _TEXT}},
            "yAxis": {
                "type": "value",
                "name": "Días promedio",
                "nameTextStyle": {"color": _TEXT},
                "axisLabel": {"color": _TEXT},
                "splitLine": {"lineStyle": {"color": _GRID}},
            },
            "series": [
                {
                    "name": "Operativa",
                    "type": "bar",
                    "data": op_vals,
                    "itemStyle": {"color": _TEAL, "borderRadius": [4, 4, 0, 0]},
                    "label": {"show": True, "position": "top", "color": _TEXT, "fontSize": 11, "formatter": "{c}"},
                    "markLine": {
                        "data": [{"yAxis": SLA_OPERATIVA}],
                        "lineStyle": {"color": _TEAL, "type": "dashed"},
                        "label": {"formatter": f"Meta {SLA_OPERATIVA}d", "color": _TEAL},
                    },
                },
                {
                    "name": "Administrativa",
                    "type": "bar",
                    "data": adm_vals,
                    "itemStyle": {"color": _INDIGO, "borderRadius": [4, 4, 0, 0]},
                    "label": {"show": True, "position": "top", "color": _TEXT, "fontSize": 11, "formatter": "{c}"},
                    "markLine": {
                        "data": [{"yAxis": SLA_ADMINISTRATIVA}],
                        "lineStyle": {"color": _INDIGO, "type": "dashed"},
                        "label": {"formatter": f"Meta {SLA_ADMINISTRATIVA}d", "color": _INDIGO},
                    },
                },
            ],
        }
        st_echarts(options_ejec, height="380px", key="sla_ejecutivo")

    st.divider()

    # Tendencia mensual
    st.write("### Tendencia mensual de días de cobertura")

    df_sla["mes"] = df_sla["fecha_cobertura"].dt.to_period("M").astype(str)
    tendencia = df_sla.groupby(["mes", "funcion_area_vacante"])["dias"].mean()
    meses = sorted(df_sla["mes"].unique().tolist())

    def _trend(area):
        vals = []
        for m in meses:
            try:
                vals.append(round(float(tendencia.loc[(m, area)]), 1))
            except KeyError:
                vals.append(None)
        return vals

    options_trend = {
        "color": [_TEAL, _INDIGO],
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "legend": {"data": ["Operativa", "Administrativa"], "textStyle": {"color": _TEXT}},
        "xAxis": {"type": "category", "data": meses, "axisLabel": {"rotate": 45, "color": _TEXT}},
        "yAxis": {
            "type": "value",
            "name": "Días promedio",
            "nameTextStyle": {"color": _TEXT},
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": [
            {
                "name": "Operativa",
                "type": "line",
                "data": _trend("OPERATIVA"),
                "smooth": True,
                "connectNulls": True,
                "lineStyle": {"color": _TEAL},
                "itemStyle": {"color": _TEAL},
                "areaStyle": {"color": "rgba(20,184,166,0.12)"},
                "markLine": {
                    "data": [{"yAxis": SLA_OPERATIVA}],
                    "lineStyle": {"color": _TEAL, "type": "dashed", "opacity": 0.6},
                    "label": {"formatter": f"Meta {SLA_OPERATIVA}d", "color": _TEAL},
                },
            },
            {
                "name": "Administrativa",
                "type": "line",
                "data": _trend("ADMINISTRATIVA"),
                "smooth": True,
                "connectNulls": True,
                "lineStyle": {"color": _INDIGO},
                "itemStyle": {"color": _INDIGO},
                "areaStyle": {"color": "rgba(99,102,241,0.12)"},
                "markLine": {
                    "data": [{"yAxis": SLA_ADMINISTRATIVA}],
                    "lineStyle": {"color": _INDIGO, "type": "dashed", "opacity": 0.6},
                    "label": {"formatter": f"Meta {SLA_ADMINISTRATIVA}d", "color": _INDIGO},
                },
            },
        ],
    }
    st_echarts(options_trend, height="380px", key="sla_tendencia")
