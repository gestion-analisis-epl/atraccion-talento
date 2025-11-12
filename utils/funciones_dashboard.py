import streamlit as st
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta
import calendar
import pytz

empresas_map = {
    "CORPORATIVO PUBLICITARIO MAO SA DE CV": 'MAO',
    "DRAUBEN SA DE CV": 'DRAUBEN',
    "ESPECIALISTAS PROFESIONALES DE LEON SA DE CV": 'EPL',
    "F2 CONSULTING GROUP SA DE CV": 'F2',
    "FICORMA SA DE CV": 'FICORMA',
    "KRONOS AMBIENTAL SAPI DE CV": 'KRONOS',
    "MARKETING EN PUBLICIDAD DE QUERETARO SA DE CV": 'MKT QRO',
    "MONTAJE SUPERVISION Y CONSTRUCCION SA DE CV": 'MSC',
    "LUMINA PANTALLAS DIGITALES SA DE CV": 'LUMINA',
    "SERVICIOS DE ANUNCIOS PUBLICITARIOS SA DE CV": 'SAP',
    "SICMART SA DE CV": 'SICMART',
    "THE BEST MARKETING SA DE CV": 'BEST MKT',
    "VINCI GERENCIA ORGANIZACIONAL SA DE CV": 'VINCI'
}

meses_es = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

trimestres = {
    1: {'nombre': 'T1 (Enero-Marzo)', 'meses': [1, 2, 3]},
    2: {'nombre': 'T2 (Abril-Junio)', 'meses': [4, 5, 6]},
    3: {'nombre': 'T3 (Julio-Septiembre)', 'meses': [7, 8, 9]},
    4: {'nombre': 'T4 (Octubre-Diciembre)', 'meses': [10, 11, 12]}
}

# Zona horaria de México
MEXICO_TZ = pytz.timezone('America/Mexico_City')

def calcular_dias_cobertura(row):
    """
    Calcula los días de cobertura actualizados en tiempo real:
    - Para vacantes DISPONIBLES (vacantes_solicitadas > 0): fecha_actual - fecha_autorización (o fecha_solicitud si no hay autorización)
    - Para vacantes CERRADAS (vacantes_contratados > 0): fecha_cobertura - fecha_autorización (o fecha_solicitud si no hay autorización)
    
    Esto asegura que las vacantes disponibles siempre muestren días actualizados.
    """
    try:
        # Obtener fecha actual en zona horaria de México
        fecha_hoy = datetime.now(MEXICO_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Determinar la fecha de inicio (priorizar fecha_autorización sobre fecha_solicitud)
        if pd.notna(row['fecha_autorizacion']):
            fecha_inicio = pd.to_datetime(row['fecha_autorizacion'])
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
        elif pd.notna(row['fecha_solicitud']):
            fecha_inicio = pd.to_datetime(row['fecha_solicitud'])
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
        else:
            return None
        
        # Determinar la fecha final según el estado de la vacante
        # Si tiene contratados y fecha de cobertura, es una vacante cerrada
        if row.get('vacantes_contratados', 0) > 0 and pd.notna(row.get('fecha_cobertura')):
            fecha_final = pd.to_datetime(row['fecha_cobertura'])
            if fecha_final.tzinfo is None:
                fecha_final = MEXICO_TZ.localize(fecha_final)
        # Si tiene vacantes solicitadas, es una vacante disponible (usar fecha actual)
        elif row.get('vacantes_solicitadas', 0) > 0:
            fecha_final = fecha_hoy
        else:
            return None
        
        # Calcular días
        dias = (fecha_final - fecha_inicio).days
        return dias
        
    except Exception as e:
        return None

def obtener_rango_semana(año, semana):
    """Obtiene el rango de fechas (lunes a domingo) para una semana ISO dada.

    Usa el calendario ISO (semana ISO) mediante datetime.fromisocalendar, de modo que
    la semana 1 es la que contiene el 4 de enero y los días van de lunes(1) a domingo(7).

    Parámetros:
    - año: int o convertible a int (el año ISO)
    - semana: int o convertible a int (número de semana ISO)

    Retorna una tupla (inicio, fin) como objetos datetime (inicio = lunes, fin = domingo).
    Levanta ValueError si la semana no es válida para ese año.
    """
    try:
        año = int(año)
        semana = int(semana)
        # datetime.fromisocalendar devuelve la fecha correspondiente al día especificado
        # usando el calendario ISO: (año, semana_iso, weekday) donde weekday: 1=Mon .. 7=Sun
        inicio = datetime.fromisocalendar(año, semana, 1)
        fin = inicio + timedelta(days=6)
        return inicio, fin
    except Exception as e:
        # Dejar que el caller maneje el error más arriba (muestra de info o logging).
        raise ValueError(f"Semana inválida o error al calcular rango ISO: {e}") from e

def obtener_rango_trimestre(año, trimestre):
    """Obtiene el rango de fechas (inicio a fin) para un trimestre dado.
    
    Parámetros:
    - año: int o convertible a int (el año)
    - trimestre: int (1, 2, 3 o 4)
    
    Retorna una tupla (inicio, fin) como objetos datetime.
    """
    try:
        año = int(año)
        trimestre = int(trimestre)
        
        if trimestre not in [1, 2, 3, 4]:
            raise ValueError(f"Trimestre debe ser 1, 2, 3 o 4. Se recibió: {trimestre}")
        
        meses_trimestre = trimestres[trimestre]['meses']
        mes_inicio = meses_trimestre[0]
        mes_fin = meses_trimestre[-1]
        
        # Primer día del primer mes del trimestre
        inicio = datetime(año, mes_inicio, 1)
        
        # Último día del último mes del trimestre
        if mes_fin == 12:
            fin = datetime(año, 12, 31)
        else:
            # Último día del mes = primer día del siguiente mes - 1 día
            siguiente_mes = datetime(año, mes_fin + 1, 1)
            fin = siguiente_mes - timedelta(days=1)
        
        return inicio, fin
    except Exception as e:
        raise ValueError(f"Error al calcular rango de trimestre: {e}") from e

def filtrar_datos(df, fecha_columna, tipo_filtro, año=None, mes=None, semana=None, trimestre=None):
    """Filtra el DataFrame según el tipo de filtro seleccionado"""
    if df.empty:
        return df
    
    df[fecha_columna] = pd.to_datetime(df[fecha_columna])
    
    if tipo_filtro == "Todo el tiempo":
        return df
    elif tipo_filtro == "Por año" and año:
        return df[df[fecha_columna].dt.year == año]
    elif tipo_filtro == "Por trimestre" and año and trimestre:
        inicio, fin = obtener_rango_trimestre(año, trimestre)
        return df[(df[fecha_columna] >= inicio) & (df[fecha_columna] <= fin)]
    elif tipo_filtro == "Por mes" and año and mes:
        return df[(df[fecha_columna].dt.year == año) & (df[fecha_columna].dt.month == mes)]
    elif tipo_filtro == "Por semana" and año and semana:
        inicio, fin = obtener_rango_semana(año, semana)
        return df[(df[fecha_columna] >= inicio) & (df[fecha_columna] <= fin)]
    else:
        return df