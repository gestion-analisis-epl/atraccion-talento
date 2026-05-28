import pandas as pd
from datetime import datetime, timedelta
import pytz
from config.opciones import TRIMESTRES, MESES_ES

MEXICO_TZ = pytz.timezone('America/Mexico_City')

# Alias para compatibilidad con imports existentes en dashboard.py
meses_es = MESES_ES
trimestres = TRIMESTRES

empresas_map = {
    "CORPORATIVO PUBLICITARIO MAO SA DE CV": "MAO",
    "DRAUBEN SA DE CV": "DRAUBEN",
    "ESPECIALISTAS PROFESIONALES DE LEON SA DE CV": "EPL",
    "F2 CONSULTING GROUP SA DE CV": "F2",
    "FICORMA SA DE CV": "FICORMA",
    "KRONOS AMBIENTAL SAPI DE CV": "KRONOS",
    "MARKETING EN PUBLICIDAD DE QUERETARO SA DE CV": "MKT QRO",
    "MONTAJE SUPERVISION Y CONSTRUCCION SA DE CV": "MSC",
    "LUMINA PANTALLAS DIGITALES SA DE CV": "LUMINA",
    "SERVICIOS DE ANUNCIOS PUBLICITARIOS SA DE CV": "SAP",
    "SICMART SA DE CV": "SICMART",
    "THE BEST MARKETING SA DE CV": "BEST MKT",
    "VINCI GERENCIA ORGANIZACIONAL SA DE CV": "VINCI",
}


def calcular_dias_cobertura(row):
    """Días entre autorización y cobertura; para vacantes abiertas usa la fecha de hoy."""
    try:
        fecha_hoy = datetime.now(MEXICO_TZ).replace(hour=0, minute=0, second=0, microsecond=0)

        if pd.notna(row['fecha_autorizacion']):
            fecha_inicio = pd.to_datetime(row['fecha_autorizacion'])
            if fecha_inicio == pd.Timestamp('1900-01-01'):
                return 1
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
        elif pd.notna(row['fecha_solicitud']):
            fecha_inicio = pd.to_datetime(row['fecha_solicitud'])
            if fecha_inicio.tzinfo is None:
                fecha_inicio = MEXICO_TZ.localize(fecha_inicio)
        else:
            return None

        if row.get('vacantes_contratados', 0) > 0 and pd.notna(row.get('fecha_cobertura')):
            fecha_final = pd.to_datetime(row['fecha_cobertura'])
            if fecha_final.tzinfo is None:
                fecha_final = MEXICO_TZ.localize(fecha_final)
        elif row.get('vacantes_solicitadas', 0) > 0:
            fecha_final = fecha_hoy
        else:
            return None

        return (fecha_final - fecha_inicio).days

    except Exception:
        return None


def obtener_rango_semana(año, semana):
    """Rango lunes-domingo para una semana ISO dada."""
    try:
        inicio = datetime.fromisocalendar(int(año), int(semana), 1)
        return inicio, inicio + timedelta(days=6)
    except Exception as e:
        raise ValueError(f"Semana inválida: {e}") from e


def obtener_rango_trimestre(año, trimestre):
    """Rango de fechas para un trimestre (1–4)."""
    try:
        año = int(año)
        trimestre = int(trimestre)
        if trimestre not in [1, 2, 3, 4]:
            raise ValueError(f"Trimestre debe ser 1–4, se recibió {trimestre}")

        meses_trim = TRIMESTRES[trimestre]['meses']
        inicio = datetime(año, meses_trim[0], 1)
        mes_fin = meses_trim[-1]
        fin = datetime(año, 12, 31) if mes_fin == 12 else datetime(año, mes_fin + 1, 1) - timedelta(days=1)
        return inicio, fin
    except Exception as e:
        raise ValueError(f"Error al calcular rango de trimestre: {e}") from e


def filtrar_datos(df, fecha_columna, tipo_filtro, año=None, mes=None, semana=None, trimestre=None, fecha_inicio=None, fecha_fin=None):
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
    elif tipo_filtro == "Por rango de fechas" and fecha_inicio and fecha_fin:
        return df[
            (df[fecha_columna] >= pd.to_datetime(fecha_inicio)) &
            (df[fecha_columna] <= pd.to_datetime(fecha_fin))
        ]
    return df


def filtrar_por_ejecutivo(df, columna_responsable, ejecutivo):
    """Filtra df por el primer nombre del responsable, normalizando alias."""
    if df.empty:
        return df
    df_temp = df.copy()
    df_temp['primer_nombre'] = df_temp[columna_responsable].str.split().str[0].replace({
        'MARTA': 'HELEN',
        'LETICIA': 'LETY',
    })
    return df_temp[df_temp['primer_nombre'] == ejecutivo]
