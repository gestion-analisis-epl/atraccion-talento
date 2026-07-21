import streamlit as st
import pandas as pd
import calendar
from datetime import date
from st_supabase_connection import SupabaseConnection
from utils.auth import require_login
from config.opciones import AREAS
from utils.funciones_comparativa import (
    metricas_comparativas,
    grafica_comparativa_agrupada,
    grafica_ejecutivos_por_anio,
    metricas_nuevo_reemplazo,
    metricas_periodo,
    grafica_mensual_periodo,
    grafica_ejecutivos_periodo,
    grafica_mensual_periodo_comparado,
    grafica_ejecutivos_periodo_comparado,
)

require_login()

conn = st.connection("supabase", type=SupabaseConnection)

st.markdown("""
<div class="dash-header">
    <span class="dash-title">Comparación Anual</span>
</div>
""", unsafe_allow_html=True)

data_altas = (
    conn.table("altas")
    .select("id, fecha_alta, contratados_alta, empresa_alta, area_alta, medio_reclutamiento_alta, responsable_alta")
    .execute()
)
df_altas = pd.DataFrame(data_altas.data)

if df_altas.empty:
    st.info("No hay datos de contrataciones disponibles.")
    st.stop()

df_altas["fecha_alta"]       = pd.to_datetime(df_altas["fecha_alta"])
df_altas["contratados_alta"] = df_altas["contratados_alta"].astype(int)

data_vacantes = (
    conn.table("vacantes")
    .select("id, fecha_solicitud, tipo_solicitud, fase_proceso, vacantes_contratados, funcion_area_vacante")
    .execute()
)
df_vacantes = pd.DataFrame(data_vacantes.data)
if not df_vacantes.empty:
    df_vacantes["fecha_solicitud"]      = pd.to_datetime(df_vacantes["fecha_solicitud"])
    df_vacantes["vacantes_contratados"] = (
        pd.to_numeric(df_vacantes["vacantes_contratados"], errors="coerce").fillna(0).astype(int)
    )

area_seleccionada = st.selectbox(
    ":material/filter_alt: Función de área",
    ["Todas"] + list(AREAS),
    index=0,
)
if area_seleccionada != "Todas":
    df_altas = df_altas[df_altas["area_alta"] == area_seleccionada]
    if not df_vacantes.empty:
        df_vacantes = df_vacantes[df_vacantes["funcion_area_vacante"] == area_seleccionada]

hoy  = date.today()
AÑOS = [2024, 2025, 2026]


def _safe_date(año: int, mes: int, dia: int) -> date:
    return date(año, mes, min(dia, calendar.monthrange(año, mes)[1]))


def _metricas_por_año(año: int, fi, ff):
    fi_ts = pd.Timestamp(fi)
    ff_ts = pd.Timestamp(ff)

    total_altas = int(
        df_altas[
            (df_altas["fecha_alta"] >= fi_ts) & (df_altas["fecha_alta"] <= ff_ts)
        ]["contratados_alta"].sum()
    )
    total_nuevo = total_reemplazo = 0
    if not df_vacantes.empty:
        mask = (
            (df_vacantes["fecha_solicitud"] >= fi_ts) &
            (df_vacantes["fecha_solicitud"] <= ff_ts) &
            (df_vacantes["fase_proceso"] == "CONTRATADO")
        )
        df_p = df_vacantes[mask]
        total_nuevo     = int(df_p[df_p["tipo_solicitud"] == "NUEVO"]["vacantes_contratados"].sum())
        total_reemplazo = int(df_p[df_p["tipo_solicitud"] == "REEMPLAZO"]["vacantes_contratados"].sum())

    st.markdown(f"**{año}**")
    st.metric("Contrataciones", f"{total_altas:,}")
    st.metric("Nuevas", f"{total_nuevo:,}")
    st.metric("Reemplazos", f"{total_reemplazo:,}")


tab_general, tab_2024, tab_2025, tab_2026, tab_comp = st.tabs(
    ["General", "2024", "2025", "2026", "Comparativa"]
)

# ── GENERAL ──────────────────────────────────────────────────────────────────
with tab_general:
    st.caption("Selecciona el rango de día y mes. El año del calendario se ignora — el período se aplica a 2024, 2025 y 2026.")
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        ref_ini = st.date_input(
            "Desde (día/mes)",
            value=date(hoy.year, 1, 1),
            format="DD/MM/YYYY",
            key="gen_ini",
        )
    with col2:
        ref_fin = st.date_input(
            "Hasta (día/mes)",
            value=date(hoy.year, 12, 31),
            format="DD/MM/YYYY",
            key="gen_fin",
        )

    fechas_años = [
        (año, _safe_date(año, ref_ini.month, ref_ini.day),
              _safe_date(año, ref_fin.month, ref_fin.day))
        for año in AÑOS
    ]

    st.divider()

    st.write("### Métricas del período")
    mc1, mc2, mc3 = st.columns(3)
    for col, (año, fi, ff) in zip([mc1, mc2, mc3], fechas_años):
        with col:
            _metricas_por_año(año, fi, ff)

    st.divider()

    st.write("### Contrataciones por mes")
    grafica_mensual_periodo_comparado(df_altas, fechas_años, key="gen_mensual")

    st.divider()

    st.write("### Contrataciones por ejecutivo")
    grafica_ejecutivos_periodo_comparado(df_altas, fechas_años, key="gen_ejec")

# ── TABS POR AÑO ─────────────────────────────────────────────────────────────
for tab, año in zip([tab_2024, tab_2025, tab_2026], AÑOS):
    with tab:
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            fecha_ini = st.date_input(
                "Desde",
                value=date(año, 1, 1),
                min_value=date(año, 1, 1),
                max_value=date(año, 12, 31),
                format="DD/MM/YYYY",
                key=f"fi_{año}",
            )
        with col2:
            fecha_fin = st.date_input(
                "Hasta",
                value=min(date(año, 12, 31), hoy),
                min_value=date(año, 1, 1),
                max_value=date(año, 12, 31),
                format="DD/MM/YYYY",
                key=f"ff_{año}",
            )

        if fecha_ini > fecha_fin:
            st.warning("La fecha de inicio debe ser anterior a la fecha final.")
        else:
            st.write("### Métricas del período")
            metricas_periodo(df_altas, df_vacantes, fecha_ini, fecha_fin)

            st.divider()

            st.write("### Contrataciones por mes")
            grafica_mensual_periodo(df_altas, fecha_ini, fecha_fin, key=f"mensual_{año}")

            st.divider()

            st.write("### Contrataciones por ejecutivo")
            grafica_ejecutivos_periodo(df_altas, fecha_ini, fecha_fin, key=f"ejec_{año}")

# ── COMPARATIVA ───────────────────────────────────────────────────────────────
with tab_comp:
    st.write("### Contrataciones por año")
    metricas_comparativas(df_altas)

    st.divider()

    st.write("### Comparativa agrupada por año")
    grafica_comparativa_agrupada(df_altas, key="comp_agrupada")

    st.divider()

    st.write("### Contrataciones por ejecutivo")
    grafica_ejecutivos_por_anio(df_altas, key="comp_ejec_anio")

    st.divider()

    st.write("### Vacantes contratadas: Nuevo vs Reemplazo")
    metricas_nuevo_reemplazo(df_vacantes)
