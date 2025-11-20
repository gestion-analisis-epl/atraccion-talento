import streamlit as st
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta
import calendar
import pytz
from utils.funciones_dashboard import calcular_dias_cobertura, obtener_rango_semana, obtener_rango_trimestre, filtrar_datos, empresas_map, meses_es, trimestres, MEXICO_TZ
from utils.graficas_dashboard import (
    grafica_contrataciones_mes,
    grafica_contrataciones_por_ejecutivo,
    grafica_contrataciones_por_medio_reclutamiento,
    grafica_vacantes_por_empresa,
    grafica_vacantes_por_area,
    grafica_embudo_fase_proceso
)

from utils.auth import require_login

# Requerir autenticación antes de mostrar cualquier contenido
require_login()

conn = st.connection("supabase", type=SupabaseConnection)

# ======================
# FILTROS
# ======================
st.write("### 📊 Dashboard de Reclutamiento")
st.markdown("---")

# Obtener datos completos
conteo_vacantes = conn.table("vacantes").select("*").execute()
todos_registros_vacantes = conteo_vacantes.data

data_altas = conn.table("altas").select("*").execute()
todos_registros_altas = data_altas.data

data_bajas = conn.table("bajas").select("*").execute()
todos_registros_bajas = data_bajas.data

# Preparar DataFrames
if todos_registros_vacantes:
    df_vacantes = pd.DataFrame(todos_registros_vacantes)
    df_vacantes['fecha_solicitud'] = pd.to_datetime(df_vacantes['fecha_solicitud'])
else:
    df_vacantes = pd.DataFrame()
    
if todos_registros_vacantes:
    df_vacantes_cerradas = pd.DataFrame(todos_registros_vacantes)
    df_vacantes_cerradas['fecha_cobertura'] = pd.to_datetime(df_vacantes_cerradas['fecha_cobertura'])
else:
    df_vacantes_cerradas = pd.DataFrame()

if todos_registros_altas:
    df_altas = pd.DataFrame(todos_registros_altas)
    df_altas['fecha_alta'] = pd.to_datetime(df_altas['fecha_alta'])
else:
    df_altas = pd.DataFrame()

if todos_registros_bajas:
    df_bajas = pd.DataFrame(todos_registros_bajas)
    df_bajas['fecha_registro_baja'] = pd.to_datetime(df_bajas['fecha_registro_baja'])
else:
    df_bajas = pd.DataFrame()

# Obtener años disponibles
años_disponibles = []
if not df_vacantes.empty:
    años_vacantes = df_vacantes['fecha_solicitud'].dt.year.dropna().unique().tolist()
    años_disponibles.extend(años_vacantes)
if not df_vacantes_cerradas.empty:
    años_vacantes_cerradas = df_vacantes_cerradas['fecha_cobertura'].dt.year.dropna().unique().tolist()
    años_disponibles.extend(años_vacantes_cerradas)
if not df_altas.empty:
    años_altas = df_altas['fecha_alta'].dt.year.dropna().unique().tolist()
    años_disponibles.extend(años_altas)
if not df_bajas.empty:
    años_bajas = df_bajas['fecha_registro_baja'].dt.year.dropna().unique().tolist()
    años_disponibles.extend(años_bajas)

# Filtrar valores NaN y convertir a enteros
años_disponibles = [int(año) for año in set(años_disponibles) if pd.notna(año)]
años_disponibles = sorted(años_disponibles, reverse=True)

if not años_disponibles:
    años_disponibles = [datetime.now(MEXICO_TZ).year]

# Interfaz de filtros
col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 2])

with col_f1:
    tipo_filtro = st.selectbox(
        "🗓️ Tipo de filtro",
        ["Todo el tiempo", "Por año", "Por trimestre", "Por mes", "Por semana"],
        index=0
    )

año_seleccionado = None
mes_seleccionado = None
semana_seleccionada = None
trimestre_seleccionado = None

if tipo_filtro in ["Por año", "Por trimestre", "Por mes", "Por semana"]:
    with col_f2:
        año_seleccionado = st.selectbox("Año", años_disponibles)

if tipo_filtro == "Por trimestre" and año_seleccionado:
    with col_f3:
        trimestres_opciones = [trimestres[t]['nombre'] for t in [1, 2, 3, 4]]
        trimestre_nombre = st.selectbox("Trimestre", trimestres_opciones, index=0)
        # Extraer el número del trimestre (T1, T2, T3, T4)
        trimestre_seleccionado = int(trimestre_nombre[1])
    with col_f4:
        if trimestre_seleccionado:
            inicio, fin = obtener_rango_trimestre(año_seleccionado, trimestre_seleccionado)
            st.info(f"📅 {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")

if tipo_filtro == "Por mes" and año_seleccionado:
    with col_f3:
        meses_opciones = list(meses_es.values())
        mes_nombre = st.selectbox("Mes", meses_opciones, index=datetime.now(MEXICO_TZ).month - 1)
        mes_seleccionado = list(meses_es.keys())[list(meses_es.values()).index(mes_nombre)]

if tipo_filtro == "Por semana" and año_seleccionado:
    with col_f3:
        # Calcular número máximo de semanas ISO para el año seleccionado (28 dic siempre cae en la última semana ISO)
        try:
            max_semana = int(datetime(int(año_seleccionado), 12, 28).isocalendar()[1])
        except Exception:
            max_semana = 52
        
        # Asegurar que max_semana sea un entero válido
        if not isinstance(max_semana, int) or max_semana < 1:
            max_semana = 52
            
        semanas_opciones = [i for i in range(1, max_semana + 1)]
        
        # Definir índice por defecto: si el año seleccionado es el actual, usar la semana actual; si no, 0
        default_idx = 0
        if int(año_seleccionado) == datetime.now(MEXICO_TZ).year:
            try:
                current_week = int(datetime.now(MEXICO_TZ).isocalendar()[1])
                default_idx = min(current_week - 1, len(semanas_opciones) - 1)
            except Exception:
                default_idx = 0
        semana_seleccionada = st.selectbox("Semana", semanas_opciones, index=default_idx)
    with col_f4:
        if semana_seleccionada:
            inicio, fin = obtener_rango_semana(año_seleccionado, semana_seleccionada)
            st.info(f"📅 {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")

st.markdown("---")

# Aplicar filtros
df_vacantes_filtrado = filtrar_datos(df_vacantes, 'fecha_solicitud', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado)
df_vacantes_cerradas_filtrado = filtrar_datos(df_vacantes_cerradas, 'fecha_cobertura', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado)
df_altas_filtrado = filtrar_datos(df_altas, 'fecha_alta', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado)
df_bajas_filtrado = filtrar_datos(df_bajas, 'fecha_registro_baja', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado)

# ======================
# MÉTRICAS PRINCIPALES
# ======================
st.write("### 📈 Métricas principales")

col1, col2, col3 = st.columns([2, 2, 2])

# No. CONTRATADOS
if not df_altas_filtrado.empty:
    n_contratados = df_altas_filtrado['contratados_alta'].astype(int).sum()
else:
    n_contratados = 0
    with col1:st.info(f'No hay altas registradas en el período seleccionado.')
col1.metric(label='Contratados Totales', value=n_contratados)

try:
    if not df_bajas_filtrado.empty:
        df_bajas = df_bajas_filtrado[df_bajas_filtrado['id'] > 0].copy()
        n_bajas = len(df_bajas)
    else:
        n_bajas = 0
        with col2: st.info(f'No hay bajas registradas en el período seleccionado.')
    col2.metric(label='Bajas Totales', value=n_bajas)
except Exception as e:
    st.error(f'Error al calcular bajas: {e}')

# No. VACANTES
if not df_vacantes.empty:
    n_vacantes = df_vacantes[df_vacantes['fecha_autorizacion'].notna()]['vacantes_solicitadas'].astype(int).sum()
else:
    n_vacantes = 0
    st.error(f'Error al calcular vacantes. No se encontraron datos.')
d = ((n_vacantes-28)/28)*100 # Valor fijo para delta. Se debe cambiar cada semana según vacantes abiertas
col3.metric(label='Vacantes disponibles a la fecha', value=n_vacantes, delta=f"{d:.2f}%")

# Requisiciones vs Contrataciones
if not df_altas_filtrado.empty and not df_vacantes.empty:
    st.write("### 📉 Requisiciones vs Contrataciones")
    porcentaje = round((n_contratados / n_vacantes)*100, 2) 
    st.metric(label="Requisiciones VS Contrataciones", value=f'{porcentaje}%')
elif df_altas_filtrado.empty and not df_vacantes.empty:
    st.error("No hay altas registradas en el período seleccionado.")
elif not df_altas_filtrado.empty and df_vacantes.empty:
    st.error("No hay vacantes registradas en el período seleccionado.")
else:
    st.error("Error al calcular requisiciones vs contrataciones.")

st.divider()

# ======================
# DIAS DE COBERTURA
# ======================

st.write("### ⏱️ Días promedio de cobertura")

col4, col5, col6 = st.columns([2, 2, 2])

# Vacantes Abiertas
try:
    if not df_vacantes.empty:
        df_cobertura =df_vacantes[(df_vacantes['vacantes_solicitadas'] > 0) & (df_vacantes['fecha_autorizacion'].notna())].copy()
        if not df_cobertura.empty:
            df_cobertura['dias_calculados'] = df_cobertura.apply(calcular_dias_cobertura, axis=1)
            promedio_cobertura = df_cobertura['dias_calculados'].dropna().mean()
            col4.metric(
                label='Promedio en vacantes disponibles', 
                value=f"{promedio_cobertura:.0f}" if pd.notna(promedio_cobertura) else "0",
                border=True
            )
        else:
            col4.metric(label='Promedio en vacantes disponibles', value="0", border=True)
    else:
        col4.metric(label='Promedio en vacantes disponibles', value="0", border=True)
except Exception as e:
    st.error(f'Error al calcular cobertura: {e}')
    col4.metric(label='Promedio en vacantes disponibles', value="Error", border=True)

# Vacantes ADMINISTRATIVAS
try:
    if not df_vacantes.empty:
        # Filtrar solo las vacantes ADMINISTRATIVAS
        df_administrativas = df_vacantes[
            (df_vacantes['funcion_area_vacante'] == 'ADMINISTRATIVA') &
            (df_vacantes['vacantes_solicitadas'] > 0) &
            (df_vacantes['fecha_autorizacion'].notna())
        ].copy()

        if not df_administrativas.empty:
            df_administrativas['dias_calculados'] = df_administrativas.apply(calcular_dias_cobertura, axis=1)
            promedio_cobertura = df_administrativas['dias_calculados'].dropna().mean()

            col5.metric(
                label='Promedio en Administrativas',
                value=f"{promedio_cobertura:.0f}" if pd.notna(promedio_cobertura) else "0",
                border=True
            )
        else:
            col5.metric(label='Promedio en Administrativas', value="0", border=True)
    else:
        col5.metric(label='Promedio en Administrativas', value="0", border=True)

except Exception as e:
    st.error(f'Error al calcular cobertura: {e}')
    col5.metric(label='Promedio en Administrativas', value="Error", border=True)

# Vacantes OPERATIVAS
try:
    if not df_vacantes.empty:
        # Filtrar solo las vacantes OPERATIVAS
        df_operativas = df_vacantes[
            (df_vacantes['funcion_area_vacante'] == 'OPERATIVA') &
            (df_vacantes['vacantes_solicitadas'] > 0) &
            (df_vacantes['fecha_autorizacion'].notna())
        ].copy()

        if not df_operativas.empty:
            df_operativas['dias_calculados'] = df_operativas.apply(calcular_dias_cobertura, axis=1)
            promedio_cobertura = df_operativas['dias_calculados'].dropna().mean()

            col6.metric(
                label='Promedio en Operativas',
                value=f"{promedio_cobertura:.0f}" if pd.notna(promedio_cobertura) else "0",
                border=True
            )
        else:
            col6.metric(label='Promedio en Operativas', value="0", border=True)
    else:
        col6.metric(label='Promedio en Operativas', value="0", border=True)

except Exception as e:
    st.error(f'Error al calcular cobertura: {e}')
    col6.metric(label='Promedio en Operativas', value="Error", border=True)

st.divider()

st.write("### ⏱️ Días promedio de cobertura en vacantes finalizadas")

col7, col8, col9 = st.columns([2, 2, 2])

# Vacantes Cerradas
try:
    if not df_vacantes_cerradas_filtrado.empty:
        df_contratacion = df_vacantes_cerradas_filtrado[df_vacantes_cerradas_filtrado['vacantes_contratados'] > 0].copy()
        if not df_contratacion.empty:
            df_contratacion['dias_calculados'] = df_contratacion.apply(calcular_dias_cobertura, axis=1)
            promedio_contratacion = df_contratacion['dias_calculados'].dropna().mean()
            col7.metric(
               label='Promedio en Vacantes finalizadas',
               value=f"{promedio_contratacion:.0f}" if pd.notna(promedio_contratacion) else "0",
               border=True
            )
        else:
            col7.metric(label='Promedio en Vacantes finalizadas', value="0", border=True)
    else:
        col7.metric(label='Promedio en Vacantes finalizadas', value="0", border=True)
except Exception as e:
    st.error(f'Error al calcular contratación: {e}')
    col7.metric(label='Promedio en Vacantes finalizadas', value="Error", border=True)
    
# Vacantes ADMINISTRATIVAS cerradas
try:
    if not df_vacantes_cerradas_filtrado.empty:
        # Filtrar solo las vacantes ADMINISTRATIVAS
        df_administrativas = df_vacantes_cerradas_filtrado[
            (df_vacantes_cerradas_filtrado['funcion_area_vacante'] == 'ADMINISTRATIVA') &
            (df_vacantes_cerradas_filtrado['vacantes_contratados'] > 0)
        ].copy()

        if not df_administrativas.empty:
            df_administrativas['dias_calculados'] = df_administrativas.apply(calcular_dias_cobertura, axis=1)
            promedio_cobertura = df_administrativas['dias_calculados'].dropna().mean()

            col8.metric(
                label='Promedio en Administrativas',
                value=f"{promedio_cobertura:.0f}" if pd.notna(promedio_cobertura) else "0",
                border=True
            )
        else:
            col8.metric(label='Promedio en Administrativas', value="0", border=True)
    else:
        col8.metric(label='Promedio en Administrativas', value="0", border=True)

except Exception as e:
    st.error(f'Error al calcular cobertura: {e}')
    col8.metric(label='Promedio en Administrativas', value="Error", border=True)

# Vacantes OPERATIVAS cerradas
try:
    if not df_vacantes_cerradas_filtrado.empty:
        # Filtrar solo las vacantes OPERATIVAS
        df_operativas = df_vacantes_cerradas_filtrado[
            (df_vacantes_cerradas_filtrado['funcion_area_vacante'] == 'OPERATIVA') &
            (df_vacantes_cerradas_filtrado['vacantes_contratados'] > 0)
        ].copy()

        if not df_operativas.empty:
            df_operativas['dias_calculados'] = df_operativas.apply(calcular_dias_cobertura, axis=1)
            promedio_cobertura = df_operativas['dias_calculados'].dropna().mean()

            col9.metric(
                label='Promedio en Operativas',
                value=f"{promedio_cobertura:.0f}" if pd.notna(promedio_cobertura) else "0",
                border=True
            )
        else:
            col9.metric(label='Promedio en Operativas', value="0", border=True)
    else:
        col9.metric(label='Promedio en Operativas', value="0", border=True)

except Exception as e:
    st.error(f'Error al calcular cobertura: {e}')
    col9.metric(label='Promedio en Operativas', value="Error", border=True)
    
st.divider()
st.write("### 📋 Detalle de las contrataciones")
try:
    if not df_altas_filtrado.empty:
        confidencial = df_altas_filtrado['confidencial'] != 'SI'
        st.dataframe(df_altas_filtrado[confidencial],
                     column_config={
                         "id": None,
                         "id_registro": None,
                         "fecha_alta": None,
                         "empresa_alta": "Empresa",
                         "puesto_alta": "Puesto",
                         "plaza_alta": "Plaza",
                         "area_alta": "Área",
                         "contratados_alta": None,
                         "medio_reclutamiento_alta": "Medio de reclutamiento",
                         "responsable_alta": "Ejecutivo de reclutamiento",
                     }, hide_index=True, width="stretch")
    else:
        st.write("No hay datos disponibles para mostrar.")
except Exception as e:
    st.error(f'Error al mostrar datos detallados: {e}')

st.divider()

# ======================
# GRAFICAS
# ======================

st.write("### 📊 Análisis visual")

# Gráficas de contrataciones (con filtro)
st.write("#### Contrataciones por Ejecutivo")
grafica_contrataciones_por_ejecutivo(df_altas_filtrado)

st.write("#### Contrataciones por Medio de Reclutamiento")
grafica_contrataciones_por_medio_reclutamiento(df_altas_filtrado)

st.write("#### Contrataciones por Mes")
grafica_contrataciones_mes(df_altas_filtrado)
# grafica_contrataciones_mes_medio_reclutamiento(df_altas_filtrado)

# Gráficas de vacantes (sin filtro - todo el tiempo)
st.divider()
st.write("### Vacantes por Empresa")
grafica_vacantes_por_empresa(df_vacantes)

st.divider()
st.write("### Vacantes por Área")
grafica_vacantes_por_area(df_vacantes)

st.divider()
st.write("### Embudo de Vacantes por Fase de Proceso")
grafica_embudo_fase_proceso(df_vacantes)
