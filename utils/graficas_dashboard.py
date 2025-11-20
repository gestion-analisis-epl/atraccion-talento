"""
Módulo de gráficas para el dashboard de reclutamiento.
Contiene funciones reutilizables para generar visualizaciones de datos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.funciones_dashboard import empresas_map, calcular_dias_cobertura
    
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
                df['primer_nombre'] = df['primer_nombre'].replace({'MARTA': 'HELEN', "SIN ESPECIFICAR": "SIN ESPECIFICAR"})
                resumen = df.groupby('primer_nombre')['contratados_alta'].sum().reset_index()
                resumen = resumen.sort_values('contratados_alta', ascending=False)
                fig = px.bar(
                    resumen, 
                    x='contratados_alta', 
                    y='primer_nombre', 
                    orientation='h', 
                    text='contratados_alta', 
                    color='primer_nombre',
                    color_discrete_sequence=px.colors.sequential.Hot_r,
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
            
            df = df[(df['vacantes_solicitadas'] > 0) & (df['fecha_autorizacion'].notna())]

            if not df.empty:
                # Calcular días de cobertura actualizados para cada vacante
                df['dias_cobertura_calculados'] = df.apply(calcular_dias_cobertura, axis=1)
                
                # Mostrar detalle de vacantes con nombre de la vacante y empresa
                df_detalle = df[['id_sistema', 'empresa_vacante', 'puesto_vacante', 'plaza_vacante', 'vacantes_solicitadas', 'dias_cobertura_calculados']].copy()
                df_detalle = df_detalle.rename(columns={
                    "id_sistema": "ID",
                    "empresa_vacante": "Empresa", 
                    "puesto_vacante": "Puesto", 
                    "plaza_vacante": "Plaza",
                    "vacantes_solicitadas": "Vacantes",
                    "dias_cobertura_calculados": "Días de cobertura"
                })
                # df_detalle['Empresa'] = df_detalle['Empresa'].replace(empresas_map)
                df_grafico = df_detalle.copy()
                df_grafico['Empresa'] = df_grafico['Empresa'].replace(empresas_map)
                #df_detalle = df_detalle.groupby(['Empresa', 'Puesto', 'Plaza'], as_index=False).agg({
                #    'Vacantes': 'sum',
                #    'Días de cobertura': 'mean'  # Promedio de días de cobertura por agrupación
                #})
                df_detalle['Días de cobertura'] = df_detalle['Días de cobertura'].round(0).astype(int)

                st.write('### Detalle de Vacantes por Empresa')
                df_detalle = df_detalle.sort_values(by='Días de cobertura', ascending=False)
                confidencial = df['confidencial'] != 'SI'
                df_detalle = df_detalle[confidencial]
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
                        color_discrete_sequence=px.colors.sequential.Sunset
                    )
                    fig.update_layout(showlegend=True, font=dict(weight='bold', size=13))
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
            df = df[(df['vacantes_solicitadas'].astype(int) > 0) & (df['fecha_autorizacion'].notna())]
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
                    color_discrete_sequence=px.colors.sequential.Emrld,
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
                df = df.loc[(df["fase_proceso"] != "CONTRATADO") & (df["estatus_solicitud"] != "PENDIENTE") & df['fecha_autorizacion'].notna() & (df["estatus_solicitud"] != "CANCELADO")]
                
                # Contar por fase de proceso
                conteo = df['fase_proceso'].value_counts().reset_index()
                conteo.columns = ['fase_proceso', 'cantidad']
                conteo = conteo.sort_values('cantidad', ascending=True)
                
                fig = px.funnel(
                    conteo,
                    x='cantidad',
                    y='fase_proceso',
                    title='Embudo de Vacantes por Fase de Proceso',
                    labels={'cantidad': 'Cantidad', 'fase_proceso': 'Fase del Proceso'},
                    color='fase_proceso',
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_layout(showlegend=False, font=dict(weight='bold', size=13))
                st.plotly_chart(fig)
            else:
                st.info('No se encontraron fases de proceso registradas.')
        else:
            st.info('No se encontraron registros de vacantes.')
    except Exception as e:
        st.error(f'Error al generar la gráfica de embudo por fase de proceso: {e}')
