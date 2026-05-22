import streamlit as st
import requests
import json
import re

# Configuración
N8N_WEBHOOK_URL = st.secrets.n8n_webhook.url
MAX_HISTORY = 10

st.markdown("""
<div class="dash-header">
    <span class="dash-title">Chatbot de Recursos Humanos</span>
</div>
""", unsafe_allow_html=True)

st.caption("Escribe tu consulta de forma clara y específica. Indica si la información corresponde a altas, bajas o vacantes. Si necesitas datos de un período determinado, incluye las fechas en tu pregunta.")

# Inicializar historial
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "chart" in msg and msg["chart"]:
            st.plotly_chart(msg["chart"], use_container_width=True)

# Función para limpiar y extraer JSON de la respuesta
def extract_json_payload(text):
    """Extrae y parsea el JSON incluso si viene envuelto en markdown o strings."""
    try:
        # 1. Intentar cargar directamente si ya es un dict
        if isinstance(text, dict):
            return text
        
        # 2. Si es una lista de n8n, tomar el primer elemento
        if isinstance(text, list) and len(text) > 0:
            return extract_json_payload(text[0])

        # 3. Limpiar bloques de código markdown (```json ... ```)
        if isinstance(text, str):
            clean_text = re.sub(r'```json\s*|\s*```', '', text).strip()
            # Buscar el primer '{' y el último '}' por si hay texto basura alrededor
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                clean_text = clean_text[start_idx:end_idx+1]
            return json.loads(clean_text)
            
    except Exception as e:
        print(f"Error parseando JSON: {e}")
    return None

# Input del usuario
if prompt := st.chat_input("Escribe tu pregunta (ej: 'Grafica las vacantes por área')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando base de datos..."):
            try:
                # Petición a n8n
                history = st.session_state.messages[-MAX_HISTORY:]
                resp = requests.post(N8N_WEBHOOK_URL, json={"message": prompt, "history": history}, timeout=60)
                resp.raise_for_status()
                raw_data = resp.json()

                # Procesar la respuesta con nuestra función robusta
                # n8n suele enviar la respuesta del Agente en un campo llamado 'output'
                data = extract_json_payload(raw_data)
                
                # Si el payload estaba anidado dentro de 'output' como un string (común en Agentes de n8n)
                if data and "output" in data and isinstance(data["output"], str) and "{" in data["output"]:
                    nested_data = extract_json_payload(data["output"])
                    if nested_data:
                        data = nested_data

                # Extraer Texto y Gráfica
                if data:
                    answer = data.get("output", "He procesado tu solicitud.")
                    chart_data = data.get("chart")
                else:
                    # Si no pudimos parsear JSON, mostrar la respuesta cruda de n8n
                    answer = raw_data[0].get("output") if isinstance(raw_data, list) else str(raw_data)
                    chart_data = None

                # Mostrar resultados
                st.write(answer)
                
                new_msg = {"role": "assistant", "content": answer}
                
                if chart_data:
                    try:
                        st.plotly_chart(chart_data, use_container_width=True)
                        new_msg["chart"] = chart_data
                    except Exception as chart_err:
                        st.warning("Se recibió una gráfica pero el formato no es compatible con Plotly.")
                
                st.session_state.messages.append(new_msg)

            except requests.exceptions.Timeout:
                st.error("La base de datos tardó demasiado en responder. Intenta con una consulta más específica.")
            except Exception as e:
                st.error(f"Hubo un problema al procesar la respuesta: {e}")