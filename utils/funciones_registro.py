import streamlit as st
from datetime import datetime, date
import pytz
from config.opciones import (
     PLAZAS, EMPRESAS, AREAS, CANALES_RECLUTAMIENTO, RESPONSABLES_RECLUTAMIENTO, 
     ESTATUS_SOLICITUD, FASE_PROCESO, TIPO_RECLUTAMIENTO
)
from config.db_utils import insertar_maestra, insertar_alta, insertar_baja, insertar_vacante

# Zona horaria de México
MEXICO_TZ = pytz.timezone('America/Mexico_City')

# ======================
# REGISTRAR UNA ALTA
# ======================
def registrar_alta(conn):
    st.write("### Formulario de altas")
    # Campos del formulario
    fecha_alta = st.date_input("Fecha de alta ", value=datetime.now(MEXICO_TZ).date(), key="fecha_alta")
    puesto_alta = st.text_input("Puesto a registrar")
    empresa_alta = st.selectbox("Empresa", EMPRESAS, index=2)    
    plaza_alta = st.selectbox("Plaza", PLAZAS, index=9)
    area_alta = st.selectbox("Función de área", AREAS, index=1)
    contratados_alta = st.number_input("Contrataciones", step=1, value=1)
    medio_reclutamiento_alta = st.selectbox("Medio de reclutamiento", CANALES_RECLUTAMIENTO, index=0)
    responsable_alta = st.selectbox("Ejecutivo de reclutamiento", RESPONSABLES_RECLUTAMIENTO, index=0)
    guardar_alta = st.button("Guardar", key="guardar_alta", type="primary")
    if guardar_alta:
        if not puesto_alta.strip():
            st.error("Debes ingresar un puesto.")
        else:
            try:
                id_maestra = insertar_maestra(conn, "Alta", {
                    "puesto": puesto_alta.strip(),
                    "empresa": empresa_alta,
                    "plaza": plaza_alta,
                    "area": area_alta,
                    })
                insertar_alta(conn, {
                    "fecha_alta": fecha_alta, 
                    "empresa_alta": empresa_alta,
                    "puesto_alta": puesto_alta.strip(),
                    "plaza_alta": plaza_alta,
                    "area_alta": area_alta,
                    "contratados_alta": contratados_alta,
                    "medio_reclutamiento_alta": medio_reclutamiento_alta,
                    "responsable_alta": responsable_alta,}, id_maestra)
                st.success("Alta registrada exitosamente", icon="✅")
            except Exception as e:
                    st.error(f"Error al registrar la alta: {e}")
                    
# ======================
# REGISTRAR UNA BAJA
# ======================              
def registrar_baja(conn):
    st.write("### Formulario de bajas")
    # Campos de Formulario
    puesto_baja = st.text_input("Puesto")
    empresa_baja = st.selectbox("Empresa", EMPRESAS, index=2)
    plaza_baja = st.selectbox("Plaza", PLAZAS, index=9)
    area_baja = st.selectbox("Función de área", AREAS, index=1)
    fecha_ingreso = st.date_input("Fecha de ingreso", value=datetime.now(MEXICO_TZ).date(), key="fecha_ingreso")
    opt_baja = st.selectbox("¿Cuenta con fecha de baja?", ("SI", "NO"))
    fecha_baja = st.date_input("Fecha de baja", value=datetime.now(MEXICO_TZ).date(), key="fecha_baja") if opt_baja == "SI" else None
    tipo_baja = st.selectbox("Tipo de baja", ("INDUCIDA", "VOLUNTARIA", "SIN ESPECIFICAR"))
    motivo_baja = st.text_input("Motivo de baja")
    guardar_baja = st.button("Guardar", key="guardar_baja", type="primary")
    
    if guardar_baja:
        if not puesto_baja.strip():
            st.error("Debes ingresar un puesto")
        else:
            try:
                id_maestra = insertar_maestra(conn, "Baja", {
                    "puesto": puesto_baja.strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U'),
                    "empresa": empresa_baja,
                    "plaza": plaza_baja,
                    "area": area_baja,
                })
                insertar_baja(conn, {
                    "fecha_baja": fecha_baja,
                    "puesto_baja": puesto_baja.strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U'),
                    "empresa_baja": empresa_baja,
                    "plaza_baja": plaza_baja,
                    "area_baja": area_baja,
                    "fecha_ingreso": fecha_ingreso,
                    "tipo_baja": tipo_baja,
                    "motivo_baja": motivo_baja.strip().upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U'),
                }, id_maestra)
                st.success("Baja registrada exitosamente", icon="✅")
            except Exception as e:
                st.error(f"Error al registrar la baja: {e}")
                
# ======================
# REGISTRAR UNA VACANTE
# ======================
def registrar_vacante(conn):
    st.write("### Formulario de vacantes")
    # -- Campos de Vacantes --
    puesto_vacante = st.text_input("Puesto")
    plaza_vacante = st.selectbox("Plaza", PLAZAS, index=9)
    empresa_vacante = st.selectbox("Empresa", EMPRESAS, index=2)
    funcion_area_vacante = st.selectbox("Función de área", AREAS, index=1)
    vacantes_solicitadas = st.number_input("Vacantes solicitadas", step=1, value=1, min_value=0)
    fecha_solicitud = st.date_input("Fecha de solicitud ", value=datetime.now(MEXICO_TZ).date(), key="fecha_solicitud")
    tipo_solicitud = st.selectbox("Tipo de solicitud", ("NUEVO", "REEMPLAZO", "SIN ESPECIFICAR"))
    estatus_solicitud = st.selectbox("Status de solicitud", ESTATUS_SOLICITUD, index=0)
    fase_proceso = st.selectbox("Fase del proceso", FASE_PROCESO, index=0)
    fecha_avance = st.date_input("Fecha de avance del proceso ", value=datetime.now(MEXICO_TZ).date(), key="fecha_avance")
    autorizacion = st.selectbox("¿La vacante fue autorizada?", ("SI", "NO"))
    fecha_autorizacion = st.date_input("Fecha de autorizacion ", value=datetime.now(MEXICO_TZ).date(), key="fecha_autorizacion") if autorizacion == "SI" else date(1900, 1, 1)
    contrataciones = st.selectbox("¿La posición fue ocupada?", ("SI", "NO"))
    if contrataciones == "SI":
        vacantes_contratadas = st.number_input("Vacantes contratadas", step=1, value=1, min_value=0)
        vacantes_solicitadas = vacantes_solicitadas - vacantes_contratadas
        fecha_cobertura = st.date_input("Fecha de cobertura ", value=datetime.now(MEXICO_TZ).date(), key="fecha_cobertura")
        tipo_reclutamiento_vacante = st.selectbox("Tipo de reclutamiento", TIPO_RECLUTAMIENTO, index=0)
        medio_reclutamiento_vacante = st.selectbox("Medio de reclutamiento", CANALES_RECLUTAMIENTO, index=0)
    else:
        vacantes_contratadas = 0
        fecha_cobertura = None
        tipo_reclutamiento_vacante = "SIN ESPECIFICAR"
        medio_reclutamiento_vacante = "SIN ESPECIFICAR"
    responsable_vacante = st.selectbox("Ejecutivo a cargo", RESPONSABLES_RECLUTAMIENTO, index=0)
    comentarios_vacante = st.text_area("Comentarios adicionales")
    guardar_vacante = st.button("Guardar", key="guardar_vacante", type="primary")
    
    if guardar_vacante:
        if not puesto_vacante.strip():
            st.error("Debes ingresar un puesto.")
        else:
            try:
                id_maestra = insertar_maestra(conn, "Vacante", {
                    "puesto": puesto_vacante.strip(),
                    "empresa": empresa_vacante,
                    "plaza": plaza_vacante,
                    "area": funcion_area_vacante,
                })
                insertar_vacante(conn, {
                    "fecha_solicitud": fecha_solicitud,
                    "tipo_solicitud": tipo_solicitud,
                    "estatus_solicitud": estatus_solicitud,
                    "fase_proceso": fase_proceso,
                    "fecha_avance": fecha_avance,
                    "fecha_autorizacion": fecha_autorizacion,
                    "puesto_vacante": puesto_vacante.strip(),
                    "plaza_vacante": plaza_vacante,
                    "empresa_vacante": empresa_vacante,
                    "funcion_area_vacante": funcion_area_vacante,
                    "vacantes_solicitadas": vacantes_solicitadas,
                    "vacantes_contratadas": vacantes_contratadas,
                    "reponsable_vacante": responsable_vacante,
                    "comentarios_vacante": comentarios_vacante,
                    "tipo_reclutamiento_vacante": tipo_reclutamiento_vacante,
                    "medio_reclutamiento_vacante": medio_reclutamiento_vacante,
                    "fecha_cobertura": fecha_cobertura,
                }, id_maestra)
                st.success("Vacante registrada exitosamente", icon="✅")
            except Exception as e:
                st.error(f"Error al registrar la vacante: {e}")
                