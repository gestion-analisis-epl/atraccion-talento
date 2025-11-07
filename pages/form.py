import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection
from datetime import datetime
from utils.funciones_registro import registrar_alta, registrar_baja, registrar_vacante
from utils.funciones_actualizacion import actualizar_vacante, actualizar_baja
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
    actualizar_vacante(conn)
    
# ======================
# ACTUALIZAR UNA BAJA
# ======================
elif opcion == "Actualizar una baja":
    actualizar_baja(conn)
