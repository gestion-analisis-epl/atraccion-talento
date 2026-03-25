def estilo_metricas():
    css = """
    <style>
    div[data-testid="stMetric"] {
        display: flex !important;
        flex-direction: column !important;  /* Apilar elementos verticalmente */
        align-items: center !important;     /* Centrar horizontalmente */
        justify-content: center !important; /* Centrar verticalmente */
        background-color: rgba(255, 255, 255, 0.04); !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        box-shadow: 0 4px 30px rgb(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(5px);
        padding: 18px !important;
        border-radius: 10px !important;
        width: 100% !important;
        max-width: 300px !important;
        height: 130px !important;
    }
    
    /* eliminar fondo heredado */
    div[data-testid="metric-container"] {
        background: transparent !important;
        width: 100% !important;  /* Asegurar que ocupe todo el ancho */
    }
    
    /* Centrar los contenedores internos */
    div[data-testid="stMetric"] > div {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }
    
    /* texto */
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricValue"] {
        color: rgb(255,255,255) !important;
        text-align: center !important;
        width: 100% !important;  /* Asegurar que el texto use todo el ancho */
    }
    
    </style> 
    """
    return css