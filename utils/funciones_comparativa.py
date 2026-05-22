import streamlit as st
import pandas as pd
from streamlit_echarts import st_echarts

_TEAL   = "#14b8a6"
_INDIGO = "#6366f1"
_AMBER  = "#f59e0b"
_TEXT   = "rgba(255,255,255,0.65)"
_GRID   = "rgba(255,255,255,0.06)"

empresas_map = {
    "CORPORATIVO PUBLICITARIO MAO SA DE CV": "MAO",
    "DRAUBEN SA DE CV": "DRAUBEN",
    "ESPECIALISTAS PROFESIONALES DE LEON SA DE CV": "EPL",
    "F2 CONSULTING GROUP SA DE CV": "F2",
    "FICORMA SA DE CV": "FICORMA",
    "KRONOS AMBIENTAL SAPI DE CV": "KRONOS",
    "MARKETING EN PUBLICIDAD DE QUERETARO SA DE CV": "MKT QRO",
    "MONTAJE SUPERVISION Y CONSTRUCCION SA DE CV": "MSC",
    "LUMINA PANTALLAS DIGITALES SA DE CV": "LUMINA",
    "SERVICIOS DE ANUNCIOS PUBLICITARIOS SA DE CV": "SAP",
    "SICMART SA DE CV": "SICMART",
    "THE BEST MARKETING SA DE CV": "BEST MKT",
    "VINCI GERENCIA ORGANIZACIONAL SA DE CV": "VINCI",
}

meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}

meses_corto = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}

trimestres = {
    1: {"nombre": "T1 (Enero-Marzo)",      "meses": [1, 2, 3]},
    2: {"nombre": "T2 (Abril-Junio)",       "meses": [4, 5, 6]},
    3: {"nombre": "T3 (Julio-Septiembre)",  "meses": [7, 8, 9]},
    4: {"nombre": "T4 (Octubre-Diciembre)", "meses": [10, 11, 12]},
}

_EJECUTIVOS = ["DIEGO", "YULIANA", "LETICIA", "ELENA"]


def metricas_comparativas(df_altas: pd.DataFrame):
    if df_altas.empty:
        st.info("No hay datos disponibles.")
        return

    df = df_altas.copy()
    df["contratados_alta"] = df["contratados_alta"].astype(int)
    años = sorted(df["fecha_alta"].dt.year.dropna().unique().astype(int).tolist())

    totales = {
        año: int(df[df["fecha_alta"].dt.year == año]["contratados_alta"].sum())
        for año in años
    }

    cols = st.columns(len(años))
    for i, año in enumerate(años):
        total = totales[año]
        prev  = totales.get(año - 1)
        if prev and prev > 0:
            cambio = (total - prev) / prev * 100
            delta  = f"{cambio:+.1f}%"
        else:
            delta = None
        cols[i].metric(label=str(año), value=f"{total:,}", delta=delta)


def grafica_mensual_por_anio(df_altas: pd.DataFrame, año: int, key: str = None):
    if df_altas.empty:
        st.info("No hay datos disponibles.")
        return

    df = df_altas.copy()
    df["contratados_alta"] = df["contratados_alta"].astype(int)
    df = df[df["fecha_alta"].dt.year == año]

    if df.empty:
        st.info(f"No hay contrataciones registradas en {año}.")
        return

    resumen = (
        df.groupby(df["fecha_alta"].dt.month)["contratados_alta"]
        .sum()
        .reindex(range(1, 13), fill_value=0)
        .reset_index()
    )
    resumen.columns = ["mes", "contratados"]

    valores       = [int(v) for v in resumen["contratados"]]
    nombres_meses = [meses_corto[m] for m in resumen["mes"]]

    options = {
        "color": [_TEAL],
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": nombres_meses,
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": [
            {
                "name": f"Contrataciones {año}",
                "type": "bar",
                "data": valores,
                "itemStyle": {"color": _TEAL, "borderRadius": [4, 4, 0, 0]},
                "label": {
                    "show": True,
                    "position": "top",
                    "color": _TEXT,
                    "fontSize": 11,
                    "formatter": "{c}",
                },
                "areaStyle": {"color": "rgba(20,184,166,0.12)"},
                "smooth": True,
            }
        ],
    }

    st_echarts(options, height="420px", width="100%", key=key)


def grafica_comparativa_agrupada(df_altas: pd.DataFrame, key: str = None):
    if df_altas.empty:
        st.info("No hay datos disponibles.")
        return

    df = df_altas.copy()
    df["contratados_alta"] = df["contratados_alta"].astype(int)

    años = sorted(df["fecha_alta"].dt.year.dropna().unique().astype(int).tolist())
    if len(años) < 2:
        st.info("Se necesitan al menos dos años de datos para mostrar la comparativa agrupada.")
        return

    colores = [_TEAL, _INDIGO, _AMBER, "#2dd4bf", "#818cf8"]

    series = []
    for i, año in enumerate(años):
        df_año = df[df["fecha_alta"].dt.year == año]
        valores = (
            df_año.groupby(df_año["fecha_alta"].dt.month)["contratados_alta"]
            .sum()
            .reindex(range(1, 13), fill_value=0)
            .tolist()
        )
        color = colores[i % len(colores)]
        series.append({
            "name": str(año),
            "type": "bar",
            "data": [int(v) for v in valores],
            "itemStyle": {"color": color, "borderRadius": [4, 4, 0, 0]},
            "label": {"show": False},
            "emphasis": {"focus": "series"},
            "areaStyle": {"color": f"{color}26"},
            "smooth": True,
        })

    options = {
        "color": colores,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "legend": {
            "data": [str(a) for a in años],
            "textStyle": {"color": _TEXT},
            "top": "4%",
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": list(meses_corto.values()),
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": series,
    }

    st_echarts(options, height="420px", width="100%", key=key)


def metricas_nuevo_reemplazo(df_vacantes: pd.DataFrame):
    if df_vacantes.empty:
        st.info("No hay datos de vacantes disponibles.")
        return

    df = df_vacantes[df_vacantes["fase_proceso"] == "CONTRATADO"].copy()
    if df.empty:
        st.info("No hay vacantes con estatus Contratado.")
        return

    años = sorted(
        [a for a in df["fecha_solicitud"].dt.year.dropna().unique().astype(int).tolist() if a >= 2024]
    )

    for tipo, label in [("NUEVO", "Nuevas"), ("REEMPLAZO", "Reemplazos")]:
        st.markdown(f"#### {label}")
        totales = {
            año: int(
                df[
                    (df["fecha_solicitud"].dt.year == año) &
                    (df["tipo_solicitud"] == tipo)
                ]["vacantes_contratados"].sum()
            )
            for año in años
        }
        cols = st.columns(len(años))
        for i, año in enumerate(años):
            total = totales[año]
            prev  = totales.get(año - 1)
            if prev and prev > 0:
                cambio = (total - prev) / prev * 100
                delta  = f"{cambio:+.1f}%"
            else:
                delta = None
            cols[i].metric(label=str(año), value=f"{total:,}", delta=delta)


def grafica_ejecutivos_por_anio(df_altas: pd.DataFrame, key: str = None):
    if df_altas.empty:
        st.info("No hay datos disponibles.")
        return

    df = df_altas.copy()
    df["contratados_alta"] = df["contratados_alta"].astype(int)

    def _match_ejecutivo(nombre: str) -> str:
        for palabra in str(nombre).upper().split():
            if palabra in _EJECUTIVOS:
                return palabra
        return ""

    df["primer_nombre"] = df["responsable_alta"].fillna("").apply(_match_ejecutivo)
    df = df[df["primer_nombre"].isin(_EJECUTIVOS)]

    if df.empty:
        st.info("No hay datos para los ejecutivos seleccionados.")
        return

    años = sorted(df["fecha_alta"].dt.year.dropna().unique().astype(int).tolist())
    colores = [_TEAL, _INDIGO, _AMBER, "#2dd4bf", "#818cf8"]

    series = []
    for i, año in enumerate(años):
        df_año = df[df["fecha_alta"].dt.year == año]
        valores = [
            int(df_año[df_año["primer_nombre"] == ejec]["contratados_alta"].sum())
            for ejec in _EJECUTIVOS
        ]
        color = colores[i % len(colores)]
        series.append({
            "name": str(año),
            "type": "bar",
            "data": valores,
            "itemStyle": {"color": color, "borderRadius": [4, 4, 0, 0]},
            "label": {
                "show": True,
                "position": "top",
                "color": _TEXT,
                "fontSize": 11,
                "formatter": "{c}",
            },
            "emphasis": {"focus": "series"},
        })

    options = {
        "color": colores,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "legend": {
            "data": [str(a) for a in años],
            "textStyle": {"color": _TEXT},
            "top": "4%",
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": _EJECUTIVOS,
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": series,
    }

    st_echarts(options, height="420px", width="100%", key=key)


def metricas_periodo(df_altas: pd.DataFrame, df_vacantes: pd.DataFrame, fecha_ini, fecha_fin):
    fi = pd.Timestamp(fecha_ini)
    ff = pd.Timestamp(fecha_fin)

    total_altas = int(
        df_altas[
            (df_altas["fecha_alta"] >= fi) & (df_altas["fecha_alta"] <= ff)
        ]["contratados_alta"].sum()
    )

    total_nuevo = total_reemplazo = 0
    if not df_vacantes.empty:
        mask = (
            (df_vacantes["fecha_solicitud"] >= fi) &
            (df_vacantes["fecha_solicitud"] <= ff) &
            (df_vacantes["fase_proceso"] == "CONTRATADO")
        )
        df_p = df_vacantes[mask]
        total_nuevo     = int(df_p[df_p["tipo_solicitud"] == "NUEVO"]["vacantes_contratados"].sum())
        total_reemplazo = int(df_p[df_p["tipo_solicitud"] == "REEMPLAZO"]["vacantes_contratados"].sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Contrataciones", f"{total_altas:,}")
    c2.metric("Nuevas", f"{total_nuevo:,}")
    c3.metric("Reemplazos", f"{total_reemplazo:,}")


def grafica_mensual_periodo(df_altas: pd.DataFrame, fecha_ini, fecha_fin, key: str = None):
    fi = pd.Timestamp(fecha_ini)
    ff = pd.Timestamp(fecha_fin)

    df = df_altas[(df_altas["fecha_alta"] >= fi) & (df_altas["fecha_alta"] <= ff)].copy()

    if df.empty:
        st.info("No hay contrataciones en el período seleccionado.")
        return

    meses_rango = list(range(fecha_ini.month, fecha_fin.month + 1))
    resumen = (
        df.groupby(df["fecha_alta"].dt.month)["contratados_alta"]
        .sum()
        .reindex(meses_rango, fill_value=0)
        .reset_index()
    )
    resumen.columns = ["mes", "contratados"]

    valores       = [int(v) for v in resumen["contratados"]]
    nombres_meses = [meses_corto[m] for m in resumen["mes"]]

    options = {
        "color": [_TEAL],
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": nombres_meses,
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": [{
            "name": "Contrataciones",
            "type": "bar",
            "data": valores,
            "itemStyle": {"color": _TEAL, "borderRadius": [4, 4, 0, 0]},
            "label": {
                "show": True,
                "position": "top",
                "color": _TEXT,
                "fontSize": 11,
                "formatter": "{c}",
            },
            "areaStyle": {"color": "rgba(20,184,166,0.12)"},
            "smooth": True,
        }],
    }

    st_echarts(options, height="380px", width="100%", key=key)


def grafica_ejecutivos_periodo(df_altas: pd.DataFrame, fecha_ini, fecha_fin, key: str = None):
    fi = pd.Timestamp(fecha_ini)
    ff = pd.Timestamp(fecha_fin)

    df = df_altas[(df_altas["fecha_alta"] >= fi) & (df_altas["fecha_alta"] <= ff)].copy()

    def _match(nombre: str) -> str:
        for palabra in str(nombre).upper().split():
            if palabra in _EJECUTIVOS:
                return palabra
        return ""

    df["ejecutivo"] = df["responsable_alta"].fillna("").apply(_match)
    df = df[df["ejecutivo"].isin(_EJECUTIVOS)]

    if df.empty:
        st.info("No hay datos para los ejecutivos en este período.")
        return

    colores = [_TEAL, _INDIGO, _AMBER, "#2dd4bf"]
    valores = [int(df[df["ejecutivo"] == e]["contratados_alta"].sum()) for e in _EJECUTIVOS]

    options = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": _EJECUTIVOS,
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": [{
            "name": "Contrataciones",
            "type": "bar",
            "data": [
                {"value": v, "itemStyle": {"color": colores[i % len(colores)], "borderRadius": [4, 4, 0, 0]}}
                for i, v in enumerate(valores)
            ],
            "label": {
                "show": True,
                "position": "top",
                "color": _TEXT,
                "fontSize": 11,
                "formatter": "{c}",
            },
        }],
    }

    st_echarts(options, height="380px", width="100%", key=key)


def grafica_mensual_periodo_comparado(df_altas: pd.DataFrame, fechas_años: list, key: str = None):
    """fechas_años: [(año, fecha_ini, fecha_fin), ...]"""
    colores = [_TEAL, _INDIGO, _AMBER, "#2dd4bf", "#818cf8"]

    ref_ini = fechas_años[0][1]
    ref_fin = fechas_años[0][2]
    meses_rango = list(range(ref_ini.month, ref_fin.month + 1))

    series = []
    for i, (año, fi, ff) in enumerate(fechas_años):
        df_f = df_altas[
            (df_altas["fecha_alta"] >= pd.Timestamp(fi)) &
            (df_altas["fecha_alta"] <= pd.Timestamp(ff))
        ].copy()
        # Use the month range of this year's dates
        m_ini = fi.month
        m_fin = ff.month
        meses = list(range(m_ini, m_fin + 1))
        valores = (
            df_f.groupby(df_f["fecha_alta"].dt.month)["contratados_alta"]
            .sum()
            .reindex(meses_rango, fill_value=0)
            .tolist()
        )
        color = colores[i % len(colores)]
        series.append({
            "name": str(año),
            "type": "bar",
            "data": [int(v) for v in valores],
            "itemStyle": {"color": color, "borderRadius": [4, 4, 0, 0]},
            "label": {
                "show": True,
                "position": "top",
                "color": _TEXT,
                "fontSize": 11,
                "formatter": "{c}",
            },
            "emphasis": {"focus": "series"},
        })

    options = {
        "color": colores,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "legend": {
            "data": [str(a) for a, _, _ in fechas_años],
            "textStyle": {"color": _TEXT},
            "top": "4%",
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": [meses_corto[m] for m in meses_rango],
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": series,
    }

    st_echarts(options, height="420px", width="100%", key=key)


def grafica_ejecutivos_periodo_comparado(df_altas: pd.DataFrame, fechas_años: list, key: str = None):
    """fechas_años: [(año, fecha_ini, fecha_fin), ...]"""
    colores = [_TEAL, _INDIGO, _AMBER, "#2dd4bf", "#818cf8"]

    def _match(nombre: str) -> str:
        for palabra in str(nombre).upper().split():
            if palabra in _EJECUTIVOS:
                return palabra
        return ""

    series = []
    for i, (año, fi, ff) in enumerate(fechas_años):
        df_f = df_altas[
            (df_altas["fecha_alta"] >= pd.Timestamp(fi)) &
            (df_altas["fecha_alta"] <= pd.Timestamp(ff))
        ].copy()
        df_f["ejecutivo"] = df_f["responsable_alta"].fillna("").apply(_match)
        valores = [
            int(df_f[df_f["ejecutivo"] == e]["contratados_alta"].sum())
            for e in _EJECUTIVOS
        ]
        color = colores[i % len(colores)]
        series.append({
            "name": str(año),
            "type": "bar",
            "data": valores,
            "itemStyle": {"color": color, "borderRadius": [4, 4, 0, 0]},
            "label": {
                "show": True,
                "position": "top",
                "color": _TEXT,
                "fontSize": 11,
                "formatter": "{c}",
            },
            "emphasis": {"focus": "series"},
        })

    options = {
        "color": colores,
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(20,20,20,0.92)",
            "borderColor": "rgba(255,255,255,0.08)",
            "textStyle": {"color": "#ffffff"},
        },
        "legend": {
            "data": [str(a) for a, _, _ in fechas_años],
            "textStyle": {"color": _TEXT},
            "top": "4%",
        },
        "toolbox": {
            "feature": {
                "magicType": {"type": ["bar", "line"]},
                "dataView": {"readOnly": True},
                "saveAsImage": {},
                "restore": {},
            }
        },
        "xAxis": {
            "type": "category",
            "data": _EJECUTIVOS,
            "axisLabel": {"color": _TEXT},
            "axisTick": {"alignWithLabel": True},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": _TEXT},
            "splitLine": {"lineStyle": {"color": _GRID}},
        },
        "series": series,
    }

    st_echarts(options, height="420px", width="100%", key=key)
