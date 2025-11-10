from datetime import datetime, date
from typing import Any, Dict
import pytz

# Zona horaria de México
MEXICO_TZ = pytz.timezone('America/Mexico_City')

# ------------------ Función maestra ------------------
def insertar_maestra(conn, tipo_registro: str, data: Dict[str, Any]) -> int:
    """
    Inserta un registro en la tabla maestra 'registros_rh' y devuelve el id.
    """
    if tipo_registro not in {"Alta", "Baja", "Vacante"}:
        raise ValueError(f"tipo_registro inválido: {tipo_registro}. Debe ser 'Alta', 'Baja' o 'Vacante'.")
    
    payload = {
        "tipo_registro": tipo_registro.strip().capitalize(),
        "fecha_creacion": datetime.now(MEXICO_TZ).isoformat(),
        "puesto": str(data.get("puesto", "")).strip().upper(),
        "empresa": str(data.get("empresa", "")).strip(),
        "plaza": str(data.get("plaza", "")).strip(),
        "area": str(data.get("area", "")).strip(),
    }
    
    response = conn.table("registros_rh").insert(payload).execute()
    return response.data[0]["id"]

# ------------------ Funciones hijas ------------------
def insertar_alta(conn, data: Dict[str, Any], id_registro: int):
    if not data.get("puesto_alta"):
        raise ValueError("El campo 'puesto_alta' es obligatorio.")
    
    payload = {
        "id_registro": id_registro,
        "fecha_alta": data["fecha_alta"].isoformat() if isinstance(data["fecha_alta"], date) else data["fecha_alta"],
        "empresa_alta": data["empresa_alta"],
        "puesto_alta": str(data["puesto_alta"]).strip().upper(),
        "plaza_alta": data["plaza_alta"],
        "area_alta": data["area_alta"],
        "contratados_alta": str(data["contratados_alta"]),
        "medio_reclutamiento_alta": data["medio_reclutamiento_alta"],
        "responsable_alta": data["responsable_alta"],
    }
    return conn.table("altas").insert(payload).execute()


def insertar_baja(conn, data: Dict[str, Any], id_registro: int):
    if not data.get("puesto_baja"):
        raise ValueError("El campo 'puesto_baja' es obligatorio.")
    
    payload = {
        "id_registro": id_registro,
        "fecha_baja": data["fecha_baja"].isoformat() if data["fecha_baja"] else None,
        "puesto_baja": str(data["puesto_baja"]).strip().upper(),
        "empresa_baja": data["empresa_baja"],
        "plaza_baja": data["plaza_baja"],
        "area_baja": data["area_baja"],
        "fecha_ingreso": data["fecha_ingreso"].isoformat() if isinstance(data["fecha_ingreso"], date) else data["fecha_ingreso"],
        "tipo_baja": data["tipo_baja"],
        "motivo_baja": str(data["motivo_baja"]).strip(),
    }
    return conn.table("bajas").insert(payload).execute()


def insertar_vacante(conn, data: Dict[str, Any], id_registro: int):
    if not data.get("puesto_vacante"):
        raise ValueError("El campo 'puesto_vacante' es obligatorio.")
    
    payload = {
        "id_registro": id_registro,
        "fecha_solicitud": data["fecha_solicitud"].isoformat(),
        "tipo_solicitud": data["tipo_solicitud"],
        "estatus_solicitud": data["estatus_solicitud"],
        "fase_proceso": data["fase_proceso"],
        "fecha_avance": data["fecha_avance"].isoformat(),
        "fecha_autorizacion": data["fecha_autorizacion"].isoformat() if data["fecha_autorizacion"] else None,
        "puesto_vacante": str(data["puesto_vacante"]).strip().upper(),
        "plaza_vacante": data["plaza_vacante"],
        "empresa_vacante": data["empresa_vacante"],
        "funcion_area_vacante": data["funcion_area_vacante"],
        "vacantes_solicitadas": data["vacantes_solicitadas"],
        "vacantes_contratados": data["vacantes_contratadas"],
        "responsable_vacante": data["reponsable_vacante"],
        "comentarios_vacante": data["comentarios_vacante"].upper(),
        "tipo_reclutamiento_vacante": data["tipo_reclutamiento_vacante"],
        "medio_reclutamiento_vacante": data["medio_reclutamiento_vacante"],
        "fecha_cobertura": data["fecha_cobertura"].isoformat() if data["fecha_cobertura"] else None,
    }
    return conn.table("vacantes").insert(payload).execute()
