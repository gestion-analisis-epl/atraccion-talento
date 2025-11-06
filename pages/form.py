import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
from utils.funciones_registro import registrar_alta, registrar_baja, registrar_vacante
from config.opciones import (
     PLAZAS, EMPRESAS, AREAS, CANALES_RECLUTAMIENTO, RESPONSABLES_RECLUTAMIENTO, 
     ESTATUS_SOLICITUD, FASE_PROCESO, TIPO_RECLUTAMIENTO
)

# Initialize Supabase connection
conn = st.connection("supabase", type=SupabaseConnection)

st.write("## Formulario de Atracción de Talento")
st.write("Este formulario permite registrar, actualizar o eliminar datos de la base de datos de atracción de talento.")
st.write("---")


opcion = st.selectbox(
    "¿Qué desea registrar en la base de datos",
    (
        "Registrar una alta",
        "Registrar una baja",
        "Registrar una vacante",
        "Actualizar una vacante",
        "Actualizar una baja"
    ),
    index=None,
    placeholder="Selecciona una opción"
)

st.write("---")


if opcion == "Registrar una alta":
    registrar_alta(conn)


elif opcion == "Registrar una baja":
    registrar_baja(conn)


elif opcion == "Registrar una vacante":
    registrar_vacante(conn)
    
# ======================
# ACTUALIZAR UNA VACANTE
# ======================
elif opcion == "Actualizar una vacante":
    st.write("### Actualización de vacante existente")
    try:
        response = conn.table("vacantes").select("*").gt('vacantes_solicitadas', 0).execute()
        df = pd.DataFrame(response.data)
        df = df.rename(columns={
            "id": "ID",
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
            "tipo_reclutamiento_vacante": "Tipo de reclutamiento",
            "medio_reclutamiento_vacante": "Medio de reclutamiento",
            "fecha_cobertura": "Fecha de cobertura",
        })
        
        st.write('### Selecciona una fila para editar')
        st.info("👆 Haz clic en cualquier fila de la tabla para seleccionarla")
        
        # Dataframe interactivo con selección
        event = st.dataframe(
            df,
            column_config={"id_registro": None},
            column_order=["Fecha de solicitud", "Puesto", "Plaza", "Empresa"],
            hide_index=True,
            width="stretch",
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Verificar si hay una fila seleccionada
        if event.selection.rows:
            fila_seleccionada = event.selection.rows[0]
            
            # Definir el diálogo modal
            @st.dialog("Editar Vacante", width="large")
            def editar_vacante(registro):
                st.write(f"**Editando: {registro['Empresa']} - {registro['Puesto']} - {registro['Plaza']}**")
                
                # Sección 1: Información de Solicitud
                st.subheader("📋 Información de Solicitud")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fecha_solicitud = st.date_input("Fecha de solicitud", 
                                                   value=pd.to_datetime(registro["Fecha de solicitud"]) if pd.notna(registro["Fecha de solicitud"]) else None)
                    tipo_solicitud_opciones = ["NUEVO", "REEMPLAZO", "SIN ESPECIFICAR"]
                    tipo_solicitud_idx = tipo_solicitud_opciones.index(registro["Tipo de solicitud"]) if pd.notna(registro["Tipo de solicitud"]) and registro["Tipo de solicitud"] in tipo_solicitud_opciones else 0
                    tipo_solicitud = st.selectbox("Tipo de solicitud", options=tipo_solicitud_opciones, index=tipo_solicitud_idx)
                
                with col2:
                    estatus_solicitud_idx = ESTATUS_SOLICITUD.index(registro["Estatus de solicitud"]) if pd.notna(registro["Estatus de solicitud"]) and registro["Estatus de solicitud"] in ESTATUS_SOLICITUD else 0
                    estatus_solicitud = st.selectbox("Estatus de solicitud", options=ESTATUS_SOLICITUD, index=estatus_solicitud_idx)
                    fase_proceso_idx = FASE_PROCESO.index(registro["Fase del proceso"]) if pd.notna(registro["Fase del proceso"]) and registro["Fase del proceso"] in FASE_PROCESO else 0
                    fase_proceso = st.selectbox("Fase del proceso", options=FASE_PROCESO, index=fase_proceso_idx)
                
                with col3:
                    fecha_avance = st.date_input("Fecha del avance", 
                                                value=pd.to_datetime(registro["Fecha del avance"]) if pd.notna(registro["Fecha del avance"]) else None)
                    fecha_autorizacion = st.date_input("Fecha de autorización", 
                                                      value=pd.to_datetime(registro["Fecha de autorización"]) if pd.notna(registro["Fecha de autorización"]) else None)
                
                st.divider()
                
                # Sección 2: Información de la Vacante
                st.subheader("💼 Información de la Vacante")
                col4, col5, col6 = st.columns(3)
                
                with col4:
                    puesto = st.text_input("Puesto", value=registro["Puesto"] if pd.notna(registro["Puesto"]) else "")
                    plaza_idx = PLAZAS.index(registro["Plaza"]) if pd.notna(registro["Plaza"]) and registro["Plaza"] in PLAZAS else 0
                    plaza = st.selectbox("Plaza", options=PLAZAS, index=plaza_idx)
                
                with col5:
                    empresa_idx = EMPRESAS.index(registro["Empresa"]) if pd.notna(registro["Empresa"]) and registro["Empresa"] in EMPRESAS else 0
                    empresa = st.selectbox("Empresa", options=EMPRESAS, index=empresa_idx)
                    funcion_area_idx = AREAS.index(registro["Función de área"]) if pd.notna(registro["Función de área"]) and registro["Función de área"] in AREAS else 0
                    funcion_area = st.selectbox("Función de área", options=AREAS, index=funcion_area_idx)
                
                with col6:
                    vacantes_solicitadas = st.number_input("Vacantes solicitadas", 
                                                          value=int(registro["Vacantes solicitadas"]) if pd.notna(registro["Vacantes solicitadas"]) else 0,
                                                          min_value=0)
                    vacantes_contratados = st.number_input("Contratados", 
                                                          value=int(registro["Contratados"]) if pd.notna(registro["Contratados"]) else 0,
                                                          min_value=0)
                
                st.divider()
                
                # Sección 3: Información de Reclutamiento
                st.subheader("🎯 Información de Reclutamiento")
                col7, col8 = st.columns(2)
                
                with col7:
                    responsable_idx = RESPONSABLES_RECLUTAMIENTO.index(registro["Responsable"]) if pd.notna(registro["Responsable"]) and registro["Responsable"] in RESPONSABLES_RECLUTAMIENTO else 0
                    responsable = st.selectbox("Responsable", options=RESPONSABLES_RECLUTAMIENTO, index=responsable_idx)
                    tipo_reclutamiento_idx = TIPO_RECLUTAMIENTO.index(registro["Tipo de reclutamiento"]) if pd.notna(registro["Tipo de reclutamiento"]) and registro["Tipo de reclutamiento"] in TIPO_RECLUTAMIENTO else 0
                    tipo_reclutamiento = st.selectbox("Tipo de reclutamiento", options=TIPO_RECLUTAMIENTO, index=tipo_reclutamiento_idx)
                
                with col8:
                    medio_reclutamiento_idx = CANALES_RECLUTAMIENTO.index(registro["Medio de reclutamiento"]) if pd.notna(registro["Medio de reclutamiento"]) and registro["Medio de reclutamiento"] in CANALES_RECLUTAMIENTO else 0
                    medio_reclutamiento = st.selectbox("Medio de reclutamiento", options=CANALES_RECLUTAMIENTO, index=medio_reclutamiento_idx)
                    fecha_cobertura = st.date_input("Fecha de cobertura", 
                                                   value=pd.to_datetime(registro["Fecha de cobertura"]) if pd.notna(registro["Fecha de cobertura"]) else None)
                
                comentarios = st.text_area("Comentarios", value=registro["Comentarios"] if pd.notna(registro["Comentarios"]) else "", height=100)
                
                st.divider()
                
                # Botones de acción
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("💾 Guardar cambios", width="stretch", type="primary"):
                        try:
                            payload_vac = {
                                "fecha_solicitud": fecha_solicitud.strftime('%Y-%m-%d') if fecha_solicitud else None,
                                "tipo_solicitud": tipo_solicitud,
                                "estatus_solicitud": estatus_solicitud,
                                "fase_proceso": fase_proceso.upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U"),
                                "fecha_avance": fecha_avance.strftime('%Y-%m-%d') if fecha_avance else None,
                                "fecha_autorizacion": fecha_autorizacion.strftime('%Y-%m-%d') if fecha_autorizacion else None,
                                "puesto_vacante": puesto.strip(),
                                "plaza_vacante": plaza,
                                "empresa_vacante": empresa,
                                "funcion_area_vacante": funcion_area,
                                "vacantes_solicitadas": vacantes_solicitadas,
                                "vacantes_contratados": vacantes_contratados,
                                "responsable_vacante": responsable,
                                "comentarios_vacante": comentarios.upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U"),
                                "tipo_reclutamiento_vacante": tipo_reclutamiento,
                                "medio_reclutamiento_vacante": medio_reclutamiento,
                                "fecha_cobertura": fecha_cobertura.strftime('%Y-%m-%d') if fecha_cobertura else None,
                            }
                            conn.table("vacantes").update(payload_vac).eq("id", registro["ID"]).execute()
                            st.success("✅ Vacante actualizada correctamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")
                
                with col_btn2:
                    if st.button("❌ Cancelar", width="stretch"):
                        st.rerun()
            
            # Mostrar botón para editar solo si hay selección
            st.success(f"✅ Seleccionaste: {df.iloc[fila_seleccionada]['Empresa']} - {df.iloc[fila_seleccionada]['Puesto']}")
            
            if st.button("✏️ Editar registro seleccionado", type="primary"):
                registro_seleccionado = df.iloc[fila_seleccionada]
                editar_vacante(registro_seleccionado)
        else:
            st.warning("⚠️ No has seleccionado ningún registro. Haz clic en una fila de la tabla.")
    
    except Exception as e:
        st.error(f'Error: {e}')

# ======================
# ACTUALIZAR UNA BAJA
# ======================
elif opcion == "Actualizar una baja":
    st.write("### Actualización de baja existente")
    try:
        response = conn.table("bajas").select("*").execute()
        df = pd.DataFrame(response.data)
        df = df.rename(columns={
            "id": "ID",
            "empresa_baja": "Empresa",
            "puesto_baja": "Puesto",
            "plaza_baja": "Plaza",
            "fecha_ingreso": "Fecha de ingreso",
            "fecha_baja": "Fecha de baja",
            "tipo_baja": "Tipo de baja",
            "motivo_baja": "Motivo de la baja",
            "area_baja": "Área",
        })
        st.write('### Datos encontrados en bajas')
        st.info("👆 Haz clic en cualquier fila de la tabla para seleccionarla")
        
        # Dataframe interactivo con selección
        event = st.dataframe(
            df,
            column_config = {
                "id_registro": None},
            hide_index=True,
            width="stretch",
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Definir el diálogo modal
        @st.dialog("Editar baja", width="large")
        def editar_baja(registro):
            st.write(f"**Editando: {registro['Empresa']} - {registro['Puesto']}**")
            
            # Sección 1. Información de Baja
            col1, col2, col3 = st.columns(3)
            
            with col1:
                fecha_ingreso = st.date_input("Fecha de ingreso", value=pd.to_datetime(registro["Fecha de ingreso"]) if pd.notna(registro["Fecha de ingreso"]) else None)
                fecha_baja = st.date_input("Fecha de baja", value=pd.to_datetime(registro["Fecha de baja"]) if pd.notna(registro["Fecha de baja"]) else None)
                
            with col2:
                empresa_baja = st.text_input("Empresa", value=registro["Empresa"] if pd.notna(registro["Empresa"]) else "")
                puesto_baja = st.text_input("Puesto", value=registro["Puesto"] if pd.notna(registro["Puesto"]) else "")
                
            with col3:
                plaza_baja = st.text_input("Plaza", value=registro["Plaza"] if pd.notna(registro["Plaza"]) else "")
                tipo_baja = st.text_input("Tipo de baja", value=registro["Tipo de baja"] if pd.notna(registro["Tipo de baja"]) else "")
            
            motivo_baja = st.text_area("Motivo de la baja", value=registro["Motivo de la baja"] if pd.notna(registro["Motivo de la baja"]) else "")
            
            col5_btn, col6_btn = st.columns(2)
            with col5_btn:
                if st.button("💾 Guardar cambios", width="stretch", type="primary"):
                    try:
                        payload_baja = {
                            "fecha_ingreso": fecha_ingreso.strftime('%Y-%m-%d') if fecha_ingreso else None,
                            "fecha_baja": fecha_baja.strftime('%Y-%m-%d') if fecha_baja else None,
                            "empresa_baja": empresa_baja.strip(),
                            "puesto_baja": puesto_baja.strip(),
                            "plaza_baja": plaza_baja.strip(),
                            "tipo_baja": tipo_baja.strip(),
                            "motivo_baja": motivo_baja.strip().upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U"),
                        }
                        conn.table("bajas").update(payload_baja).eq("id", registro["ID"]).execute()
                        st.success("✅ Baja actualizada correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al guardar: {e}")
                        
            with col6_btn:
                if st.button("❌ Cancelar", width="stretch"):
                    st.rerun()
        
        # Verificar si hay una fila seleccionada
        if event.selection.rows:
            fila_seleccionada = event.selection.rows[0]
            st.success(f"✅ Seleccionaste: {df.iloc[fila_seleccionada]['Empresa']} - {df.iloc[fila_seleccionada]['Puesto']}")
            
            if st.button("✏️ Editar registro seleccionado", type="primary"):
                registro_seleccionado = df.iloc[fila_seleccionada]
                editar_baja(registro_seleccionado)
        else:
            st.warning("⚠️ No has seleccionado ningún registro. Haz clic en una fila de la tabla.")
    
    except Exception as e:
        st.error(f'Error: {e}')