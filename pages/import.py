import streamlit as st
from datetime import datetime, date
from st_supabase_connection import SupabaseConnection
import pandas as pd
import pytz
import traceback

from utils.auth import require_login
from config.db_utils import (
    insertar_maestra, 
    insertar_vacante, 
    buscar_vacante_por_id_sistema, 
    actualizar_vacante_sistema, 
    actualizar_maestra
)

require_login()

# --- Configuración base ---
conn = st.connection("supabase", type=SupabaseConnection)
MEXICO_TZ = pytz.timezone("America/Mexico_City")

st.write("### Importar datos desde archivo de Enla-c")

# --- Subida del archivo ---
archivo = st.file_uploader("Selecciona un archivo", type=["xlsx", "xls"], key="import_file")
subir_archivo = st.button("📤 Verificar archivo", type="primary")

# --- Mapeos de columnas ---
column_map_vacantes = {
    "fecha_solicitud": "Fecha Solicitud",
    "tipo_solicitud": "Tipo de solicitud",
    "estatus_solicitud": "Estatus De Solicitud",
    "fase_proceso": "Fase del Proceso",
    "fecha_avance": "Fecha de avance del proceso",
    "fecha_autorizacion": "Fecha Autorizada",
    "puesto_vacante": "Puesto solicitado",
    "plaza_vacante": "Plaza",
    "empresa_vacante": "Empresa",
    "funcion_area_vacante": "Función Área",
    "vacantes_solicitadas": "No.Vacantes Solicitadas",
    "vacantes_contratados": "No. Vacantes Contratados",
    "responsable_vacante": "Responsable Del Proceso",
    "comentarios_vacante": "Comentarios Del Seguimiento Del Proceso",
    "tipo_reclutamiento_vacante": "Tipo de Reclutamiento",
    "medio_reclutamiento_vacante": "Medio de Reclutamiento/HeadHunter",
    "id_sistema": "ID",
    "fecha_cobertura": "Fecha Del Seguimiento Del Proceso"
}

# --- Utilidad de fecha ---
def convertir_fecha(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, str):
        try:
            return pd.to_datetime(valor)
        except:
            return None
    return None

# --- Verificar archivo ---
if subir_archivo and archivo is not None:
    try:
        df = pd.read_excel(archivo)
        df.columns = df.columns.astype(str).str.strip()
        st.session_state["archivo_df"] = df
        st.session_state["archivo_ok"] = True
        st.success("Archivo cargado correctamente. Revisa la vista previa y confirma.")
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.code(traceback.format_exc())

elif subir_archivo and archivo is None:
    st.error("Debes seleccionar un archivo.")

# --- Vista previa ---
if st.session_state.get("archivo_ok", False):
    df_preview = st.session_state["archivo_df"]
    st.write("### Vista previa del archivo cargado")
    st.dataframe(df_preview.head(10))
    st.write("Confirma que el archivo es correcto antes de subirlo a la base de datos.")

    if st.button("✅ Confirmar", type="primary", key="confirmar_subida"):
        try:
            df = df_preview.copy()
            df_vacantes = df[[v for v in column_map_vacantes.values() if v in df.columns]].copy()
            df_vacantes = df_vacantes.rename(columns={v: k for k, v in column_map_vacantes.items()})

            for col in ["fecha_solicitud", "fecha_avance", "fecha_autorizacion"]:
                if col in df_vacantes.columns:
                    df_vacantes[col] = df_vacantes[col].apply(convertir_fecha)

            df_vacantes["fecha_importacion"] = datetime.now(MEXICO_TZ)

            registros_exitosos = 0
            registros_actualizados = 0
            registros_nuevos = 0
            registros_fallidos = 0
            errores = []

            progress_bar = st.progress(0)
            status_text = st.empty()
            logs_box = st.empty()

            total_rows = len(df_vacantes)
            logs = []

            for idx, row in df_vacantes.iterrows():
                try:
                    id_sistema_actual = int(row.get("id_sistema")) if pd.notna(row.get("id_sistema")) else None
                    
                    logs.append(f"🔄 Fila {idx + 1}: procesando {row.get('puesto_vacante', '')} (ID: {id_sistema_actual})")
                    
                    maestra_data = {
                        "puesto": str(row.get("puesto_vacante", "")).strip(),
                        "empresa": str(row.get("empresa_vacante", "")).strip(),
                        "plaza": str(row.get("plaza_vacante", "")).strip(),
                        "area": str(row.get("funcion_area_vacante", "")).strip(),
                    }

                    def safe_str(valor):
                        if pd.isna(valor):
                            return None
                        return str(valor).strip() if str(valor).strip() else None
                    
                    vacante_data = {
                        "fecha_solicitud": row.get("fecha_solicitud"),
                        "tipo_solicitud": str(row.get("tipo_solicitud", "")).strip().upper() or None,
                        "estatus_solicitud": str(row.get("estatus_solicitud", "")).strip().upper() or None,
                        "fase_proceso": str(row.get("fase_proceso", "")).strip().upper() or None,
                        "fecha_avance": row.get("fecha_avance"),
                        "fecha_autorizacion": row.get("fecha_autorizacion"),
                        "puesto_vacante": maestra_data["puesto"],
                        "plaza_vacante": maestra_data["plaza"],
                        "empresa_vacante": maestra_data["empresa"],
                        "funcion_area_vacante": maestra_data["area"],
                        "vacantes_solicitadas": max(
                            int(row.get("vacantes_solicitadas", 0)) - int(row.get("vacantes_contratados", 0))
                            if (
                                pd.notna(row.get("vacantes_solicitadas"))
                                and pd.notna(row.get("vacantes_contratados"))
                                and int(row.get("vacantes_contratados", 0)) > 0
                            )
                            else int(row.get("vacantes_solicitadas", 0)) if pd.notna(row.get("vacantes_solicitadas")) else 0,
                            0
                        ),
                        "vacantes_contratadas": int(row.get("vacantes_contratados", 0))
                        if pd.notna(row.get("vacantes_contratados"))
                        else 0,
                        "reponsable_vacante": safe_str(row.get("responsable_vacante")) or "SIN ESPECIFICAR",
                        "comentarios_vacante": safe_str(row.get("comentarios_vacante")),
                        "tipo_reclutamiento_vacante": safe_str(row.get("tipo_reclutamiento_vacante")) or "SIN ESPECIFICAR",
                        "medio_reclutamiento_vacante": safe_str(row.get("medio_reclutamiento_vacante")) or "SIN ESPECIFICAR",
                        "fecha_cobertura": row.get("fecha_cobertura") or None,
                        "id_sistema": id_sistema_actual
                    }

                    # Buscar si ya existe el registro
                    vacante_existente = None
                    if id_sistema_actual:
                        vacante_existente = buscar_vacante_por_id_sistema(conn, id_sistema_actual)
                    
                    if vacante_existente:
                        id_maestra = vacante_existente["id_registro"]
                        id_vacante = vacante_existente["id"]
                        
                        actualizar_maestra(conn, id_maestra, maestra_data)
                        actualizar_vacante_sistema(conn, vacante_data, id_maestra, id_vacante)
                        
                        logs.append(f"🔄 Registro actualizado (ID Sistema: {id_sistema_actual})")
                        registros_actualizados += 1
                        registros_exitosos += 1
                    else:
                        id_maestra = insertar_maestra(conn, "Vacante", maestra_data)
                        if id_maestra is None:
                            raise Exception("No se generó ID de maestra")
                        
                        insertar_vacante(conn, vacante_data, id_maestra)
                        logs.append(f"✅ Registro nuevo insertado (ID Sistema: {id_sistema_actual})")
                        registros_nuevos += 1
                        registros_exitosos += 1

                except Exception as e:
                    registros_fallidos += 1
                    error_msg = f"⚠️ Error en fila {idx + 1}: {e}"
                    logs.append(error_msg)
                    errores.append(error_msg)

                progress = (idx + 1) / total_rows
                progress_bar.progress(progress)
                status_text.text(f"Procesando {idx + 1}/{total_rows}")
                logs_box.write("\n".join(logs[-5:]))

            progress_bar.empty()
            status_text.empty()

            st.success(f"✅ Importación completada: {registros_exitosos} registros procesados.")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📝 Nuevos", registros_nuevos)
            with col2:
                st.metric("🔄 Actualizados", registros_actualizados)
            with col3:
                st.metric("⚠️ Fallidos", registros_fallidos)
            
            if registros_fallidos > 0:
                st.warning(f"⚠️ {registros_fallidos} registros fallaron.")
                with st.expander("Ver errores"):
                    for err in errores[:10]:
                        st.error(err)
                    if len(errores) > 10:
                        st.info(f"... y {len(errores) - 10} más.")

        except Exception as e:
            st.error(f"Error general en la importación: {e}")
            st.code(traceback.format_exc())
