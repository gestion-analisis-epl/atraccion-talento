"""
Módulo de autenticación para la aplicación de Atracción de Talento.
Proporciona funciones para validar que el usuario esté autenticado antes de acceder a páginas protegidas.
"""
import streamlit as st


def require_login():
    """
    Verifica si el usuario está autenticado; si no, muestra aviso y detiene la ejecución de la página.
    
    Esta función debe ser llamada al inicio de cada página que requiera autenticación.
    Si el usuario no está autenticado, muestra un mensaje de advertencia y detiene
    la ejecución del script para evitar que se muestren datos sensibles.
    
    Uso:
        from utils.auth import require_login
        require_login()
    """
    if not st.session_state.get("autenticado", False):
        st.warning("🔒 Debes iniciar sesión para acceder a esta página.")
        st.info("Por favor, regresa a la página principal para iniciar sesión.")
        
        # Detener ejecución para evitar mostrar datos sensibles
        st.stop()
