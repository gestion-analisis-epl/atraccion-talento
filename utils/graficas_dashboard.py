import streamlit as st
import pandas as pd
import plotly.express as px
from utils.funciones_dashboard import calcular_dias_cobertura
from utils.tabla_interactiva import render_interactive_table
from config.opciones import EMPRESAS_NOMBRE_CORTO, MESES_ES
from streamlit_echarts import st_echarts, JsCode
from streamlit_pivot import st_pivot_table
from utils.logger import get_logger
logger = get_logger(__name__)

# Paleta corporativa
_TEAL    = "#14b8a6"
_INDIGO  = "#6366f1"
_AMBER   = "#f59e0b"
_PALETTE = [_TEAL, _INDIGO, _AMBER, "#2dd4bf", "#818cf8", "#fcd34d"]
_TEXT    = "rgba(255,255,255,0.65)"
_GRID    = "rgba(255,255,255,0.06)"

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.75)", family="Inter, sans-serif"),
    xaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID),
    yaxis=dict(gridcolor=_GRID, zerolinecolor=_GRID),
)

_TOOLTIP = {
    "trigger": "axis",
    "axisPointer": {"type": "shadow"},
    "backgroundColor": "rgba(20,20,20,0.92)",
    "borderColor": "rgba(255,255,255,0.08)",
    "textStyle": {"color": "#ffffff"},
}

_TOOLTIP_ITEM = {
    "trigger": "item",
    "backgroundColor": "rgba(20,20,20,0.92)",
    "borderColor": "rgba(255,255,255,0.08)",
    "textStyle": {"color": "#ffffff"},
}

_TOOLBOX = {
    "feature": {
        "magicType": {"type": ["line", "bar"]},
        "dataView": {"readOnly": True},
        "saveAsImage": {},
        "restore": {},
    }
}

_TOOLBOX_SIMPLE = {
    "feature": {
        "dataView": {"readOnly": True},
        "saveAsImage": {},
    }
}

_YAXIS = {
    "type": "value",
    "axisLabel": {"color": _TEXT},
    "splitLine": {"lineStyle": {"color": _GRID}},
}


def tabla_dinamica_contrataciones(df_altas_filtrado):
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                tabla_dinamica = df.drop(columns=['id_registro', 'confidencial'])
                tabla_dinamica = tabla_dinamica.rename(
                    columns={
                        'id': 'ID',
                        'fecha_alta': 'Fecha de alta',
                        'empresa_alta': 'Empresa',
                        'puesto_alta': 'Puesto',
                        'plaza_alta': 'Plaza',
                        'area_alta': 'Área',
                        'contratados_alta': 'Contrataciones',
                        'medio_reclutamiento_alta': 'Medio de reclutamiento',
                        'responsable_alta': 'Ejecutivo de reclutamiento',
                    },
                )
                st_pivot_table(
                    tabla_dinamica,
                    key='pivot_table_ejecutivos',
                    rows=['Fecha de alta'],
                    columns=['Ejecutivo de reclutamiento', 'Área'],
                    values=['Contrataciones'],
                    aggregation={'Contrataciones': 'sum', 'ID': 'count'},
                    show_totals=True,
                    interactive=True,
                    conditional_formatting=[{
                        'type': 'data_bars',
                        'apply_to': ['Contrataciones'],
                        'color': _TEAL,
                        'fill': 'gradient'
                    }],
                    export_filename="contrataciones"
                )
            else:
                st.info('No se encontraron contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontraron registros de contrataciones.')
    except Exception as e:
        logger.error("Error en tabla_dinamica_contrataciones: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_contrataciones_por_ejecutivo(df_altas_filtrado):
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df['primer_nombre'] = df['responsable_alta'].str.split().str[0]
                df['primer_nombre'] = df['primer_nombre'].replace({
                    'MARTA': 'HELEN',
                    'LETICIA': 'LETY',
                    'YULIANA': 'YULI',
                })
                resumen = (
                    df.groupby(['primer_nombre', 'area_alta'])['contratados_alta']
                    .sum()
                    .reset_index()
                )
                pivot = (
                    resumen.pivot_table(
                        index='primer_nombre',
                        columns='area_alta',
                        values='contratados_alta',
                        aggfunc='sum',
                        fill_value=0
                    )
                )
                pivot['_total'] = pivot.sum(axis=1)
                pivot = pivot.sort_values('_total', ascending=True).drop(columns='_total')

                nombres = pivot.index.tolist()
                op_vals  = [int(v) for v in pivot.get('OPERATIVA',      [0] * len(nombres))]
                adm_vals = [int(v) for v in pivot.get('ADMINISTRATIVA', [0] * len(nombres))]

                options = {
                    "color": [_TEAL, _INDIGO],
                    "tooltip": _TOOLTIP,
                    "legend": {
                        "data": ["Operativa", "Administrativa"],
                        "top": "5%",
                        "left": "center",
                        "textStyle": {"color": _TEXT},
                    },
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "toolbox": _TOOLBOX_SIMPLE,
                    "xAxis": {
                        "type": "value",
                        "axisLabel": {"color": _TEXT},
                        "splitLine": {"lineStyle": {"color": _GRID}},
                    },
                    "yAxis": {
                        "type": "category",
                        "data": nombres,
                        "axisLabel": {"overflow": "truncate", "color": _TEXT},
                    },
                    "series": [
                        {
                            "name": "Operativa",
                            "type": "bar",
                            "stack": "total",
                            "label": {"show": True, "position": "inside", "fontWeight": "bold", "formatter": "{c}"},
                            "emphasis": {"focus": "series"},
                            "data": op_vals,
                        },
                        {
                            "name": "Administrativa",
                            "type": "bar",
                            "stack": "total",
                            "label": {"show": True, "position": "inside", "fontWeight": "bold", "formatter": "{c}"},
                            "emphasis": {"focus": "series"},
                            "data": adm_vals,
                        },
                    ],
                }
                st_echarts(options, height="400px", width="100%")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        logger.error("Error en grafica_contrataciones_por_ejecutivo: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_contrataciones_por_empresa(df_altas_filtrado):
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df.replace(EMPRESAS_NOMBRE_CORTO, inplace=True)
                resumen = (
                    df.groupby('empresa_alta')['contratados_alta']
                    .sum()
                    .reset_index()
                    .sort_values('contratados_alta', ascending=False)
                )

                todas = resumen['empresa_alta'].tolist()

                with st.popover(":material/filter_list: Empresas"):
                    seleccionadas = st.multiselect(
                        "Mostrar empresas",
                        options=todas,
                        default=todas,
                        key="sel_empresas_contrataciones",
                    )

                if not seleccionadas:
                    st.info('Selecciona al menos una empresa para ver la gráfica.')
                    return

                df_sel = resumen[resumen['empresa_alta'].isin(seleccionadas)].sort_values('contratados_alta', ascending=True)
                empresas_sel = df_sel['empresa_alta'].tolist()
                valores_sel  = [int(v) for v in df_sel['contratados_alta'].tolist()]
                total_sel    = sum(valores_sel)

                data_items = []
                for empresa, valor in zip(empresas_sel, valores_sel):
                    pct = valor / total_sel * 100 if total_sel > 0 else 0
                    data_items.append({
                        "value": valor,
                        "itemStyle": {"color": _PALETTE[todas.index(empresa) % len(_PALETTE)], "borderRadius": [0, 4, 4, 0]},
                        "label": {
                            "show": True,
                            "position": "right",
                            "color": _TEXT,
                            "fontSize": 11,
                            "formatter": f"{valor} ({pct:.1f}%)",
                        },
                    })

                options = {
                    "tooltip": _TOOLTIP,
                    "grid": {"left": "2%", "right": "18%", "top": "4%", "bottom": "4%", "containLabel": True},
                    "xAxis": {
                        "type": "value",
                        "axisLabel": {"color": _TEXT},
                        "splitLine": {"lineStyle": {"color": _GRID}},
                    },
                    "yAxis": {
                        "type": "category",
                        "data": empresas_sel,
                        "axisLabel": {"color": _TEXT},
                    },
                    "series": [{
                        "type": "bar",
                        "data": data_items,
                        "barMaxWidth": 36,
                        "emphasis": {"focus": "series"},
                    }],
                }

                altura = max(360, len(empresas_sel) * 52)
                st_echarts(options, height=f"{altura}px", width="100%", key="chart_contrataciones_empresa")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        logger.error("Error en grafica_contrataciones_por_empresa: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_contrataciones_por_medio_reclutamiento(df_altas_filtrado):
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                resumen = (
                    df.groupby('medio_reclutamiento_alta')['contratados_alta']
                    .sum()
                    .reset_index()
                    .sort_values('contratados_alta', ascending=True)
                )

                total  = int(resumen['contratados_alta'].sum())
                valores = [int(v) for v in resumen['contratados_alta']]

                options = {
                    "color": [_TEAL],
                    "tooltip": {
                        **_TOOLTIP,
                        "formatter": JsCode(
                            f"function(p){{ return p[0].name + ': ' + p[0].value + ' (' + (p[0].value / {total} * 100).toFixed(2) + '%)'; }}"
                        ),
                    },
                    "toolbox": _TOOLBOX_SIMPLE,
                    "xAxis": {
                        "type": "value",
                        "axisLabel": {"color": _TEXT},
                        "splitLine": {"lineStyle": {"color": _GRID}},
                    },
                    "yAxis": {
                        "type": "category",
                        "data": [str(n) for n in resumen['medio_reclutamiento_alta']],
                        "axisLabel": {"overflow": "truncate", "color": _TEXT},
                    },
                    "series": [{
                        "name": "Contrataciones",
                        "type": "bar",
                        "label": {"show": True, "position": "inside", "fontWeight": "bold"},
                        "itemStyle": {"color": _TEAL},
                        "data": valores,
                    }],
                }
                st_echarts(options, height="400px", width="100%")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        logger.error("Error en grafica_contrataciones_por_medio_reclutamiento: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_vacantes_por_empresa(df_vacantes):
    try:
        if not df_vacantes.empty:
            df = df_vacantes.copy()
            df['vacantes_solicitadas'] = df['vacantes_solicitadas'].astype(int)
            df = df[(df['vacantes_solicitadas'] > 0) & (df['fecha_autorizacion'].notna())]

            if not df.empty:
                df['dias_cobertura_calculados'] = df.apply(calcular_dias_cobertura, axis=1)
                df_detalle = df[[
                    'id_sistema', 'fecha_autorizacion', 'empresa_vacante', 'puesto_vacante',
                    'plaza_vacante', 'vacantes_solicitadas', 'dias_cobertura_calculados',
                    'confidencial', 'fase_proceso',
                ]].copy()
                df_detalle['fecha_autorizacion'] = df_detalle['fecha_autorizacion'].dt.date
                df_detalle = df_detalle.rename(columns={
                    "id_sistema": "ID",
                    "fecha_autorizacion": "Fecha de autorización",
                    "empresa_vacante": "Empresa",
                    "puesto_vacante": "Puesto",
                    "plaza_vacante": "Plaza",
                    "vacantes_solicitadas": "Vacantes",
                    "dias_cobertura_calculados": "Días de cobertura",
                    "fase_proceso": "Fase de proceso",
                })
                df_grafico = df_detalle.copy()
                df_grafico['Empresa'] = df_grafico['Empresa'].replace(EMPRESAS_NOMBRE_CORTO)
                df_detalle['Días de cobertura'] = df_detalle['Días de cobertura'].round(0).astype(int)
                df_detalle = df_detalle.sort_values(by='Días de cobertura', ascending=False)
                df_detalle.loc[df_detalle['confidencial'] == 'SI', 'Puesto'] = 'VACANTE'
                df_detalle = df_detalle.drop(columns=['confidencial']).reset_index(drop=True)

                st_pivot_table(
                    df_detalle,
                    key='pivot_table_vacantes',
                    rows=['ID', 'Empresa', 'Puesto'],
                    values=['Vacantes', 'Días de cobertura'],
                    aggregation={'Vacantes': 'sum', 'Días de cobertura': 'avg'},
                    conditional_formatting=[{
                        "type": "threshold",
                        "apply_to": ['Días de cobertura'],
                        "conditions": [
                            {"operator": "gt", "value": 15, "background": _INDIGO, "bold": True},
                        ],
                    }],
                    export_filename="vacantes_actuales"
                )

                resumen = df_grafico.groupby('Empresa')['Vacantes'].sum().reset_index()
                resumen = resumen.sort_values('Vacantes', ascending=False)

                st.write('### Resumen de Vacantes por Empresa')
                col1, col2 = st.columns([2, 2])
                with col1:
                    render_interactive_table(resumen, height=360)

                options = {
                    "color": [_TEAL],
                    "tooltip": _TOOLTIP_ITEM,
                    "toolbox": _TOOLBOX_SIMPLE,
                    "xAxis": {
                        "type": "category",
                        "data": [str(n) for n in resumen['Empresa']],
                        "axisLabel": {"rotate": 45, "overflow": "truncate", "color": _TEXT},
                    },
                    "yAxis": _YAXIS,
                    "series": [{
                        "name": "Vacantes",
                        "type": "bar",
                        "label": {"show": True, "position": "inside", "fontWeight": "bold"},
                        "itemStyle": {"color": _TEAL},
                        "data": [int(v) for v in resumen['Vacantes']],
                    }],
                }
                with col2:
                    st_echarts(options)
            else:
                st.info('No se encontraron vacantes.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        logger.error("Error en grafica_vacantes_por_empresa: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_vacantes_por_area(df_vacantes):
    try:
        if not df_vacantes.empty:
            df = df_vacantes.copy()
            df = df[(df['vacantes_solicitadas'].astype(int) > 0) & (df['fecha_autorizacion'].notna())]
            if not df.empty:
                resumen = (
                    df.groupby('funcion_area_vacante')['vacantes_solicitadas']
                    .sum()
                    .reset_index()
                    .rename(columns={"funcion_area_vacante": "Función de área", "vacantes_solicitadas": "Vacantes"})
                    .sort_values(by='Vacantes', ascending=False)
                )

                col1, col2 = st.columns([2, 2])
                with col1:
                    render_interactive_table(resumen, height=360)

                options = {
                    "color": [_TEAL, _INDIGO],
                    "tooltip": _TOOLTIP_ITEM,
                    "legend": {"top": "1%", "left": "center", "textStyle": {"color": _TEXT}},
                    "toolbox": _TOOLBOX_SIMPLE,
                    "series": [{
                        "name": "Función de área",
                        "type": "pie",
                        "radius": ["40%", "80%"],
                        "avoidLabelOverlap": True,
                        "itemStyle": {"borderRadius": 5, "borderColor": "#2a2a2a", "borderWidth": 2},
                        "label": {"show": False, "fontWeight": "bold", "position": "center", "color": _TEXT},
                        "emphasis": {"label": {"show": True, "fontWeight": "bold", "fontSize": 20}},
                        "data": [
                            {"value": int(v), "name": str(n)}
                            for v, n in zip(resumen['Vacantes'], resumen['Función de área'])
                        ],
                    }],
                }
                with col2:
                    st_echarts(options, width="500px")
            else:
                st.info('No se encontraron vacantes.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        logger.error("Error en grafica_vacantes_por_area: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_contrataciones_mes(df_altas_filtrado):
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df['mes_alta'] = df['fecha_alta'].dt.month.map(MESES_ES)
                meses_ordenados = list(MESES_ES.values())
                df['mes_alta'] = pd.Categorical(df['mes_alta'], categories=meses_ordenados, ordered=True)
                resumen = df.groupby('mes_alta', as_index=False, observed=True)['contratados_alta'].sum()

                options = {
                    "color": [_TEAL],
                    "tooltip": {**_TOOLTIP, "axisPointer": {"type": "line"}},
                    "toolbox": _TOOLBOX,
                    "xAxis": {
                        "type": "category",
                        "data": [str(n) for n in resumen['mes_alta']],
                        "axisLabel": {"rotate": 45, "overflow": "truncate", "color": _TEXT},
                    },
                    "yAxis": _YAXIS,
                    "series": {
                        "name": "Contrataciones por Mes",
                        "type": "line",
                        "areaStyle": {"color": "rgba(20,184,166,0.15)"},
                        "lineStyle": {"color": _TEAL},
                        "itemStyle": {"color": _TEAL},
                        "smooth": True,
                        "data": [int(v) for v in resumen['contratados_alta']],
                    },
                }
                st_echarts(options, height="350px", width="100%")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        logger.error("Error en grafica_contrataciones_mes: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def grafica_embudo_fase_proceso(df_vacantes_filtrado):
    try:
        if not df_vacantes_filtrado.empty:
            df = df_vacantes_filtrado.copy()
            df = df[df['fase_proceso'].notna()]

            if not df.empty:
                df = df.loc[
                    (df["fase_proceso"] != "CONTRATADO") &
                    (df["estatus_solicitud"] != "PENDIENTE") &
                    df['fecha_autorizacion'].notna() &
                    (df["estatus_solicitud"] != "CANCELADO") &
                    (df["estatus_solicitud"] != "PAUSADO") &
                    (df['vacantes_solicitadas'] > 0)
                ]
                conteo = df['fase_proceso'].value_counts().reset_index()
                conteo.columns = ['fase_proceso', 'cantidad']
                conteo = conteo.sort_values('cantidad', ascending=True)

                fig = px.funnel(
                    conteo,
                    x='cantidad',
                    y='fase_proceso',
                    title='Embudo por Fase de Proceso',
                    labels={'cantidad': 'Total', 'fase_proceso': 'Fase del Proceso'},
                    color='fase_proceso',
                    color_discrete_sequence=_PALETTE,
                )
                fig.update_layout(**_PLOTLY_LAYOUT, showlegend=False)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info('No se encontraron fases de proceso registradas.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        logger.error("Error en grafica_embudo_fase_proceso: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def contrataciones_area_redes_pagadas(df_altas_filtrado):
    col1, col2, col3, col4 = st.columns(4)
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df['mes_alta'] = df['fecha_alta'].dt.month.map(MESES_ES)
                df['mes_alta'] = pd.Categorical(df['mes_alta'], categories=MESES_ES.values(), ordered=True)

                total_contrataciones = df['contratados_alta'].sum()
                col1.metric('Contratados Totales', total_contrataciones)

                df_redes = df[df['medio_reclutamiento_alta'] == 'REDES PAGADAS']
                col2.metric('Contratados Redes Pagadas', df_redes['contratados_alta'].sum())

                df_op = df[df['area_alta'] == 'OPERATIVA']
                col3.metric('Contrataciones Operativas', df_op['contratados_alta'].sum())

                df_op_redes = df_op[df_op['medio_reclutamiento_alta'] == 'REDES PAGADAS']
                col4.metric('Contrataciones Operativas Redes Pagadas', df_op_redes['contratados_alta'].sum())

                df_area = df_op.groupby('mes_alta', observed=True)['contratados_alta'].sum().reset_index()
                df_bar  = df_redes.groupby('mes_alta', observed=True)['contratados_alta'].sum().reset_index()

                options = {
                    "color": [_TEAL, _INDIGO],
                    "tooltip": _TOOLTIP,
                    "legend": {
                        "data": ["Contrataciones Totales", "Contrataciones Redes Pagadas"],
                        "textStyle": {"color": _TEXT},
                    },
                    "toolbox": _TOOLBOX,
                    "xAxis": [{
                        "type": "category",
                        "data": [str(n) for n in df_bar['mes_alta']],
                        "axisPointer": {"type": "shadow"},
                        "axisLabel": {"rotate": 45, "overflow": "truncate", "color": _TEXT},
                    }],
                    "yAxis": [_YAXIS],
                    "series": [
                        {
                            "name": "Contrataciones Totales",
                            "type": "line",
                            "lineStyle": {"color": _TEAL},
                            "itemStyle": {"color": _TEAL},
                            "data": [int(v) for v in df_area['contratados_alta']],
                        },
                        {
                            "name": "Contrataciones Redes Pagadas",
                            "type": "bar",
                            "itemStyle": {"color": _INDIGO},
                            "data": [int(v) for v in df_bar['contratados_alta']],
                        },
                    ],
                }
                st_echarts(options, height="500px")
            else:
                st.info('No se encontraron contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontraron registros de contrataciones.')
    except Exception as e:
        logger.error("Error en contrataciones_area_redes_pagadas: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")


def promedio_plaza_puesto(df_vacantes_cerradas_filtrado):
    try:
        if not df_vacantes_cerradas_filtrado.empty:
            df = df_vacantes_cerradas_filtrado.copy()
            df['dias_cobertura_calculados'] = df.apply(calcular_dias_cobertura, axis=1)
            df = df[df['vacantes_contratados'] > 0]

            col1, col2, col3 = st.columns([2, 2, 2])
            st.write('### Tablas Detalle')
            row_container = st.container(horizontal=True, horizontal_alignment='center')

            valor_promedio_general = df['dias_cobertura_calculados'].mean().round(0)
            valor_actual = 15 + 30 / 2
            with col1:
                promedio_general = st.metric(label='Promedio Global', value=valor_promedio_general, delta=f"Meta actual: {valor_actual:.0f} días")

            df_plaza = (
                df.groupby('plaza_vacante')['dias_cobertura_calculados']
                .mean()
                .reset_index()
                .sort_values(by='dias_cobertura_calculados', ascending=False)
                .round(0)
                .rename(columns={'plaza_vacante': 'Plaza', 'dias_cobertura_calculados': 'Días de cobertura'})
            )
            df_puesto = (
                df.groupby('puesto_vacante')['dias_cobertura_calculados']
                .mean()
                .reset_index()
                .sort_values(by='dias_cobertura_calculados', ascending=False)
                .round(0)
                .rename(columns={'puesto_vacante': 'Puesto', 'dias_cobertura_calculados': 'Días de cobertura'})
            )

            with col2:
                plaza_mas_alta = st.metric(label=df_plaza.iloc[0]['Plaza'], value=f"{df_plaza.iloc[0]['Días de cobertura']:.0f} días")
            with col3:
                puesto_mas_alto = st.metric(label=df_puesto.iloc[0]['Puesto'], value=f"{df_puesto.iloc[0]['Días de cobertura']:.0f} días")

            with row_container:
                render_interactive_table(df_plaza, height=460)
                render_interactive_table(df_puesto, height=460)

            return plaza_mas_alta, promedio_general, None, None

    except Exception as e:
        logger.error("Error en promedio_plaza_puesto: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")
