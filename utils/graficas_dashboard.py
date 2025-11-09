"""
Módulo de gráficas para el dashboard de reclutamiento.
Contiene funciones reutilizables para generar visualizaciones de datos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.funciones_dashboard import empresas_map
    
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
                resumen = df.groupby('primer_nombre')['contratados_alta'].sum().reset_index()
                resumen = resumen.sort_values('contratados_alta', ascending=False)
                fig = px.bar(
                    resumen, 
                    x='contratados_alta', 
                    y='primer_nombre', 
                    orientation='h', 
                    text='contratados_alta', 
                    color='primer_nombre',
                    color_discrete_sequence=px.colors.sequential.PuBu,
                    title='Contrataciones realizadas por Ejecutivo',
                    labels={'contratados_alta': 'Contrataciones', 'primer_nombre': 'Ejecutivo'}
                )
                fig.update_layout(showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por ejecutivo: {e}')


def grafica_contrataciones_por_medio_reclutamiento(df_altas_filtrado):
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
                datos_a_mostrar = st.number_input('¿Cuántos medios desea observar?', min_value=1, max_value=resumen.shape[0])
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
                    color_discrete_sequence=px.colors.sequential.Magenta,
                    title='Contrataciones por Medio de Reclutamiento',
                    labels={'contratados_alta': 'Contrataciones', 'medio_reclutamiento_alta': 'Medio de Reclutamiento'}
                )
                #fig.update_traces(textposition='outside')
                fig.update_layout(yaxis=dict(tickmode="linear"), showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
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
            df = df[df['vacantes_solicitadas'] > 0]

            if not df.empty:
                # Mostrar detalle de vacantes con nombre de la vacante y empresa
                df_detalle = df[['empresa_vacante', 'puesto_vacante', 'plaza_vacante', 'vacantes_solicitadas']].copy()
                df_detalle = df_detalle.rename(columns={
                    "empresa_vacante": "Empresa", 
                    "puesto_vacante": "Puesto", 
                    "plaza_vacante": "Plaza",
                    "vacantes_solicitadas": "Vacantes"
                })
                # df_detalle['Empresa'] = df_detalle['Empresa'].replace(empresas_map)
                df_grafico = df_detalle.copy()
                df_grafico['Empresa'] = df_grafico['Empresa'].replace(empresas_map)
                df_detalle = df_detalle.groupby(['Empresa', 'Puesto', 'Plaza'], as_index=False).agg({'Vacantes': 'sum'})

                st.write('### Detalle de Vacantes por Empresa')
                df_detalle = df_detalle.sort_values(by='Vacantes', ascending=False)
                st.dataframe(df_detalle, hide_index=True)

                # Resumen por empresa
                resumen = df_grafico.groupby('Empresa')['Vacantes'].sum().reset_index()
                resumen = resumen.sort_values('Vacantes', ascending=False)
                with st.container():
                    st.write('### Resumen de Vacantes por Empresa')
                    
                    col1, col2 = st.columns([2, 2])
                    with col1:
                        st.dataframe(resumen, hide_index=True)

                    # Gráfico de pie
                    fig = px.pie(
                        resumen, 
                        values='Vacantes', 
                        names='Empresa', 
                        color='Empresa',
                        color_discrete_sequence=px.colors.sequential.ice_r
                    )
                    fig.update_layout(showlegend=False, font=dict(weight='bold', size=13))
                    with col2:
                        st.plotly_chart(fig)
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
            df = df[df['vacantes_solicitadas'].astype(int) > 0]
            if not df.empty:
                resumen = df.groupby('funcion_area_vacante')['vacantes_solicitadas'].sum().reset_index()
                columns_name = {
                    "funcion_area_vacante": "Función de área", 
                    "vacantes_solicitadas": "Vacantes"
                }
                resumen = resumen.rename(columns=columns_name)
                resumen = resumen.sort_values(by='Vacantes', ascending=False)
                st.write('### Vacantes por Función de Área')
                st.dataframe(resumen, hide_index=True)
                fig = px.bar(
                    resumen, 
                    x='Vacantes', 
                    y='Función de área',
                    text='Vacantes',
                    orientation='h',
                    color='Función de área',
                    color_discrete_sequence=px.colors.sequential.Teal,
                    title='Distribución de Vacantes por Función de Área'
                )
                fig.update_layout(showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
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

                fig = px.area(
                    resumen,
                    x='mes_alta',
                    y='contratados_alta',
                    title='Contrataciones por Mes',
                    labels={'mes_alta': 'Mes', 'contratados_alta': 'Contrataciones'},
                    color_discrete_sequence=px.colors.sequential.dense,
                    markers=True
                )
                st.plotly_chart(fig)
            else:
                st.info('No se encontró información de contrataciones en el periodo seleccionado.')
        else:
            st.info('No se encontró información de contrataciones.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por mes: {e}')

        
def grafica_contrataciones_mes_medio_reclutamiento(df_altas_filtrado):
    """
    Genera gráfica de líneas con contrataciones por mes y medio de reclutamiento.
    
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

                bar_info = (
                    df.groupby(['mes_alta', 'medio_reclutamiento_alta'])['contratados_alta']
                    .sum()
                    .reset_index()
                )
                line_info = (
                    df.groupby('mes_alta', as_index=False)['contratados_alta']
                    .sum()
                )

                bar_info['mes_alta'] = pd.Categorical(bar_info['mes_alta'], categories=meses_ordenados, ordered=True)
                line_info['mes_alta'] = pd.Categorical(line_info['mes_alta'], categories=meses_ordenados, ordered=True)

                bar_info = bar_info.sort_values('mes_alta')
                line_info = line_info.sort_values('mes_alta')

                fig = px.bar(
                    bar_info,
                    x='mes_alta',
                    y='contratados_alta',
                    color='medio_reclutamiento_alta',
                    title='Contrataciones por Mes y Medio de Reclutamiento',
                    labels={
                        'mes_alta': 'Mes',
                        'contratados_alta': 'Contrataciones',
                        'medio_reclutamiento_alta': 'Medio de Reclutamiento'
                    },
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )

                fig.add_scatter(
                    x=line_info['mes_alta'],
                    y=line_info['contratados_alta'],
                    mode='lines+markers',
                    name='Total Mensual',
                    line=dict(color='black', width=4),
                    marker=dict(size=8)
                )

                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f'Error al generar la gráfica de contrataciones por mes y medio: {e}')
