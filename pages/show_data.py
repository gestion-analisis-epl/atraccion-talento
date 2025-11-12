import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd
import datetime as dt
import pytz
from utils.auth import require_login

# Requerir autenticación antes de mostrar cualquier contenido
require_login()

# Zona horaria de México
MEXICO_TZ = pytz.timezone('America/Mexico_City')

conn = st.connection("supabase", type=SupabaseConnection)
consulta = st.selectbox("¿Qué deseas consulta?", ("Altas", "Bajas", "Vacantes", "Todos los registros"), index=None, placeholder="Selecciona una opción", key="consulta")
st.write("---")

# ======================
# CONSULTAR UNA ALTA
# ======================
if consulta == "Altas":
    response =conn.table("altas").select("*").execute()
    st.write("## Datos encontrados en Altas")
    df_altas = pd.DataFrame(response.data)
    columns_names = {
        'id': 'ID',
        'id_registro': 'ID General',
        'fecha_alta': 'Fecha de alta',
        'empresa_alta': 'Empresa',
        'puesto_alta': 'Puesto',
        'plaza_alta': 'Plaza',
        'area_alta': 'Función de área',
        'contratados_alta': 'Contratados',
        'medio_reclutamiento_alta': 'Medio de reclutamiento',
        'responsable_alta': 'Responsable'
    }
    df_altas = df_altas.rename(columns=columns_names)
    df_altas = df_altas.sort_values(by='ID', ascending=True)
    st.dataframe(df_altas, hide_index=True, column_order=["ID", "Fecha de alta", "Empresa", "Puesto", "Plaza",
                                                          "Función de área", "Contratados", "Medio de reclutamiento", "Responsable"])

# ======================
# CONSULTAR UNA BAJA
# ======================
elif consulta == "Bajas":
    response = conn.table("bajas").select("*").execute()
    st.write("## Datos encontrados en Bajas")
    df_bajas = pd.DataFrame(response.data)
    df_bajas = df_bajas.rename(columns={
        "id": "ID", 
        "empresa_baja": "Empresa",
        "puesto_baja": "Puesto",
        "plaza_baja": "Plaza",
        "fecha_ingreso": "Fecha de ingreso",
        "fecha_baja": "Fecha de baja", 
        "tipo_baja": "Tipo de baja",
        "motivo_baja": "Motivo de la baja"
    })
    df_bajas = df_bajas.sort_values(by='ID', ascending=True)
    st.dataframe(df_bajas, hide_index=True, column_order=["ID", "Empresa", "Puesto", "Plaza", "Fecha de ingreso","Fecha de baja", "Tipo de baja", "Motivo de la baja"])

# ======================
# CONSULTAR VACANTES
# ======================
elif consulta == "Vacantes":
    response =conn.table("vacantes").select("*").execute()
    st.write("## Datos encontrados en Vacantes")
    df_vacantes = pd.DataFrame(response.data)
    
    # Convertir fechas a datetime con zona horaria de México
    df_vacantes['fecha_solicitud'] = pd.to_datetime(df_vacantes['fecha_solicitud'], errors='coerce')
    df_vacantes['fecha_autorizacion'] = pd.to_datetime(df_vacantes['fecha_autorizacion'], errors='coerce')
    df_vacantes['fecha_cobertura'] = pd.to_datetime(df_vacantes['fecha_cobertura'], errors='coerce')
    
    # Calcular días de cobertura
    # Si existe fecha_autorización: fecha_cobertura - fecha_autorización
    # Si no existe fecha_autorización: fecha_cobertura - fecha_solicitud
    # Si no hay fecha_cobertura, usar fecha_hoy (México)
    def calcular_dias_cobertura(row):
        # Obtener fecha actual en zona horaria de México
        fecha_hoy = dt.datetime.now(MEXICO_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Determinar la fecha de referencia final (cobertura o hoy)
        if pd.notna(row['fecha_cobertura']):
            fecha_final = row['fecha_cobertura']
            if fecha_final.tzinfo is None:
                fecha_final = MEXICO_TZ.localize(fecha_final)
        else:
            fecha_final = fecha_hoy
        
        # Determinar la fecha de inicio (autorización o solicitud)
        if pd.notna(row['fecha_autorizacion']):
            fecha_inicio = row['fecha_autorizacion']
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
            return (fecha_final - fecha_inicio).days
        elif pd.notna(row['fecha_solicitud']):
            fecha_inicio = row['fecha_solicitud']
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
            return (fecha_final - fecha_inicio).days
        else:
            return None
    
    df_vacantes['dias_cobertura'] = df_vacantes.apply(calcular_dias_cobertura, axis=1)
    
    columns_name = {
        "id": "ID de Origen",
        "id_sistema": "ID del Sistema",
        "id_registro": "ID General",
        "fecha_solicitud": "Fecha de solicitud",
        "tipo_solicitud": "Tipo de solicitud",
        "estatus_solicitud": "Estatus de solicitud",
        "fase_proceso": "Fase del proceso",
        "fecha_avance": "Fecha del avance",
        "fecha_autorizacion": "Fecha de autorización",
        "puesto_vacante": "Puesto",
        "plaza_vacante": "Plaza",
        "empresa_vacante": "Empresa",
        "funcion_area_vacante": "Función de área",
        "vacantes_solicitadas": "Vacantes solicitadas",
        "vacantes_contratados": "Contratados",
        "responsable_vacante": "Responsable",
        "comentarios_vacante": "Comentarios",
        "tipo_reclutamiento": "Tipo de reclutamiento",
        "medio_reclutamiento_vacante": "Medio de reclutamiento",
        "fecha_cobertura": "Fecha de cobertura",
        "dias_cobertura": "Días de cobertura"
    }
    df_vacantes = df_vacantes.rename(columns=columns_name)
    confidencial = df_vacantes['confidencial'] != 'SI'
    df_vacantes = df_vacantes[confidencial]
    df_vacantes = df_vacantes.sort_values(by='ID del Sistema', ascending=False)
    st.dataframe(df_vacantes, hide_index=True, column_order=["ID del Sistema", "Fecha de solicitud", "Tipo de solicitud", "Estatus de solicitud",
                                                             "Fase del proceso", "Fecha del avance", "Fecha de autorización",
                                                             "Puesto", "Plaza", "Empresa", "Función de área", "Vacantes solicitadas",
                                                             "Contratados", "Responsable", "Comentarios", "Tipo de reclutamiento",
                                                             "Medio de reclutamiento", "Fecha de cobertura", "Días de cobertura"])

# ==============================
# CONSULTAR TODOS LOS REGISTROS
# ==============================    
elif consulta == "Todos los registros":
    response =conn.table("registros_rh").select("*").execute()
    st.write("## Datos encontrados en Registros RH")
    df_registros_rh = pd.DataFrame(response.data)
    columns_name = {
        "id": "ID",
        "tipo_registro": "Tipo de registro",
        "fecha_creacion": "Fecha de creación del registro",
        "puesto": "Puesto",
        "empresa": "Empresa",
        "plaza": "Plaza",
        "area": "Función de área"
    }
    df_registros_rh = df_registros_rh.rename(columns=columns_name)
    st.dataframe(df_registros_rh, hide_index=True, column_order=["ID", "Tipo de registro", "Puesto", "Empresa",
                                                                 "Plaza", "Función de área"] )
    
else:
    st.info("No se encontraron registros.")
