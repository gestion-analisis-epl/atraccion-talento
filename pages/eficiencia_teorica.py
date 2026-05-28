import streamlit as st
from datetime import date, datetime
import pandas as pd
from utils.vars_efiencia import variables_actividades, variables_eficiencia
from st_supabase_connection import SupabaseConnection
from utils.auth import require_login

require_login()

conn = st.connection("supabase", type=SupabaseConnection)

vacantes = (conn.table("vacantes")
                   .select(
                       """
                       id, id_registro, fecha_solicitud, tipo_solicitud, estatus_solicitud, fase_proceso,
                       fecha_avance, fecha_autorizacion, puesto_vacante, plaza_vacante, empresa_vacante,
                       funcion_area_vacante, vacantes_solicitadas, vacantes_contratados, responsable_vacante,
                       comentarios_vacante, tipo_reclutamiento_vacante, medio_reclutamiento_vacante, fecha_cobertura,
                       id_sistema, confidencial
                       """
                   )
                   .neq("fase_proceso", "CONTRATADO")
                   .not_.in_("estatus_solicitud", ["FINALIZADO", "PAUSADO", "CANCELADO", "RECHAZADA"])
                   .not_.is_('fecha_autorizacion', None)
                   .execute()
                   )

vacantes_data = vacantes.data
vacantes_df = pd.DataFrame(vacantes_data)

# Actividades 
revision_requisicion, publicacion_vacante, filtro_candidatos, coordinar_entrevistas, formato_competencias_perfil, entrevistas, seleccion_final, seguimiento, tiempo_total = variables_actividades()
personas_atraccion, horas_diarias, dias_laborales_mes = variables_eficiencia()
vacantes_activas = vacantes_df['vacantes_solicitadas'].astype(int).sum()

st.markdown(f"""
<div class="dash-header">
    <span class="dash-title">Indicador de Eficiencia Teórica</span>
    <span class="dash-badge">Atracción de Talento</span>
</div>
""", unsafe_allow_html=True)

main_container = st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="center", gap="small")

with main_container:
    horas_trabajador = personas_atraccion * horas_diarias * dias_laborales_mes
    horas_trabajador_metrica = st.metric(label="Horas Trabajador", value=f'{horas_trabajador:,} hrs')
    
    capacidad_teorica = horas_trabajador / tiempo_total
    capacidad_teorica_metrica = st.metric(label="Capacidad Teórica", value=f'{capacidad_teorica:.2f}')
    
    eficiencia_teorica = (vacantes_activas / capacidad_teorica) * 100
    eficiencia_teorica_metrica = st.metric(label="Eficiencia Teórica", value=f'{eficiencia_teorica:.2f} %')
    
st.markdown("---")
    
indicador_eficiencia_teorica = {
        "Resultado": [
            ":material/trending_down: Menor a 80%",
            ":material/trending_flat: Entre 80% y 100%",
            ":material/trending_up: Mayor a 100%",
            ":material/arrows_more_up: Mayor a 150%"
        ],
        "Interpretación": [
            ":blue[Capacidad disponible / subutilización]",
            ":green[Operación estable]",
            ":orange[Sobrecarga operativa]",
            ":red[Riesgo de saturación del proceso]"
        ],
    }
    
st.table(indicador_eficiencia_teorica, border="horizontal")