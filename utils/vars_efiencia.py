import numpy as np
import pandas as pd

def variables_actividades():
    revision_requisicion = 0.1
    publicacion_vacante = 2
    filtro_candidatos = 2
    coordinar_entrevistas = 3
    formato_competencias_perfil = 0.5
    entrevistas = 4
    seleccion_final = 1
    seguimiento = 0.5
    tiempo_total = revision_requisicion + publicacion_vacante + filtro_candidatos + coordinar_entrevistas + formato_competencias_perfil + entrevistas + seleccion_final + seguimiento
    return revision_requisicion, publicacion_vacante, filtro_candidatos, coordinar_entrevistas, formato_competencias_perfil, entrevistas, seleccion_final, seguimiento, tiempo_total

def variables_eficiencia():
    personas_atraccion = 4
    horas_diarias = 9
    dias_laborales_mes = 22
    return personas_atraccion, horas_diarias, dias_laborales_mes