# 🎯 Sistema de Atracción de Talento - Grupo EPL

Sistema integral de gestión de reclutamiento y selección de personal desarrollado para Especialistas Profesionales de León (Grupo EPL). Permite el registro, seguimiento y análisis de vacantes, contrataciones y bajas de personal.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Supabase](https://img.shields.io/badge/Supabase-181818?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Módulos del Sistema](#-módulos-del-sistema)
- [Base de Datos](#-base-de-datos)
- [Tecnologías](#-tecnologías)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

## ✨ Características

### 🔐 Autenticación y Seguridad
- Sistema de login con credenciales encriptadas
- Gestión de sesiones de usuario
- Protección de rutas y acceso restringido

### 📊 Dashboard Analítico
- **Métricas en tiempo real**:
  - Total de contratados
  - Bajas registradas
  - Vacantes disponibles
  - Días promedio de cobertura (actualizados dinámicamente)
  
- **Filtros avanzados**:
  - Todo el tiempo
  - Por año
  - Por trimestre (T1-T4)
  - Por mes
  - Por semana

- **Análisis por categoría**:
  - Vacantes disponibles vs finalizadas
  - Áreas administrativas vs operativas
  - Detalle de contrataciones y vacantes

- **Visualizaciones interactivas**:
  - Contrataciones por ejecutivo
  - Contrataciones por medio de reclutamiento
  - Distribución de vacantes por empresa
  - Análisis por función de área

### 📝 Gestión de Registros
- **Altas**: Registro de nuevas contrataciones
- **Bajas**: Gestión de salidas de personal
- **Vacantes**: Control de posiciones abiertas y su seguimiento

### 🔄 Importación Masiva
- Carga de datos desde archivos Excel
- Validación automática de datos
- Actualización inteligente (insert/update automático)
- Filtros de calidad de datos:
  - Validación de fechas de autorización (año 2000+)
  - Asignación condicional de fecha de cobertura
- Reporte detallado de importación

### 🔍 Consulta de Datos
- Visualización de registros con filtros
- Cálculo dinámico de días de cobertura
- Exportación de datos en formato tabular

### ✏️ Actualización de Registros
- Modificación de registros existentes
- Historial de cambios
- Validación de datos en tiempo real

## 📁 Estructura del Proyecto

```
atraccion-talento/
│
├── app.py                          # Aplicación principal con autenticación
├── requirements.txt                # Dependencias del proyecto
├── .gitignore                     # Archivos ignorados por Git
│
├── .streamlit/                    # Configuración de Streamlit
│   └── secrets.toml              # Credenciales (NO incluir en Git)
│
├── config/                        # Configuraciones del sistema
│   ├── db_utils.py               # Funciones de base de datos (CRUD)
│   └── opciones.py               # Catálogos y opciones del sistema
│
├── pages/                         # Páginas de la aplicación
│   ├── dashboard.py              # Dashboard analítico principal
│   ├── form.py                   # Formularios de registro
│   ├── import.py                 # Importación masiva desde Excel
│   └── show_data.py              # Consulta y visualización de datos
│
├── utils/                         # Utilidades y funciones auxiliares
│   ├── auth.py                   # Funciones de autenticación
│   ├── funciones_actualizacion.py # Lógica de actualización de registros
│   ├── funciones_dashboard.py    # Cálculos y filtros del dashboard
│   ├── funciones_registro.py     # Lógica de registro de datos
│   └── graficas_dashboard.py     # Generación de gráficas
│
├── static/                        # Archivos estáticos
│   ├── Fira_Code/                # Fuente tipográfica
│   └── Styrene_B_Family/         # Fuente tipográfica
│
└── img/                           # Imágenes y logos
```

## 🔧 Requisitos Previos

- Python 3.8 o superior
- Cuenta de Supabase (base de datos)
- Navegador web moderno

## 🚀 Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/gestion-analisis-epl/atraccion-talento.git
cd atraccion-talento
```

2. **Crear entorno virtual** (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuración

### 1. Configuración de Supabase

Crear el archivo `.streamlit/secrets.toml`:

```toml
# Conexión a Supabase
[connections.supabase]
url = "tu_supabase_url"
key = "tu_supabase_key"

# Credenciales de usuarios
[passwords]
usuario1 = "contraseña_hasheada"
usuario2 = "contraseña_hasheada"
```

### 2. Estructura de Base de Datos

El sistema utiliza las siguientes tablas en Supabase:

#### Tabla: `registros_rh` (Maestra)
- `id` (int, PK)
- `tipo_registro` (text)
- `fecha_creacion` (timestamp)
- `puesto` (text)
- `empresa` (text)
- `plaza` (text)
- `area` (text)

#### Tabla: `altas`
- `id` (int, PK)
- `id_registro` (int, FK)
- `fecha_alta` (date)
- `empresa_alta` (text)
- `puesto_alta` (text)
- `plaza_alta` (text)
- `area_alta` (text)
- `contratados_alta` (int)
- `medio_reclutamiento_alta` (text)
- `responsable_alta` (text)

#### Tabla: `bajas`
- `id` (int, PK)
- `id_registro` (int, FK)
- `fecha_baja` (date)
- `puesto_baja` (text)
- `empresa_baja` (text)
- `plaza_baja` (text)
- `area_baja` (text)
- `fecha_ingreso` (date)
- `tipo_baja` (text)
- `motivo_baja` (text)

#### Tabla: `vacantes`
- `id` (int, PK)
- `id_registro` (int, FK)
- `id_sistema` (int, único)
- `fecha_solicitud` (date)
- `tipo_solicitud` (text)
- `estatus_solicitud` (text)
- `fase_proceso` (text)
- `fecha_avance` (date)
- `fecha_autorizacion` (date)
- `puesto_vacante` (text)
- `plaza_vacante` (text)
- `empresa_vacante` (text)
- `funcion_area_vacante` (text)
- `vacantes_solicitadas` (int)
- `vacantes_contratados` (int)
- `responsable_vacante` (text)
- `comentarios_vacante` (text)
- `tipo_reclutamiento_vacante` (text)
- `medio_reclutamiento_vacante` (text)
- `fecha_cobertura` (date)
- `dias_cobertura` (int)

### 3. Variables de Entorno

El sistema utiliza la zona horaria `America/Mexico_City` para todos los cálculos de fechas y tiempos.

## 💻 Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en `http://localhost:8501`

### Flujo de Trabajo

1. **Login**: Ingresar con credenciales autorizadas
2. **Dashboard**: Visualizar métricas y análisis
3. **Formularios**: Registrar nuevas altas, bajas o vacantes
4. **Importar**: Cargar datos masivos desde Excel
5. **Consultar**: Revisar registros existentes
6. **Actualizar**: Modificar información según sea necesario

## 🔨 Módulos del Sistema

### 📊 Dashboard (`pages/dashboard.py`)
- Métricas principales de reclutamiento
- Análisis de días de cobertura (actualizados en tiempo real)
- Gráficas interactivas por ejecutivo, medio y empresa
- Filtros temporales avanzados

### 📝 Formularios (`pages/form.py`)
- Registro de Altas
- Registro de Bajas
- Registro de Vacantes
- Validación de datos en tiempo real

### 📤 Importación (`pages/import.py`)
- Carga masiva desde Excel
- Mapeo automático de columnas
- Validación de fechas y datos
- Actualización inteligente (insert/update)
- Reporte de resultados

### 🔍 Consulta (`pages/show_data.py`)
- Visualización de todos los registros
- Cálculo dinámico de días de cobertura
- Filtros por tipo de registro

### ✏️ Actualización (`utils/funciones_actualizacion.py`)
- Modificación de registros existentes
- Validación de cambios
- Sincronización con base de datos

## 🗄️ Base de Datos

El sistema utiliza **Supabase** como backend, proporcionando:
- Base de datos PostgreSQL
- API REST automática
- Autenticación y seguridad
- Backups automáticos

### Características del Modelo de Datos

- **Diseño relacional** con tabla maestra y tablas hijas
- **Integridad referencial** mediante llaves foráneas
- **Identificadores únicos** (`id_sistema`) para sincronización
- **Timestamps automáticos** para auditoría
- **Zona horaria México** para consistencia temporal

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Streamlit** | Framework web para Python |
| **Pandas** | Manipulación y análisis de datos |
| **Plotly** | Visualizaciones interactivas |
| **Supabase** | Base de datos y backend |
| **PyTZ** | Manejo de zonas horarias |
| **OpenPyXL** | Lectura de archivos Excel |

## 📈 Funcionalidades Destacadas

### Cálculo Dinámico de Días de Cobertura

El sistema calcula automáticamente los días de cobertura en tiempo real:

- **Vacantes Disponibles**: `fecha_actual - fecha_autorización` (o `fecha_solicitud`)
- **Vacantes Cerradas**: `fecha_cobertura - fecha_autorización` (o `fecha_solicitud`)

Esto asegura que las métricas siempre estén actualizadas sin depender de valores almacenados.

### Filtros Temporales Inteligentes

- **Por Trimestre**: T1 (Ene-Mar), T2 (Abr-Jun), T3 (Jul-Sep), T4 (Oct-Dic)
- **Por Semana**: Basado en calendario ISO
- **Rango de fechas** personalizado y automático

### Importación con Validación

- Validación de fechas (año 2000+)
- Asignación condicional basada en fase del proceso
- Detección automática de duplicados
- Actualización vs inserción inteligente

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es propiedad de **Especialistas Profesionales de León (Grupo EPL)**. Todos los derechos reservados.

---

## 👥 Equipo

Desarrollado con ❤️ por el equipo de Gestión y Análisis de EPL

**Grupo EPL** - Especialistas Profesionales de León
- [LinkedIn](https://linkedin.com/in/alexaemtz)
- [Sitio Web](https://www.grupoepl.com.mx/)

---

## 📞 Soporte

Para soporte técnico o dudas sobre el sistema:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo interno

---

**Última actualización**: Noviembre 2025
