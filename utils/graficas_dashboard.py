"""
Módulo de gráficas para el dashboard de reclutamiento.
Contiene funciones reutilizables para generar visualizaciones de datos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.funciones_dashboard import empresas_map, calcular_dias_cobertura
from config.opciones import EMPRESAS_NOMBRE_CORTO
from streamlit_echarts import st_echarts, JsCode
from streamlit_pivot import st_pivot_table


def tabla_dinamica_contrataciones(df_altas_filtrado):
    """
    Genera tabla dinámica de contrataciones con la información de altas.
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                tabla_dinamica = df.drop(columns=['id', 'id_registro', 'confidencial'])
                tabla_dinamica = tabla_dinamica.rename(
                    columns={
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
                    conditional_formatting=[{
                        'type': 'data_bars',
                        'apply_to': ['Contrataciones'],
                        'color': '#1976d2',
                        'fill': 'gradient'
                    }]
                )
            else:
                st.info('No se encontraron contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontraron registros de contrataciones.')
    except Exception as e:
        st.error(f'Error al mostrar tabla dinámica: {e}')

def grafica_contrataciones_por_ejecutivo(df_altas_filtrado):
    """
    Genera gráfica de barras horizontales con contrataciones por ejecutivo.
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df['primer_nombre'] = df['responsable_alta'].str.split().str[0]
                df['primer_nombre'] = df['primer_nombre'].replace({
                    'MARTA': 'HELEN',
                    "LETICIA": "LETY",
                    "YULIANA": "YULI"
                })

                resumen = (
                    df.groupby(['primer_nombre', 'area_alta'])['contratados_alta']
                    .sum()
                    .reset_index()
                )

                # Tabla pivote para alinear ambas áreas por reclutador
                pivot = (
                    resumen.pivot_table(
                        index='primer_nombre',
                        columns='area_alta',
                        values='contratados_alta',
                        aggfunc='sum',
                        fill_value=0
                    )
                )
                
                # Ordenar por total ascendente (para barras horizontales)
                pivot['_total'] = pivot.sum(axis=1)
                pivot = pivot.sort_values('_total', ascending=True).drop(columns='_total')

                nombres = pivot.index.tolist()
                op_vals  = [int(v) for v in pivot.get('OPERATIVA',   [0]*len(nombres))]
                adm_vals = [int(v) for v in pivot.get('ADMINISTRATIVA', [0]*len(nombres))]

                options = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {
                        "data": ["Operativa", "Administrativa"],
                        "top": "5%",
                        "left": "center"
                    },
                    "grid": {
                        "left": "3%", "right": "4%",
                        "bottom": "3%", "containLabel": True
                    },
                    "toolbox": {
                        "feature": {
                            "dataView": {"readOnly": True},
                            "saveAsImage": {}
                        }
                    },
                    "xAxis": {"type": "value"},
                    "yAxis": {
                        "type": "category",
                        "data": nombres,
                        "axisLabel": {"overflow": "truncate"}
                    },
                    "series": [
                        {
                            "name": "Operativa",
                            "type": "bar",
                            "stack": "total",
                            "label": {
                                "show": True,
                                "position": "inside",
                                "fontWeight": "bold",
                                "formatter": "{c}"   # oculta el 0 opcionalmente
                            },
                            "emphasis": {"focus": "series"},
                            "data": op_vals
                        },
                        {
                            "name": "Administrativa",
                            "type": "bar",
                            "stack": "total",
                            "label": {
                                "show": True,
                                "position": "inside",
                                "fontWeight": "bold",
                                "formatter": "{c}"
                            },
                            "emphasis": {"focus": "series"},
                            "data": adm_vals
                        }
                    ]
                }
                
                st_echarts(options, height="400px", width="100%")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por ejecutivo: {e}')
        
def grafica_contrataciones_por_empresa(df_altas_filtrado):
    """
    Genera gráfica de pie con contrataciones por empresa.
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                df.replace(EMPRESAS_NOMBRE_CORTO, inplace=True)
                resumen = df.groupby('empresa_alta')['contratados_alta'].sum().reset_index()
                resumen = resumen.sort_values('contratados_alta', ascending=False)
                resumen['total_contratados'] = resumen['contratados_alta'].sum()
                resumen['porcentaje'] = (resumen['contratados_alta'] / resumen['total_contratados'] * 100).round(1)
                # Etiqueta combinada
                resumen['etiqueta'] = resumen.apply(lambda row: f"{row['contratados_alta']} ({row['porcentaje']}%)", axis=1)
                resumen.rename(columns={'empresa_alta': 'Empresa', 'etiqueta': 'Contratados', 'contratados_alta': 'Total'}, inplace=True)
                fig = px.bar(
                    resumen,
                    x='Total',
                    y='Empresa',
                    orientation='h',
                    text='Contratados',
                    color='Empresa',
                    color_discrete_sequence=px.colors.sequential.Mint,
                    title='Contrataciones realizadas por Empresa',
                )
                
                fig.update_layout()
                st.plotly_chart(fig)
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por ejecutivo: {e}')

def grafica_contrataciones_por_medio_reclutamiento_1(df_altas_filtrado):
    """
    Genera gráfica de barras horizontales con contrataciones por medio de reclutamiento.
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                resumen = df.groupby('medio_reclutamiento_alta')['contratados_alta'].sum().reset_index()
                datos_a_mostrar = st.number_input('¿Cuántos medios desea observar?', min_value=1, max_value=resumen.shape[0], value=resumen.shape[0])
                resumen = resumen.sort_values('contratados_alta', ascending=False).head(datos_a_mostrar)
                # Calcular total y porcentajes
                total_contrataciones = resumen['contratados_alta'].sum()
                resumen['porcentaje'] = (resumen['contratados_alta'] / total_contrataciones * 100).round(1)
                # Etiqueta combinada
                resumen['etiqueta'] = resumen.apply(lambda row: f"{row['contratados_alta']} ({row['porcentaje']}%)", axis=1)
                fig = px.bar(
                    resumen, 
                    x='contratados_alta', 
                    y='medio_reclutamiento_alta', 
                    orientation='h', 
                    text='etiqueta', 
                    color='medio_reclutamiento_alta',
                    color_discrete_sequence=px.colors.sequential.thermal_r,
                    title='Contrataciones por Medio de Reclutamiento',
                    labels={'contratados_alta': 'Contrataciones', 'medio_reclutamiento_alta': 'Medio de Reclutamiento'}
                )
                fig.update_layout(yaxis=dict(tickmode="linear"), showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por medio: {e}')
        
def grafica_contrataciones_por_medio_reclutamiento(df_altas_filtrado):
    """"
    Genera gráfica de barras horizontales con contrtaciones por medio de reclutamiento
    
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                resumen = df.groupby('medio_reclutamiento_alta')['contratados_alta'].sum().reset_index()
                resumen = resumen.sort_values('contratados_alta', ascending=True)
                
                total = int(resumen['contratados_alta'].sum())
                valores = [int(v) for v in resumen['contratados_alta']]
                
                options = {
                    "tooltip": {
                        "trigger": "axis",
                        "axisPointer": {
                            "type": "shadow"
                        },
                        "formatter": JsCode(
                            f"function(p){{ return p[0].name + ': ' + p[0].value + ' (' + (p[0].value / {total} * 100).toFixed(2) + '%)'; }}"
                        )
                    },
                    "legend": {"top": "5%", "left": "center", "show": False},
                    "toolbox": {
                        "feature": {
                            "dataView": {"readOnly": True},
                            "saveAsImage": {},
                        }
                    },
                    "xAxis": {
                        "type": "value"
                    },
                    "yAxis": {
                        "type": "category",
                        "data": [str(n) for n in resumen['medio_reclutamiento_alta']],
                        "axisLabel": {"overflow": "truncate"}
                    },
                    "series": [
                        {
                            "name": "Contrataciones",
                            "type": "bar",
                            "label": {
                                "show": True,
                                "position": "inside",
                                "fontWeight": "bold",
                            },
                            "data": valores
                        }
                    ]
                }
                st_echarts(options, height="400px", width="100%")
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por medio: {e}')

def grafica_vacantes_por_empresa(df_vacantes):
    """
    Genera tabla de detalle, resumen y gráfica de pie con vacantes por empresa.
    
    Args:
        df_vacantes: DataFrame de vacantes (sin filtrar por tiempo)
    """
    try:
        if not df_vacantes.empty:
            df = df_vacantes.copy()
            df['vacantes_solicitadas'] = df['vacantes_solicitadas'].astype(int)
            
            df = df[(df['vacantes_solicitadas'] > 0) & (df['fecha_autorizacion'].notna())]

            if not df.empty:
                # Calcular días de cobertura actualizados para cada vacante
                df['dias_cobertura_calculados'] = df.apply(calcular_dias_cobertura, axis=1)
                # Mostrar detalle de vacantes con nombre de la vacante y empresa
                df_detalle = df[['id_sistema', 'fecha_autorizacion', 'empresa_vacante', 'puesto_vacante', 'plaza_vacante', 'vacantes_solicitadas', 'dias_cobertura_calculados', 'confidencial', 'fase_proceso']].copy()
                df_detalle['fecha_autorizacion'] = df_detalle['fecha_autorizacion'].dt.date
                df_detalle = df_detalle.rename(columns={
                    "id_sistema": "ID",
                    "fecha_autorizacion": "Fecha de autorización",
                    "empresa_vacante": "Empresa", 
                    "puesto_vacante": "Puesto", 
                    "plaza_vacante": "Plaza",
                    "vacantes_solicitadas": "Vacantes",
                    "dias_cobertura_calculados": "Días de cobertura",
                    "fase_proceso": "Fase de proceso"
                })
                # df_detalle['Empresa'] = df_detalle['Empresa'].replace(empresas_map)
                df_grafico = df_detalle.copy()
                df_grafico['Empresa'] = df_grafico['Empresa'].replace(empresas_map)
                #df_detalle = df_detalle.groupby(['Empresa', 'Puesto', 'Plaza'], as_index=False).agg({
                #    'Vacantes': 'sum',
                #    'Días de cobertura': 'mean'  # Promedio de días de cobertura por agrupación
                #})
                df_detalle['Días de cobertura'] = df_detalle['Días de cobertura'].round(0).astype(int)

                #st.write('### Detalle de Vacantes')
                df_detalle = df_detalle.sort_values(by='Días de cobertura', ascending=False)
                df_detalle.loc[df_detalle['confidencial'] == 'SI', 'Puesto'] = 'VACANTE'
                st.dataframe(df_detalle, hide_index=True, column_config={
                    'confidencial': None
                })

                # Resumen por empresa
                resumen = df_grafico.groupby('Empresa')['Vacantes'].sum().reset_index()
                resumen = resumen.sort_values('Vacantes', ascending=False)
                with st.container():
                    st.write('### Resumen de Vacantes por Empresa')
                    
                    col1, col2 = st.columns([2, 2])
                    with col1:
                        st.dataframe(resumen, hide_index=True)

                    # Gráfico de barras
                    options = {
                        "tooltip": {"trigger": "item"},
                        "legend": {"top": "5%", "left": "center", "show": False},
                        "toolbox": {
                            "feature": {
                                "dataView": {"readOnly": True},
                                "saveAsImage": {},
                            }
                        },
                        "xAxis": {
                            "type": "category",
                            "data": [str(n) for n in resumen['Empresa']],
                            "axisLabel": {"rotate": 45, "overflow": "truncate"}
                        },
                        "yAxis": {
                            "type": "value",
                        },
                        "series": [
                            {
                                "name": "Vacantes",
                                "type": "bar",
                                "label": {"show": True, "position": "inside", "fontWeight": "bold"},
                                "data": [int(v) for v in resumen['Vacantes']]
                            }
                        ]
                    }
                    with col2:
                        st_echarts(options)
            else:
                st.info('No se encontraron vacantes.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de vacantes por empresa: {e}')


def grafica_vacantes_por_area(df_vacantes):
    """
    Genera tabla y gráfica de barras con vacantes por función de área.
    
    Args:
        df_vacantes: DataFrame de vacantes (sin filtrar por tiempo)
    """
    try:
        if not df_vacantes.empty:
            df = df_vacantes.copy()
            df = df[(df['vacantes_solicitadas'].astype(int) > 0) & (df['fecha_autorizacion'].notna())]
            if not df.empty:
                resumen = df.groupby('funcion_area_vacante')['vacantes_solicitadas'].sum().reset_index()
                columns_name = {
                    "funcion_area_vacante": "Función de área", 
                    "vacantes_solicitadas": "Vacantes"
                }
                resumen = resumen.rename(columns=columns_name) 
                resumen = resumen.sort_values(by='Vacantes', ascending=False)
                col1, col2 = st.columns([2, 2])
                with col1:
                    st.dataframe(resumen, hide_index=True)
                options = {
                    "tooltip": {"trigger": "item"},
                    "legend": {"top": "1%", "left": "center"},
                    "toolbox": {
                        "feature": {
                            "dataView": {"readOnly": True},
                            "saveAsImage": {},
                        }
                    },
                    "series": [
                        {
                            "name": "Función de área",
                            "type": "pie",
                            "radius": ["40%", "80%"],
                            "avoidLabelOverlap": True,
                            "itemStyle": {"borderRadius": 5, "borderColor": "#2a2a2a", "borderWidth": 2},
                            "label": {"show": False, "fontWeight": "bold", "position": "center"},
                            "emphasis": {"label": {"show": True, "fontWeight": "bold", "fontSize": 20}},
                            "data": [
                                {"value": int(v), "name": str(n)}
                                for v, n in zip(resumen['Vacantes'], resumen['Función de área'])
                            ]
                        }
                    ]
                }
                with col2:
                    st_echarts(options, width="500px")
            else:
                st.info('No se encontraron vacantes.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        st.error(f'Error al generar la información de vacantes por área: {e}')
        
def grafica_contrataciones_mes(df_altas_filtrado):
    """
    Genera gráfica de barras con contrataciones por mes.
    
    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                # Mapeo manual de meses
                meses = {
                    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
                }
                df['mes_alta'] = df['fecha_alta'].dt.month.map(meses)

                meses_ordenados = list(meses.values())
                df['mes_alta'] = pd.Categorical(df['mes_alta'], categories=meses_ordenados, ordered=True)

                resumen = df.groupby('mes_alta', as_index=False)['contratados_alta'].sum()
                
                options = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "line"}},
                    "toolbox": {
                        "feature": {
                            "dataView": {"readOnly": True},
                            "magicType": {"type": ["line", "bar"]},
                            "restore": {},
                            "saveAsImage": {}
                        }
                    },
                    "xAxis": {
                        "type": "category",
                        "data": [str(n) for n in resumen['mes_alta']],
                        "axisLabel": {"rotate": 45, "overflow": "truncate"}
                    },
                    "yAxis": {
                        "type": "value"
                    },
                    "series": {
                        "name": "Contrataciones por Mes",
                        "type": "line",
                        "areaStyle": {},
                        "smooth": True,
                        "data": [int(v) for v in resumen['contratados_alta']],
                    }
                }
                st_echarts(options, height="350px", width="100%")
               
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por mes: {e}')

def grafica_embudo_fase_proceso(df_vacantes_filtrado):
    """
    Genera gráfica de embudo con vacantes por fase de proceso.
    
    Args:
        df_vacantes_filtrado: DataFrame filtrado de vacantes
    """
    try:
        if not df_vacantes_filtrado.empty:
            df = df_vacantes_filtrado.copy()
            df = df[df['fase_proceso'].notna()]
            
            if not df.empty:
                # Filtrar registros que NO sean "CONTRATADO"
                df = df.loc[
                (df["fase_proceso"] != "CONTRATADO") & 
                (df["estatus_solicitud"] != "PENDIENTE") & 
                df['fecha_autorizacion'].notna() & 
                (df["estatus_solicitud"] != "CANCELADO") &
                (df["estatus_solicitud"] != "PAUSADO") &
                (df['vacantes_solicitadas'] > 0)
                ]
                
                # Contar por fase de proceso
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
                    color_discrete_sequence=px.colors.qualitative.Pastel2,
                )
                fig.update_layout(showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
            else:
                st.info('No se encontraron fases de proceso registradas.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de embudo por fase de proceso: {e}')

def contrataciones_area_redes_pagadas(df_altas_filtrado):
    """
    Genera información referente a contrataciones de redes pagadas,
    de acuerdo a la función de área.

    Args:
        df_altas_filtrado: DataFrame filtrado de altas
    """
    col1, col2, col3, col4 = st.columns(4)
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df = df[df['contratados_alta'].astype(int) > 0]
            if not df.empty:
                meses_es = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
                df['mes_alta'] = df['fecha_alta'].dt.month.map(meses_es)
                df['mes_alta'] = pd.Categorical(df['mes_alta'], categories=meses_es.values(), ordered=True)

                total_contrataciones = df['contratados_alta'].sum()
                col1.metric('Contratados Totales', total_contrataciones)
                total_redes_pagadas = df[df['medio_reclutamiento_alta'] == 'REDES PAGADAS']
                contrataciones_redes_pagadas = total_redes_pagadas['contratados_alta'].sum()
                col2.metric('Contratados Redes Pagadas', contrataciones_redes_pagadas)
                total_operativas = df[df['area_alta'] == 'OPERATIVA']
                contrataciones_operativas = total_operativas['contratados_alta'].sum()
                col3.metric('Contrataciones Operativas', contrataciones_operativas)
                total_operativas_redes_pagadas = total_operativas[total_operativas['medio_reclutamiento_alta'] == 'REDES PAGADAS']
                contrataciones_operativas_redes_pagadas = total_operativas_redes_pagadas['contratados_alta'].sum()
                col4.metric('Contrataciones Operativas Redes Pagadas', contrataciones_operativas_redes_pagadas)

                df_area = total_operativas.groupby('mes_alta')['contratados_alta'].sum().reset_index()
                df_bar = total_redes_pagadas.groupby('mes_alta')['contratados_alta'].sum().reset_index()
                
                options = {
                    "tooltip": {"trigger": "axis"},
                    "toolbox": {
                        "feature": {
                            "dataView": {"readOnly": True},
                            "magicType": {"type": ["line", "bar"]},
                            "restore": {},
                            "saveAsImage": {}
                        }
                    },
                    "xAxis": [
                        {
                            "type": "category",
                            "data": [str(n) for n in df_bar['mes_alta']],
                            "axisPointer": {"type": "shadow"},
                            "axisLabel": {"rotate": 45, "overflow": "truncate"}
                        }
                    ],
                    "yAxis": [
                        {
                            "type": "value",
                        }
                    ],
                    "series": [
                        {
                            "name": "Contrataciones Totales",
                            "type": "line",
                            "data": [int(v) for v in df_area['contratados_alta']],
                            
                        },
                        {
                            "name": "Contrataciones Redes Pagadas",
                            "type": "bar",
                            "data": [int(v) for v in df_bar['contratados_alta']],
                        }
                    ]
                }
                
                st_echarts(options, height="500px")
               
            else:
                st.info('No se encontraron contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontraron registros de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la información de contrataciones por área: {e}')
        
def promedio_plaza_puesto(df_vacantes_cerradas_filtrado):
    """
    Genera tabla de detalle y gráficas de promedio de días de cobertura por puesto y plaza.
    
    Args:
        df_vacantes_cerradas_filtrado: DataFrame de vacantes cerradas filtrado por tiempo
    """
    try:
        if not df_vacantes_cerradas_filtrado.empty:
            df = df_vacantes_cerradas_filtrado.copy()
            df['dias_cobertura_calculados'] = df.apply(calcular_dias_cobertura, axis=1)
            """vacantes_excluir = (
                (df['estatus_solicitud'] != "FINALIZADO") &
                (df['fase_proceso'] != "CONTRATADO")
            )
            df = df[~vacantes_excluir]"""
            df = df[df['vacantes_contratados'] > 0]
            
            col1, col2, col3 = st.columns([2, 2, 2])
            st.write('### Tablas Detalle')
            row_container = st.container(horizontal=True, horizontal_alignment='center')
            
            with col1:
                valor_promedio_general = df['dias_cobertura_calculados'].mean().round(0)
                valor_actual = 15 + 30 / 2
                promedio_general = st.metric(label='Promedio Global', value=valor_promedio_general, delta=f"Meta actual: {valor_actual:.0f} días")
                
            with row_container:
                df_plaza = df.groupby('plaza_vacante')['dias_cobertura_calculados'].mean().reset_index().sort_values(by='dias_cobertura_calculados', ascending=False).round(0)
                df_plaza = df_plaza.rename(columns={'plaza_vacante': 'Plaza', 'dias_cobertura_calculados': 'Días de cobertura'})
            
            with col2:
                plaza_mas_alta = st.metric(label=df_plaza.iloc[0]['Plaza'], value=f"{df_plaza.iloc[0]['Días de cobertura']:.0f} días")
                
            df_puesto = df.groupby('puesto_vacante')['dias_cobertura_calculados'].mean().reset_index().sort_values(by='dias_cobertura_calculados', ascending=False).round(0)
            df_puesto = df_puesto.rename(columns={'puesto_vacante': 'Puesto', 'dias_cobertura_calculados': 'Días de cobertura'})
            
            with col3:
                puesto_mas_alto = st.metric(label=df_puesto.iloc[0]['Puesto'], value=f"{df_puesto.iloc[0]['Días de cobertura']:.0f} días")
            
            with row_container:
                tabla_plaza = st.dataframe(df_plaza, hide_index=True)
                tabla_puesto = st.dataframe(df_puesto, hide_index=True)
            
            return plaza_mas_alta, promedio_general, tabla_plaza, tabla_puesto
            
    except Exception as e:
        st.error(f'Error al calcular promedio de plaza y puesto: {e}')