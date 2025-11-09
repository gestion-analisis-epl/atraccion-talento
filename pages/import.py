import streamlit as st
from st_supabase_connection import SupabaseConnection
import pandas as pd

from utils.auth import require_login

require_login()

conn = st.connection("supabase", type=SupabaseConnection)

st.write("### Importar datos desde archivo de Excel")

archivo = st.file_uploader("Selecciona un archivo de Excel", type=["xlsx"], key="import_file")
subir_archivo = st.button("📤 Subir archivo a la base de datos", type="primary")
if subir_archivo and archivo is not None:
    try:
        archivo = pd.read_excel(archivo)
        st.dataframe(archivo, hide_index=True)
    except Exception as e:
        st.error(f"Error al leer el archivo de Excel: {e}")

