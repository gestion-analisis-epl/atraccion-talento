import streamlit as st
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
from datetime import datetime, timedelta
import calendar

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

def calcular_dias_cobertura(row):
    """
    Calcula los días de cobertura según las reglas:
    - Si vacantes_contratados > 0: fecha_cobertura - fecha_solicitud
    - Si vacantes_solicitadas > 0: fecha_hoy - fecha_solicitud
    """
    try:
        fecha_solicitud = pd.to_datetime(row['fecha_solicitud'])
        
        if row['vacantes_contratados'] > 0 and pd.notna(row.get('fecha_cobertura')):
            fecha_cobertura = pd.to_datetime(row['fecha_cobertura'])
            dias = (fecha_cobertura - fecha_solicitud).days
        elif row['vacantes_solicitadas'] > 0:
            fecha_hoy = datetime.now()
            dias = (fecha_hoy - fecha_solicitud).days
        else:
            dias = None
            
        return dias
    except:
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

def filtrar_datos(df, fecha_columna, tipo_filtro, año=None, mes=None, semana=None):
    """Filtra el DataFrame según el tipo de filtro seleccionado"""
    if df.empty:
        return df
    
    df[fecha_columna] = pd.to_datetime(df[fecha_columna])
    
    if tipo_filtro == "Todo el tiempo":
        return df
    elif tipo_filtro == "Por año" and año:
        return df[df[fecha_columna].dt.year == año]
    elif tipo_filtro == "Por mes" and año and mes:
        return df[(df[fecha_columna].dt.year == año) & (df[fecha_columna].dt.month == mes)]
    elif tipo_filtro == "Por semana" and año and semana:
        inicio, fin = obtener_rango_semana(año, semana)
        return df[(df[fecha_columna] >= inicio) & (df[fecha_columna] <= fin)]
    else:
        return df