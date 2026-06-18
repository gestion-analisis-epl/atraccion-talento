import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta
import calendar
import pytz
from utils.funciones_dashboard import calcular_dias_cobertura, promedio_dias_cerradas, obtener_rango_semana, obtener_rango_trimestre, filtrar_datos, filtrar_por_ejecutivo, meses_es, trimestres, MEXICO_TZ
from utils.graficas_dashboard import (
    grafica_contrataciones_mes,
    grafica_contrataciones_por_ejecutivo,
    grafica_contrataciones_por_medio_reclutamiento,
    grafica_vacantes_por_empresa,
    grafica_vacantes_por_area,
    grafica_embudo_fase_proceso,
    grafica_contrataciones_por_empresa,
    contrataciones_area_redes_pagadas,
    promedio_plaza_puesto,
    tabla_dinamica_contrataciones,
)
from utils.auth import require_login
from utils.logger import get_logger

logger = get_logger(__name__)

# Requerir autenticación antes de mostrar cualquier contenido
require_login()

conn = st.connection("supabase", type=SupabaseConnection)

# Filtros

data_actualizacion = (conn.table("registros_rh").select("ultima_actualizacion").order("ultima_actualizacion", desc=True).limit(1).execute())

# Snapshot más reciente para delta dinámico (ordenado por año y semana real, no por fecha de inserción)
snap_resp = (
    conn.table("snapshot_vacantes_semanales")
    .select("n_vacantes, semana_iso, año")
    .order("año", desc=True)
    .order("semana_iso", desc=True)
    .limit(1)
    .execute()
)

snap_anterior         = snap_resp.data[0] if snap_resp.data else None
n_vacantes_anterior   = int(snap_anterior["n_vacantes"]) if snap_anterior else None
semana_anterior_label = f"S{snap_anterior['semana_iso']} {snap_anterior['año']}" if snap_anterior else ""
ultima_actualizacion = data_actualizacion.data[0]['ultima_actualizacion']


ultima_fecha = datetime.strptime(ultima_actualizacion, '%Y-%m-%d').date()
st.markdown(f"""
<div class="dash-header">
    <span class="dash-title">Dashboard de Reclutamiento</span>
    <span class="dash-badge">Actualizado: {ultima_fecha}</span>
</div>
""", unsafe_allow_html=True)


# Obtener datos completos
conteo_vacantes = (conn.table("vacantes")
.select("""
        id, id_registro, fecha_solicitud, tipo_solicitud, estatus_solicitud, fase_proceso,
        fecha_avance, fecha_autorizacion, puesto_vacante, plaza_vacante, empresa_vacante,
        funcion_area_vacante, vacantes_solicitadas, vacantes_contratados, responsable_vacante,
        comentarios_vacante, tipo_reclutamiento_vacante, medio_reclutamiento_vacante, fecha_cobertura,
        id_sistema, confidencial
        """).execute())
todos_registros_vacantes = conteo_vacantes.data

data_altas = (conn.table("altas")
              .select("""
                      id, id_registro, fecha_alta, empresa_alta, puesto_alta, plaza_alta, area_alta,
                      contratados_alta, medio_reclutamiento_alta, responsable_alta, confidencial
                      """).execute())
todos_registros_altas = data_altas.data

data_bajas = (conn.table("bajas_sistema")
              .select("*")
              .gte("fecha_baja", "2024-01-01")
              .lte("fecha_baja", "2026-12-31")
              .execute())
todos_registros_bajas = data_bajas.data

data_catalogo_docs = conn.table("catalogo_documentos").select("*").execute()
data_colaboradores = conn.table("colaboradores_activos").select("*").execute()

# archivos_expedientes supera 1 000 filas — se pagina para traer todos los registros
_arch_rows, _arch_offset = [], 0
while True:
    _page = (
        conn.table("archivos_expedientes")
        .select("id_colaborador, id_documento, estatus_pdf")
        .range(_arch_offset, _arch_offset + 999)
        .execute()
    )
    if not _page.data:
        break
    _arch_rows.extend(_page.data)
    if len(_page.data) < 1000:
        break
    _arch_offset += 1000

# Preparar DataFrames
if todos_registros_vacantes:
    df_vacantes = pd.DataFrame(todos_registros_vacantes)
    df_vacantes['fecha_solicitud']      = pd.to_datetime(df_vacantes['fecha_solicitud'])
    df_vacantes['fecha_cobertura']      = pd.to_datetime(df_vacantes['fecha_cobertura'])
    df_vacantes['fecha_autorizacion']   = pd.to_datetime(df_vacantes['fecha_autorizacion'])
    df_vacantes['vacantes_contratados'] = pd.to_numeric(df_vacantes['vacantes_contratados'], errors='coerce').fillna(0).astype(int)
    df_vacantes_cerradas = df_vacantes
else:
    df_vacantes = pd.DataFrame()
    df_vacantes_cerradas = pd.DataFrame()

if todos_registros_altas:
    df_altas = pd.DataFrame(todos_registros_altas)
    df_altas['fecha_alta'] = pd.to_datetime(df_altas['fecha_alta'])
else:
    df_altas = pd.DataFrame()

if todos_registros_bajas:
    df_bajas = pd.DataFrame(todos_registros_bajas)
    df_bajas['fecha_baja'] = pd.to_datetime(df_bajas['fecha_baja'])
else:
    df_bajas = pd.DataFrame()
    
df_catalogo_docs = pd.DataFrame(data_catalogo_docs.data) if data_catalogo_docs.data else pd.DataFrame()
df_colaboradores = pd.DataFrame(data_colaboradores.data) if data_colaboradores.data else pd.DataFrame()
df_archivos      = pd.DataFrame(_arch_rows) if _arch_rows else pd.DataFrame()

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
    años_bajas = df_bajas['fecha_baja'].dt.year.dropna().unique().tolist()
    años_disponibles.extend(años_bajas)

# Filtrar valores NaN y convertir a enteros
años_disponibles = [int(año) for año in set(años_disponibles) if pd.notna(año)]
años_disponibles = sorted(años_disponibles, reverse=True)

if not años_disponibles:
    años_disponibles = [datetime.now(MEXICO_TZ).year]

ejecutivos_disponibles = ["Todos", "DIEGO", "HELEN", "LETY", "YULIANA"]

# Interfaz de filtros
col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([2, 2, 2, 2, 2])

with col_f1:
    tipo_filtro = st.selectbox(
        ":material/filter_alt: Tipo de filtro",
        ["Todo el tiempo", "Por año", "Por trimestre", "Por mes", "Por semana", "Por rango de fechas"],
        index=0
    )

with col_f5:
    ejecutivo_seleccionado = st.selectbox(
        ":material/person: Ejecutivo",
        ejecutivos_disponibles,
        index=0
    )

año_seleccionado = None
mes_seleccionado = None
semana_seleccionada = None
trimestre_seleccionado = None
fecha_inicio = None
fecha_fin = None

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
            st.info(f":material/calendar_today: {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")

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
            st.info(f":material/calendar_today: {inicio.strftime('%d/%m/%Y')} - {fin.strftime('%d/%m/%Y')}")

if tipo_filtro == "Por rango de fechas":
    with col_f2:
        fecha_inicio = st.date_input(
            "Fecha de inicio",
            value=datetime.now(MEXICO_TZ).date() - timedelta(days=30),
            format="DD/MM/YYYY"
        )
    with col_f3:
        fecha_fin = st.date_input(
            "Fecha de fin",
            value=datetime.now(MEXICO_TZ).date(),
            format="DD/MM/YYYY"
        )
    with col_f4:
        if fecha_inicio and fecha_fin:
            st.info(f":material/calendar_today: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")

st.markdown("---")

# Aplicar filtros
df_vacantes_filtrado = filtrar_datos(df_vacantes, 'fecha_solicitud', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
df_vacantes_cerradas_filtrado = filtrar_datos(df_vacantes_cerradas, 'fecha_cobertura', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
df_altas_filtrado = filtrar_datos(df_altas, 'fecha_alta', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
df_bajas_filtrado = filtrar_datos(df_bajas, 'fecha_baja', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
df_requisiciones_filtrado = filtrar_datos(df_vacantes, 'fecha_autorizacion', tipo_filtro, año_seleccionado, mes_seleccionado, semana_seleccionada, trimestre_seleccionado, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)

if ejecutivo_seleccionado != "Todos":
    df_altas_filtrado             = filtrar_por_ejecutivo(df_altas_filtrado,             'responsable_alta',      ejecutivo_seleccionado)
    df_vacantes_cerradas_filtrado = filtrar_por_ejecutivo(df_vacantes_cerradas_filtrado, 'responsable_vacante',   ejecutivo_seleccionado)
    df_requisiciones_filtrado     = filtrar_por_ejecutivo(df_requisiciones_filtrado,     'responsable_vacante',   ejecutivo_seleccionado)
vacantes_excluir = (
    (df_vacantes['estatus_solicitud'] == 'CANCELADO') |
    (df_vacantes['estatus_solicitud'] == 'FINALIZADO') |
    (df_vacantes['estatus_solicitud'] == 'PAUSADO') |
    (df_vacantes['fase_proceso'] == 'CONTRATADO')
) if not df_vacantes.empty else pd.Series(dtype=bool)

st.write("### :material/search_insights: Métricas principales")
tab1, tab6, tab2, tab3, tab4, tab5 = st.tabs([":material/search_insights: Métricas Principales", ":material/files: Expedientes", ":material/analytics: Análisis Visual", ":material/info: Información de Vacantes", ":material/article_person: Redes Pagadas", ":material/analytics: Promedio de Plaza y Puesto"])
with tab1:
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
        logger.error("Error al calcular bajas: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")

    # No. VACANTES
    if not df_vacantes.empty:
        n_vacantes = df_vacantes[df_vacantes['fecha_autorizacion'].notna() & ~vacantes_excluir]['vacantes_solicitadas'].astype(int).sum()
    else:
        n_vacantes = 0
        st.error(f'Error al calcular vacantes. No se encontraron datos.')
    if n_vacantes_anterior and n_vacantes_anterior > 0:
        d = ((n_vacantes - n_vacantes_anterior) / n_vacantes_anterior) * 100
        delta_str = f"{d:+.1f}%"
    else:
        delta_str = None
    col3.metric(label='Vacantes disponibles a la fecha', value=n_vacantes, delta=delta_str, delta_color="inverse")

    # Requisiciones vs Contrataciones
    total_requisiciones = df_requisiciones_filtrado['vacantes_solicitadas'].astype(int).sum() + df_requisiciones_filtrado['vacantes_contratados'].astype(int).sum()
    total_no_requisitadas = (df_requisiciones_filtrado['fase_proceso'] == "SIN SOLICITUD DE REQUISICION").sum()
    if not df_requisiciones_filtrado.empty:
        with col1:
            st.metric(label="Requisiciones Totales", value=total_requisiciones)
        with col2:
            st.metric(label="Vacantes no requisitadas", value=total_no_requisitadas)
    if not df_altas_filtrado.empty and not df_vacantes.empty:
        with col3:
            if total_requisiciones > 0:
                porcentaje = round((n_contratados / total_requisiciones)*100, 2) 
                st.metric(label="Requisiciones VS Contrataciones", value=f'{porcentaje}%')
            else:
                st.metric(label="Requisiciones VS Contrataciones", value="0%")
    elif df_altas_filtrado.empty and not df_vacantes.empty:
        st.error("No hay altas registradas en el período seleccionado.")
    elif not df_altas_filtrado.empty and df_vacantes.empty:
        st.error("No hay vacantes registradas en el período seleccionado.")
    else:
        st.error("Error al calcular requisiciones vs contrataciones.")

    st.divider()

    with st.expander("Días promedio de cobertura"):
        st.write("### :material/clock_loader_20: Días promedio de cobertura")

        col4, col5, col6 = st.columns([2, 2, 2])
        
        # Vacantes Abiertas
        try:
            if not df_vacantes.empty:
                df_cobertura = df_vacantes[
                    (df_vacantes['fase_proceso'] != 'CONTRATADO') &
                    (df_vacantes['estatus_solicitud'] != 'FINALIZADO') &
                    (df_vacantes['estatus_solicitud'] != 'PAUSADO') &
                    (df_vacantes['estatus_solicitud'] != 'CANCELADO') &
                    (df_vacantes['fecha_autorizacion'].notna()) &
                    (df_vacantes['fecha_autorizacion'] != pd.Timestamp('1900-01-01'))
                ]
                
                if not df_cobertura.empty:
                    df_cobertura['dias_calculados'] = df_cobertura.apply(calcular_dias_cobertura, axis=1)
                    promedio_cobertura = df_cobertura['dias_calculados'].dropna().mean()
                    col4.metric(
                        label='Promedio en vacantes disponibles', 
                        value=f"{round(promedio_cobertura)}" if pd.notna(promedio_cobertura) else "0",
                        border=True
                    )
                else:
                    col4.metric(label='Promedio en vacantes disponibles', value="0", border=True)
            else:
                col4.metric(label='Promedio en vacantes disponibles', value="0", border=True)
        except Exception as e:
            logger.error("Error al calcular cobertura: %s", e, exc_info=True)
            st.error("Ocurrió un error inesperado. Por favor recarga la página.")
            col4.metric(label='Promedio en vacantes disponibles', value="Error", border=True)

        # Vacantes ADMINISTRATIVAS
        try:
            if not df_vacantes.empty:
                # Filtrar solo las vacantes ADMINISTRATIVAS
                df_administrativas = df_vacantes[
                    (df_vacantes['funcion_area_vacante'] == 'ADMINISTRATIVA') &
                    (df_vacantes['fase_proceso'] != 'CONTRATADO') &
                    (df_vacantes['estatus_solicitud'] != 'FINALIZADO') &
                    (df_vacantes['estatus_solicitud'] != 'PAUSADO') &
                    (df_vacantes['estatus_solicitud'] != 'CANCELADO') &
                    (df_vacantes['fecha_autorizacion'].notna()) &
                    (df_vacantes['fecha_autorizacion'] != pd.Timestamp('1900-01-01'))
                ].copy()

                if not df_administrativas.empty:
                    df_administrativas['dias_calculados'] = df_administrativas.apply(calcular_dias_cobertura, axis=1)
                    promedio_cobertura = df_administrativas['dias_calculados'].dropna().mean()
                    col5.metric(
                        label='Promedio en Administrativas',
                        value=f"{round(promedio_cobertura)}" if pd.notna(promedio_cobertura) else "0",
                        border=True
                    )
                else:
                    col5.metric(label='Promedio en Administrativas', value="0", border=True)
            else:
                col5.metric(label='Promedio en Administrativas', value="0", border=True)

        except Exception as e:
            logger.error("Error al calcular cobertura: %s", e, exc_info=True)
            st.error("Ocurrió un error inesperado. Por favor recarga la página.")
            col5.metric(label='Promedio en Administrativas', value="Error", border=True)

        # Vacantes OPERATIVAS
        try:
            if not df_vacantes.empty:
                # Filtrar solo las vacantes OPERATIVAS
                df_operativas = df_vacantes[
                    (df_vacantes['funcion_area_vacante'] == 'OPERATIVA') &
                    (df_vacantes['fase_proceso'] != 'CONTRATADO') &
                    (df_vacantes['estatus_solicitud'] != 'FINALIZADO') &
                    (df_vacantes['estatus_solicitud'] != 'PAUSADO') &
                    (df_vacantes['estatus_solicitud'] != 'CANCELADO') &
                    (df_vacantes['fecha_autorizacion'].notna()) &
                    (df_vacantes['fecha_autorizacion'] != pd.Timestamp('1900-01-01'))
                ].copy()

                if not df_operativas.empty:
                    df_operativas['dias_calculados'] = df_operativas.apply(calcular_dias_cobertura, axis=1)
                    promedio_cobertura = df_operativas['dias_calculados'].dropna().mean()
                    col6.metric(
                        label='Promedio en Operativas',
                        value=f"{round(promedio_cobertura)}" if pd.notna(promedio_cobertura) else "0",
                        border=True
                    )
                else:
                    col6.metric(label='Promedio en Operativas', value="0", border=True)
            else:
                col6.metric(label='Promedio en Operativas', value="0", border=True)

        except Exception as e:
            logger.error("Error al calcular cobertura: %s", e, exc_info=True)
            st.error("Ocurrió un error inesperado. Por favor recarga la página.")
            col6.metric(label='Promedio en Operativas', value="Error", border=True)

    st.divider()
    
    st.write("### :material/clock_loader_90: Días promedio de cobertura en vacantes finalizadas")

    col7, col8, col9 = st.columns([2, 2, 2])

    # Vacantes Cerradas
    try:
        promedio_contratacion = promedio_dias_cerradas(df_vacantes_cerradas_filtrado)
        col7.metric(
            label='Promedio en Vacantes finalizadas',
            value=f"{round(promedio_contratacion)}" if promedio_contratacion is not None else "0",
            border=True,
        )
    except Exception as e:
        logger.error("Error al calcular contratación: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")
        col7.metric(label='Promedio en Vacantes finalizadas', value="Error", border=True)

    # Vacantes ADMINISTRATIVAS cerradas
    try:
        promedio_cobertura = promedio_dias_cerradas(df_vacantes_cerradas_filtrado, 'ADMINISTRATIVA')
        if promedio_cobertura is not None and promedio_cobertura > 0:
            valor = 45 / promedio_cobertura * 100
            ponderacion = f'{valor:.2f}%'
            delta_color = "inverse" if valor < 100 else "normal"
        else:
            ponderacion = None
            delta_color = "off"
        col8.metric(
            label='Promedio en Administrativas',
            value=f"{round(promedio_cobertura)}" if promedio_cobertura is not None else "0",
            border=True,
            delta=ponderacion,
            delta_color=delta_color,
        )
    except Exception as e:
        logger.error("Error al calcular cobertura: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")
        col8.metric(label='Promedio en Administrativas', value="Error", border=True)

    # Vacantes OPERATIVAS cerradas
    try:
        promedio_cobertura = promedio_dias_cerradas(df_vacantes_cerradas_filtrado, 'OPERATIVA')
        if promedio_cobertura is not None and promedio_cobertura > 0:
            valor = 15 / promedio_cobertura * 100
            ponderacion = f'{valor:.2f}%'
            delta_color = "inverse" if valor < 100 else "normal"
        else:
            ponderacion = None
            delta_color = "off"
        col9.metric(
            label='Promedio en Operativas',
            value=f"{round(promedio_cobertura)}" if promedio_cobertura is not None else "0",
            border=True,
            delta=ponderacion,
            delta_color=delta_color,
        )
    except Exception as e:
        logger.error("Error al calcular cobertura: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")
        col9.metric(label='Promedio en Operativas', value="Error", border=True)
        
    st.divider()

    st.write("### :material/docs: Detalle de las contrataciones")
    try:
        if not df_altas_filtrado.empty:
            df = df_altas_filtrado.copy()
            df['fecha_alta'] = df['fecha_alta'].dt.date
            df = df.rename(columns={
                'empresa_alta': 'Empresa',
                "puesto_alta": "Puesto",
                "plaza_alta": "Plaza",
                "area_alta": "Área",
                'fecha_alta': 'Fecha de contratación',
                "medio_reclutamiento_alta": "Medio de reclutamiento",
                "responsable_alta": "Ejecutivo de reclutamiento",
                'contratados_alta': 'Contratados',
                'confidencial': 'Confidencial',
            })
            df.loc[df['Confidencial'] == 'SI', 'Puesto'] = 'VACANTE'
            st.dataframe(df,
                        column_config={
                            "id": None,
                            "id_registro": None,
                            "contratados_alta": None, 
                            'Confidencial': None,
                        }, hide_index=True, width="stretch")
        else:
            st.write("No hay datos disponibles para mostrar.")
    except Exception as e:
        logger.error("Error al mostrar datos detallados: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")

    st.divider()

with tab2:
    st.write("### :material/analytics: Análisis visual")
    
    st.write("#### Tabla dinámica de contrataciones")
    tabla_dinamica_contrataciones(df_altas_filtrado)

    # Gráficas de contrataciones (con filtro)
    st.write("#### Contrataciones por Ejecutivo")
    grafica_contrataciones_por_ejecutivo(df_altas_filtrado)

    st.write("#### Contrataciones por Medio de Reclutamiento")
    grafica_contrataciones_por_medio_reclutamiento(df_altas_filtrado)

    st.write("#### Contrataciones por Mes")
    grafica_contrataciones_mes(df_altas_filtrado)

    st.divider()
    st.write('### Contrataciones por Empresa')
    grafica_contrataciones_por_empresa(df_altas_filtrado)
    st.divider()

with tab3:
    df_vacantes_activas = df_vacantes[~vacantes_excluir] if not df_vacantes.empty else df_vacantes

    st.write("### Detalle de Vacantes")
    grafica_vacantes_por_empresa(df_vacantes_activas)

    st.divider()
    st.write("### Vacantes por Área")
    grafica_vacantes_por_area(df_vacantes_activas)

    st.divider()
    st.write("### Embudo de Vacantes por Fase de Proceso")
    grafica_embudo_fase_proceso(df_vacantes_activas)
    st.divider()

with tab4:
    st.write("### Contrataciones por Redes Pagadas")
    contrataciones_area_redes_pagadas(df_altas_filtrado)

with tab5:
    st.write('### Detalle de Promedio de Días de Cobertura por Plaza y Puesto')
    promedio_plaza_puesto(df_vacantes_cerradas_filtrado)

with tab6:
    st.write("### :material/files: Expedientes de Colaboradores")

    docs_requeridos_ids = (
        df_catalogo_docs[df_catalogo_docs['requerido'] == True]['id'].tolist()
        if not df_catalogo_docs.empty else []
    )
    n_docs_requeridos = len(docs_requeridos_ids)

    colaboradores_ids = (
        df_colaboradores[df_colaboradores['activo'] == True]['id_colaborador'].tolist()
        if not df_colaboradores.empty else []
    )
    n_colaboradores = len(colaboradores_ids)

    if not df_archivos.empty and n_docs_requeridos > 0 and n_colaboradores > 0:
        df_req = df_archivos[
            (df_archivos['id_colaborador'].isin(colaboradores_ids)) &
            (df_archivos['id_documento'].isin(docs_requeridos_ids))
        ].copy()
        docs_ok_por_colab = (
            df_req[df_req['estatus_pdf'] == True]
            .groupby('id_colaborador')['id_documento']
            .nunique()
        )
        n_completos = int((docs_ok_por_colab >= n_docs_requeridos).sum())
    else:
        n_completos = 0

    n_faltantes   = n_colaboradores - n_completos
    pct_completos = (n_completos / n_colaboradores * 100) if n_colaboradores > 0 else 0.0

    col10, col11, col12, col13 = st.columns(4)
    col10.metric(label='Expedientes Totales',     value=n_colaboradores)
    col11.metric(label='Expedientes Completos',   value=n_completos,  delta=f"{pct_completos:.1f}%")
    col12.metric(label='Expedientes Faltantes',   value=n_faltantes,  delta=f"{100 - pct_completos:.1f}%", delta_color="inverse")
    col13.metric(label='% Expedientes Completos', value=f"{pct_completos:.1f}%")

    st.divider()

    if not df_colaboradores.empty and not df_catalogo_docs.empty and not df_archivos.empty:
        df_colab_activos = df_colaboradores[df_colaboradores['activo'] == True].copy()
        df_docs_req      = df_catalogo_docs[df_catalogo_docs['requerido'] == True].copy()

        docs_entregados = (
            df_archivos[
                df_archivos['id_documento'].isin(docs_requeridos_ids) &
                df_archivos['id_colaborador'].isin(colaboradores_ids) &
                (df_archivos['estatus_pdf'] == True)
            ][['id_colaborador', 'id_documento']]
            .drop_duplicates()
        )

        docs_por_colab = docs_entregados.groupby('id_colaborador')['id_documento'].nunique()
        completos_ids  = set(docs_por_colab[docs_por_colab >= n_docs_requeridos].index)
        df_colab_activos['Estatus'] = df_colab_activos['id_colaborador'].apply(
            lambda x: 'COMPLETO' if x in completos_ids else 'INCOMPLETO'
        )

        entregados_set = set(zip(docs_entregados['id_colaborador'], docs_entregados['id_documento']))
        doc_ids        = df_docs_req['id'].tolist()
        doc_nombres    = df_docs_req['nombre_documento'].tolist()

        df_wide = df_colab_activos[[
            'id_colaborador', 'nombre_completo', 'empresa', 'plaza', 'departamento', 'puesto', 'Estatus'
        ]].copy()

        for doc_id, doc_nombre in zip(doc_ids, doc_nombres):
            df_wide[doc_nombre] = df_wide['id_colaborador'].apply(
                lambda cid, did=doc_id: (cid, did) in entregados_set
            )

        df_wide = (
            df_wide
            .drop(columns=['id_colaborador'])
            .sort_values('nombre_completo', ascending=True)
            .reset_index(drop=True)
            .rename(columns={
                'nombre_completo': 'Colaborador',
                'empresa':         'Empresa',
                'plaza':           'Plaza',
                'departamento':    'Departamento',
                'puesto':          'Puesto',
            })
        )

        def _reset_exp_page():
            st.session_state['exp_page'] = 0

        col_busq, col_fest, col_femp = st.columns([3, 1, 2])
        with col_busq:
            busqueda = st.text_input(
                ":material/search: Buscar",
                placeholder="Colaborador o empresa...",
                key="exp_busqueda",
                on_change=_reset_exp_page,
            )
        with col_fest:
            filtro_estatus = st.selectbox(
                "Estatus",
                ["Todos", "COMPLETO", "INCOMPLETO"],
                key="exp_filtro_estatus",
                on_change=_reset_exp_page,
            )
        with col_femp:
            empresas_disp = sorted(df_wide['Empresa'].dropna().unique().tolist())
            filtro_empresa = st.multiselect(
                "Empresa",
                empresas_disp,
                key="exp_filtro_empresa",
                on_change=_reset_exp_page,
            )

        if busqueda.strip():
            termino = busqueda.strip()
            mask = (
                df_wide['Colaborador'].str.contains(termino, case=False, na=False) |
                df_wide['Empresa'].str.contains(termino, case=False, na=False)
            )
            df_wide = df_wide[mask].reset_index(drop=True)
        if filtro_estatus != "Todos":
            df_wide = df_wide[df_wide['Estatus'] == filtro_estatus].reset_index(drop=True)
        if filtro_empresa:
            df_wide = df_wide[df_wide['Empresa'].isin(filtro_empresa)].reset_index(drop=True)

        PAGE_SIZE   = 15
        total_filas = len(df_wide)
        total_pags  = max(1, -(-total_filas // PAGE_SIZE))

        if 'exp_page' not in st.session_state:
            st.session_state['exp_page'] = 0
        st.session_state['exp_page'] = min(st.session_state['exp_page'], total_pags - 1)

        col_prev, col_info, col_next = st.columns([1, 4, 1])
        with col_prev:
            if st.button('← Anterior', key='exp_prev', disabled=st.session_state['exp_page'] == 0):
                st.session_state['exp_page'] -= 1
                st.rerun()
        with col_info:
            inicio = st.session_state['exp_page'] * PAGE_SIZE + 1
            fin    = min(inicio + PAGE_SIZE - 1, total_filas)
            st.caption(f"Mostrando {inicio}–{fin} de {total_filas} colaboradores · Página {st.session_state['exp_page'] + 1} de {total_pags}")
        with col_next:
            if st.button('Siguiente →', key='exp_next', disabled=st.session_state['exp_page'] >= total_pags - 1):
                st.session_state['exp_page'] += 1
                st.rerun()

        start   = st.session_state['exp_page'] * PAGE_SIZE
        df_page = df_wide.iloc[start : start + PAGE_SIZE]

        col_config = {
            doc: st.column_config.CheckboxColumn(doc, disabled=True)
            for doc in doc_nombres
        }

        st.dataframe(
            df_page,
            hide_index=True,
            use_container_width=True,
            column_config=col_config,
        )
    else:
        st.info("No hay datos de expedientes disponibles.")
