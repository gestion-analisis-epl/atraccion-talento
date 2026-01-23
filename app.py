import streamlit as st

st.set_page_config(page_title="Atraccion de Talento", layout="wide")

# ======================
# SISTEMA DE AUTENTICACIÓN
# ======================
# Obtener credenciales 
def obtener_usuarios():
    """Obtiene los usuarios y contraseñas desde secrets.toml"""
    try:
        return dict(st.secrets["passwords"])
    except Exception as e:
        st.error(f"Error al cargar credenciales: {e}")
        return {}

def verificar_login(usuario, password):
    """Verifica si las credenciales son correctas"""
    usuarios = obtener_usuarios()
    return usuarios.get(usuario) == password

def mostrar_login():
    """Muestra la pantalla de login"""
    st.title(":material/key: Acceso al Sistema")
    st.markdown("### Atracción de Talento - Especialistas Profesionales de León")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        usuario = st.text_input(":material/person: Usuario", key="login_usuario")
        password = st.text_input(":material/password: Contraseña", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Ingresar", type="primary", use_container_width=True):
                if verificar_login(usuario, password):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.rerun()
                else:
                    st.error(":material/cancel: Usuario o contraseña incorrectos")
        
        with col_btn2:
            if st.button("Limpiar", use_container_width=True):
                st.rerun()

def mostrar_app():
    """Muestra la aplicación principal"""
    st.title("Atracción de Talento")
    
    with st.sidebar:
        st.markdown('<h2 style="text-align: center">Especialistas Profesionales de León</h2>', unsafe_allow_html=True)
        st.sidebar.image("img/grupo-epl.png")
        
        # Mostrar usuario logueado y botón de cerrar sesión
        st.markdown("---")
        st.write(f":material/account_circle: Usuario: **{st.session_state.get('usuario', 'N/A')}**")
        if st.button(":material/logout: Cerrar sesión", use_container_width=True):
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            st.rerun()
    
    # -- SETUP --
    form_page = st.Page(
        page = "pages/form.py",
        title = "Formulario de Atracción de Talento",
        icon = ":material/add_notes:"
    )
    dashboard_page = st.Page(
        page = "pages/dashboard.py",
        title = "Dashboard",
        icon = ":material/analytics:"
    )
    
    show_data_page = st.Page(
        page = "pages/show_data.py",
        title = "Mostrar Datos",
        icon = ":material/database:"
    )
    
    import_data_page = st.Page(
        page="pages/import.py",
        title="Importar Datos",
        icon=":material/upload:"
    )
    
    pg = st.navigation(pages=[form_page, dashboard_page, show_data_page, import_data_page])
    pg.run()

# ======================
# CONTROL DE ACCESO
# ======================
# Inicializar estado de autenticación
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# Mostrar login o app según el estado
if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_app()