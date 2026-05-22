def estilo_metricas():
    css = """
    <style>
    div[data-testid="stMetric"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(5px);
        padding: 18px !important;
        border-radius: 10px !important;
        width: 100% !important;
        max-width: 300px !important;
        height: 130px !important;
        transition: border-color 0.2s ease, background-color 0.2s ease !important;
    }

    div[data-testid="stMetric"]:hover {
        border-color: rgba(20, 184, 166, 0.45) !important;
        background-color: rgba(20, 184, 166, 0.04) !important;
    }

    div[data-testid="metric-container"] {
        background: transparent !important;
        width: 100% !important;
    }

    div[data-testid="stMetric"] > div {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.72rem !important;
        font-weight: 400 !important;
        color: rgba(255,255,255,0.6) !important;
        text-align: center !important;
        width: 100% !important;
        letter-spacing: 0.02em !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        text-align: center !important;
        width: 100% !important;
        line-height: 1.2 !important;
    }

    div[data-testid="stMetricDelta"] {
        font-size: 0.72rem !important;
        font-weight: 500 !important;
    }
    </style>
    """
    return css


def estilo_dashboard():
    css = """
    <style>
    /* ── PAGE HEADER ──────────────────────────── */
    .dash-header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 20px;
    }
    .dash-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    .dash-badge {
        font-size: 0.7rem;
        font-weight: 400;
        color: rgba(255,255,255,0.45);
        background: rgba(255,255,255,0.06);
        padding: 3px 10px;
        border-radius: 100px;
        white-space: nowrap;
    }

    /* ── SECTION HEADERS ──────────────────────── */
    .main h3 {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-left: 3px solid #14b8a6 !important;
        padding-left: 10px !important;
        margin: 1.25rem 0 0.6rem 0 !important;
        line-height: 1.4 !important;
        letter-spacing: -0.01em !important;
    }
    .main h4 {
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        color: rgba(255,255,255,0.55) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin: 1rem 0 0.4rem 0 !important;
    }

    /* ── TABS ─────────────────────────────────── */
    div[data-baseweb="tab-list"] {
        gap: 2px !important;
        background: transparent !important;
        padding-bottom: 0 !important;
    }
    button[data-baseweb="tab"] {
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 8px 14px !important;
        color: rgba(255,255,255,0.48) !important;
        background: transparent !important;
        border-radius: 6px 6px 0 0 !important;
        transition: color 0.15s ease, background 0.15s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: rgba(255,255,255,0.85) !important;
        background: rgba(255,255,255,0.05) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #14b8a6 !important;
        background: transparent !important;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #14b8a6 !important;
        height: 2px !important;
        border-radius: 2px 2px 0 0 !important;
    }
    div[data-baseweb="tab-border"] {
        background: rgba(255,255,255,0.08) !important;
    }

    /* ── DIVIDERS ─────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid rgba(255,255,255,0.06) !important;
        margin: 1.25rem 0 !important;
    }

    /* ── EXPANDERS ────────────────────────────── */
    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background: rgba(255,255,255,0.03) !important;
    }
    div[data-testid="stExpander"] details[open] > summary {
        border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── ALERT / INFO BOXES ───────────────────── */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        font-size: 0.8rem !important;
    }

    /* ── SIDEBAR FLEX LAYOUT ─────────────────── */
    div[data-testid="stSidebarContent"] {
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
        overflow-y: auto !important;
    }
    div[data-testid="stSidebarUserContent"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 !important;
    }
    div[data-testid="stSidebarUserContent"] > div:last-child {
        margin-top: auto !important;
        padding-bottom: 1rem !important;
    }

    /* ── SIDEBAR LOGOUT BUTTON ───────────────── */
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        border-left: 2px solid transparent !important;
        border-radius: 6px !important;
        padding: 6px 10px !important;
        color: #f87171 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        box-shadow: none !important;
        transition: background 0.15s ease, border-color 0.15s ease !important;
    }
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(239, 68, 68, 0.08) !important;
        border-left: 2px solid rgba(239, 68, 68, 0.40) !important;
        color: #f87171 !important;
    }

    /* ── SIDEBAR NAV ──────────────────────────── */
    section[data-testid="stSidebar"] span[data-testid="stSidebarNavSectionHeader"] {
        font-size: 0.62rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: rgba(255,255,255,0.3) !important;
        padding: 14px 12px 4px 12px !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
        border-radius: 6px !important;
        padding: 6px 10px !important;
        color: rgba(255,255,255,0.55) !important;
        border-left: 2px solid transparent !important;
        transition: background 0.15s ease, color 0.15s ease !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
        background: rgba(255,255,255,0.05) !important;
        color: rgba(255,255,255,0.9) !important;
    }

    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {
        background: rgba(20,184,166,0.1) !important;
        color: #14b8a6 !important;
        border-left: 2px solid #14b8a6 !important;
    }

    </style>
    """
    return css
