import streamlit as st
import pandas as pd
from utils.tabla_interactiva import render_interactive_table


# ─────────────────────────────────────────────────────────────
# Carga de datos
# ─────────────────────────────────────────────────────────────

def cargar_datos_expedientes(conn):
    """Carga las tres tablas de expedientes desde Supabase.

    archivos_expedientes se pagina porque supera el límite de 1 000 filas.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (df_catalogo_docs, df_colaboradores, df_archivos)
    """
    data_catalogo = conn.table("catalogo_documentos").select("*").execute()
    data_colab    = conn.table("colaboradores_activos").select("*").execute()

    rows, offset = [], 0
    while True:
        page = (
            conn.table("archivos_expedientes")
            .select("id_colaborador, id_documento, estatus_pdf")
            .range(offset, offset + 999)
            .execute()
        )
        if not page.data:
            break
        rows.extend(page.data)
        if len(page.data) < 1000:
            break
        offset += 1000

    df_catalogo = pd.DataFrame(data_catalogo.data) if data_catalogo.data else pd.DataFrame()
    df_colab    = pd.DataFrame(data_colab.data)    if data_colab.data    else pd.DataFrame()
    df_archivos = pd.DataFrame(rows)               if rows               else pd.DataFrame()

    return df_catalogo, df_colab, df_archivos


# ─────────────────────────────────────────────────────────────
# Renderizado del tab
# ─────────────────────────────────────────────────────────────

def render_tab_expedientes(df_catalogo_docs, df_colaboradores, df_archivos):
    """Renderiza el contenido completo del tab de Expedientes.

    Se llama dentro de `with tab6:` en dashboard.py.
    Muestra KPIs y la tabla interactiva de colaboradores × documentos.
    """
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

        render_interactive_table(
            df_wide,
            bool_cols  = doc_nombres,
            badge_cols = {'Estatus': {'COMPLETO': 'bc', 'INCOMPLETO': 'bi'}},
            height     = 665,
        )
    else:
        st.info("No hay datos de expedientes disponibles.")
