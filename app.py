import streamlit as st
import datetime

# --- CONFIGURACIÓN INICIAL Y TEMA CELESTE ---
st.set_page_config(layout="wide", page_title="Rentokil - Panel de Supervisión")

COLOR_CELESTE = "#00A0E0"
COLOR_AZUL_OSCURO = "#002B49"

st.markdown(f"""
    <style>
    .stApp header {{background-color: transparent;}}
    h1, h2, h3 {{color: {COLOR_AZUL_OSCURO};}}
    div[data-testid="stForm"] {{ border: 2px solid {COLOR_CELESTE}; border-radius: 10px; padding: 20px; }}
    button[kind="primary"] {{
        background-color: {COLOR_CELESTE} !important;
        border-color: {COLOR_CELESTE} !important;
        color: white !important;
        font-weight: bold !important;
    }}
    button[kind="primary"]:hover {{
        background-color: {COLOR_AZUL_OSCURO} !important;
        border-color: {COLOR_AZUL_OSCURO} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- BASES DE DATOS ---

DATABASE_CLIENTES = {
    "AGROCOMMERCE": "Av. José Miguel Infante 8745, Renca, Región Metropolitana",
    "TUCAPEL CD": "VOLCAN LINCABUR 435, PUDAHUEL",
    "ECONUT PARCELA 30": "18 SEPT, Paine",
    "CV TRADING": "CAMINO VALDIVIA DE PAINE S/N BUIN",
    "CALBU BUIN": "La Estancilla 8991, Buin, Región Metropolitana",
    "LA PINTANA": "Lautaro 2260, La Pintana",
    "PUENTE VERDE": "Avenida Puente Verde 2080, Quilicura",
    "FINE FRUITS": "PAULA JARAQUEMADA, PAINE",
    "STARFOOD": "Bernardo O'Higgins 150, 9361274 Colina, Región Metropolitana",
    "TUCAPEL STGO CENTRO": "Tucapel 3140, Santiago, Bodega 10 PNC",
    "MALTEXCO": "Bellavista 681, 9680086 Talagante, Región Metropolitana, Chile",
    "NAMA": "Cam. Bernardo O'Higgins 20137, Pudahuel, Región Metropolitana, Chile",
    "PRUNESCO": "RAMON SUBERCASEUX 2712, Pirque, Chile",
    "WALMART": "Av. El Parque 1000, Pudahuel, Región Metropolitana",
    "LA INVERNADA": "CAMINO SAN MIGUEL PARC 2 PAINE",
    "AGROCOMMERCE LOGINSA": "LO SIERRA 04460 SAN BDO",
    "PACKING MERQUEN": "PANAM. SUR KM. 40 , PAINE",
    "CHOROMBO": "CAMINO PUBLICO CASABLANCA KM. 22, MARIA PINTO",
    "MOLINO PUENTE ALTO": "BALMACEDA 27 PTE ALTO",
    "VITAKAI": "CAMINO STA. CECILIA PARC SAN EDO., EL MONTE",
    "DAFF": "PANAM. NORTE 16950 LAMPA",
    "CRAMER": "BALMACEDA 3050 PEÑAFLOR",
    "LA TAPERA": "SAN MIGUEL DE LIRAY PARCELA 16 Y 17 COLINA",
    "GROWEX": "CAMINO LAS PARCELAS 21 ISLA DE MAIPO",
    "BALMACEDA": "BALMACEDA 1726 STGO",
    "GOOD FOOD": "BALMACEDA 3050 PEÑAFLOR",
    "KIOSCLUB": "JUAN ELIAS 1701 RECOLETA",
    "PRODALMEN": "FUNDO CHALLAY ALTO, HUELQUEN, PAINE",
    "DEGESCH": "JOSE LUIS CARO 1321, PADRE HURTADO",
    "CAROZZI NOS": "LONGITUDINAL SUR 5201, NOS",
    "MSC MAIPU": "AV. PAJARITOS 1061 MAIPU",
    "MOLINO EXPOSICION": "AV. EXPOSICION 1657 EST CENTRAL",
    "MOLINO BALMACEDA": "BALMACEDA 1726 STGO",
    "MSC EXPOSICION": "AV. EXPOSICION 1657 EST CENTRAL",
    "TALLER GAMMA": "Mapocho  # 4573 , Quinta Normal.",
    "CAMPO ANDINO": "CAMINO EL OLIVETO 4193 TALAGANTE",
    "OTRO": ""
}

DATABASE_PERSONAL = {
    "Marcos Escobar": {"rut": "8.546.549-K", "cargo": "Técnico"},
    "Carlos Narbona": {"rut": "20.121.067-K", "cargo": "Representante Técnico"},
    "Cristian Corral": {"rut": "16.630.012-6", "cargo": "Técnico"},
    "Eduardo Inostroza": {"rut": "18.692.998-5", "cargo": "Técnico"},
    "Juan Vásquez": {"rut": "15.629.902-2", "cargo": "Técnico"},
    "Maximiliano Caro": {"rut": "20.120.770-3", "cargo": "Representante Técnico"},
    "Víctor Becerra": {"rut": "17.759.655-8", "cargo": "Técnico"},
    "Sebastián Carrillo": {"rut": "19.514.568-7", "cargo": "Representante Técnico"},
    "Cristian Saavedra": {"rut": "19.703.885-3", "cargo": "Técnico"},
    "Juan Callofa": {"rut": "15.531.428-1", "cargo": "Representante Técnico"},
    "OTRO": {"rut": "", "cargo": ""}
}

# --- ENCABEZADO DE LA APP ---
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
with col_logo2:
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_AZUL_OSCURO};'>🛡️ Portal de Supervisión</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: {COLOR_CELESTE};'>Investigación de Incidentes y KPIs</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# FORMULARIO DE INVESTIGACIÓN
# ==============================================================================

st.subheader("1. Datos Generales del Incidente")
col_c1, col_c2 = st.columns(2)
with col_c1:
    cliente_sel = st.selectbox("Seleccione Cliente / Planta", list(DATABASE_CLIENTES.keys()))
    if cliente_sel == "OTRO":
        cliente_final = st.text_input("Ingrese Razón Social manualmente:")
        direccion_final = st.text_input("Ingrese Dirección manualmente:")
    else:
        cliente_final = cliente_sel
        direccion_final = st.text_input("Dirección (Auto-completada)", DATABASE_CLIENTES[cliente_sel])

with col_c2:
    fecha_incidente = st.date_input("Fecha del Incidente", datetime.date.today())
    hora_incidente = st.time_input("Hora del Incidente", datetime.datetime.now().time())

st.markdown("---")

st.subheader("2. Personal Involucrado (Evaluado)")
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    personal_sel = st.selectbox("Seleccione Técnico / Representante", list(DATABASE_PERSONAL.keys()))
    if personal_sel == "OTRO":
        nombre_personal = st.text_input("Ingrese Nombre manualmente:")
        rut_personal = st.text_input("Ingrese RUT manualmente:")
        cargo_personal = st.text_input("Ingrese Cargo manualmente:")
    else:
        nombre_personal = personal_sel
        rut_personal = st.text_input("RUT", DATABASE_PERSONAL[personal_sel]["rut"])
        cargo_personal = st.text_input("Cargo", DATABASE_PERSONAL[personal_sel]["cargo"])

st.markdown("---")

st.subheader("3. Descripción de los Hechos")
st.markdown("Registre la declaración del técnico o el relato objetivo de la desviación encontrada.")
descripcion_hechos = st.text_area("Detalle de la situación:", height=150, placeholder="Ej: Durante la inspección de rutina, se detectó que el técnico...")

# Espacio reservado para el paso 4 (Motor KPI)
st.markdown("---")
st.info("Próximamente: Motor de Evaluación KPI y Puntajes (Paso 4)")
