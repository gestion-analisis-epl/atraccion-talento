import streamlit as st
import bcrypt
from datetime import datetime, timedelta, timezone
from streamlit_cookies_manager import EncryptedCookieManager
from styles.styles import estilo_metricas, estilo_dashboard
from utils.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Atraccion de Talento", layout="wide", page_icon=":material/menu:")

SESSION_DAYS = 30


cookies = EncryptedCookieManager(
    prefix="atraccion_talento_",
    password=st.secrets.cookies_manager.cookies_password,
)

if not cookies.ready():
    st.stop()

# ======================
# SISTEMA DE AUTENTICACIÓN
# ======================
def obtener_usuarios():
    """Obtiene los usuarios y contraseñas desde secrets.toml"""
    try:
        return dict(st.secrets["passwords"])
    except Exception as e:
        logger.error("Error al cargar credenciales: %s", e, exc_info=True)
        st.error("Ocurrió un error inesperado. Por favor recarga la página.")
        return {}

def verificar_login(usuario, password):
    """Verifica credenciales comparando con el hash bcrypt almacenado en secrets."""
    usuarios = obtener_usuarios()
    hash_almacenado = usuarios.get(usuario)
    if not hash_almacenado:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_almacenado.encode("utf-8"))
    except Exception:
        return False


def _crear_sesion_persistente(usuario):
    """Guarda sesión persistente en cookie por SESSION_DAYS días."""
    expira = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    cookies["auth_user"] = usuario
    cookies["auth_exp"] = expira.isoformat()
    cookies.save()


def _restaurar_sesion_desde_cookie():
    """Restaura sesión desde cookie si no ha expirado."""
    if st.session_state.get("logout_solicitado"):
        return False

    usuario = cookies.get("auth_user")
    expira_raw = cookies.get("auth_exp")

    if not usuario or not expira_raw:
        return False

    try:
        expira = datetime.fromisoformat(expira_raw)
    except ValueError:
        _eliminar_sesion_persistente()
        return False

    ahora = datetime.now(timezone.utc)
    if expira.tzinfo is None:
        expira = expira.replace(tzinfo=timezone.utc)

    if ahora >= expira:
        _eliminar_sesion_persistente()
        return False

    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario
    return True


def _eliminar_sesion_persistente():
    """Elimina cookies de sesión persistente."""
    if "auth_user" in cookies:
        del cookies["auth_user"]
    if "auth_exp" in cookies:
        del cookies["auth_exp"]
    cookies.save()

def mostrar_login():
    st.markdown("""
    <style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 32px 28px !important;
        border: none !important;
        border-radius: 14px !important;
        background: rgba(255,255,255,0.04) !important;
        box-shadow: 0 4px 40px rgba(0,0,0,0.25) !important;
    }
    .login-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin: 12px 0 4px 0;
        letter-spacing: -0.01em;
    }
    .login-subtitle {
        font-size: 0.78rem;
        color: rgba(255,255,255,0.4);
        text-align: center;
        margin-bottom: 24px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])

    with col2:
        with st.container(border=False):
            st.image("img/grupo-epl.png", width="stretch")
            st.markdown('<p class="login-title">Atracción de Talento</p>', unsafe_allow_html=True)
            st.markdown('<p class="login-subtitle">Especialistas Profesionales de León</p>', unsafe_allow_html=True)

            usuario = st.text_input(":material/person: Usuario", key="login_usuario")
            password = st.text_input(":material/password: Contraseña", type="password", key="login_password")

            if st.button("Ingresar", type="primary", width="stretch"):
                if verificar_login(usuario, password):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["logout_solicitado"] = False
                    _crear_sesion_persistente(usuario)
                    st.rerun()
                else:
                    st.error(":material/cancel: Usuario o contraseña incorrectos")

NOMBRES_DISPLAY = {
    "atepl": "Atracción de Talento",
    "admin": "Administrador",
    "user": "Equipo de Reclutamiento",
    "atracciontalento": "Atracción de Talento",
}

def mostrar_app():
    usuario        = st.session_state.get("usuario", "")
    nombre_display = NOMBRES_DISPLAY.get(usuario, usuario)
    iniciales      = nombre_display[:2].upper() if nombre_display else "?"

    # Logo fijado arriba del sidebar
    with st.sidebar:
        st.logo("img/grupo-epl.png", size="large")

    form_page = st.Page(
        page="pages/form.py",
        title="Gestión de Registros",
        icon=":material/add_notes:"
    )
    dashboard_page = st.Page(
        page="pages/dashboard.py",
        title="Dashboard",
        icon=":material/analytics:"
    )
    comparativa_anual_page = st.Page(
        page="pages/comparativa_anual.py",
        title="Comparación Anual",
        icon=":material/trending_up:"
    )
    
    eficiencia_teorica_page = st.Page(
        page="pages/eficiencia_teorica.py",
        title="KPIs Atracción de Talento",
        icon=":material/trending_up:"
    )
    
    show_data_page = st.Page(
        page="pages/show_data.py",
        title="Mostrar Datos",
        icon=":material/database:"
    )
    import_data_page = st.Page(
        page="pages/import.py",
        title="Importar Datos",
        icon=":material/upload:"
    )
    chatbot_page = st.Page(
        page="pages/chatbot.py",
        title="Chatbot",
        icon=":material/chat:"
    )

    st.markdown(estilo_metricas() + estilo_dashboard(), unsafe_allow_html=True)

    pg = st.navigation({
        "Análisis": [dashboard_page, comparativa_anual_page, eficiencia_teorica_page],
        "Registros": [form_page, show_data_page, import_data_page],
        "Herramientas": [chatbot_page],
    })

    # Botón y tarjeta de usuario al fondo del sidebar (se renderizan después de los nav links)
    with st.sidebar:
        if st.button(":material/logout: Cerrar sesión", width="stretch"):
            st.session_state["logout_solicitado"] = True
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            _eliminar_sesion_persistente()
            st.rerun()

        st.divider()

        st.markdown(f"""
        <style>
        .user-card {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            margin: 4px 0 0 0;
        }}
        .user-avatar {{
            width: 32px;
            height: 32px;
            min-width: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #14b8a6, #0d9488);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 700;
            color: #000;
            letter-spacing: 0.03em;
        }}
        .user-name {{
            font-size: 0.8rem;
            font-weight: 500;
            color: rgba(255,255,255,0.85);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        </style>
        <div class="user-card">
            <div class="user-avatar">{iniciales}</div>
            <span class="user-name">{nombre_display}</span>
        </div>
        """, unsafe_allow_html=True)

    pg.run()

# ======================
# CONTROL DE ACCESO
# ======================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

if "logout_solicitado" not in st.session_state:
    st.session_state["logout_solicitado"] = False

if not st.session_state["autenticado"]:
    _restaurar_sesion_desde_cookie()

if not st.session_state["autenticado"]:
    mostrar_login()
else:
    mostrar_app()
