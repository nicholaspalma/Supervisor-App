import streamlit as st
import datetime

# ==============================================================================
# CONFIGURACIÓN INICIAL Y TEMA CORPORATIVO
# ==============================================================================
st.set_page_config(layout="wide", page_title="Rentokil - Panel de Supervisión")

COLOR_CELESTE = "#00A0E0"
COLOR_AZUL_OSCURO = "#002B49"

st.markdown(f"""
    <style>
    .stApp header {{background-color: transparent;}}
    h1, h2, h3, h4 {{color: {COLOR_AZUL_OSCURO};}}
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

# ==============================================================================
# BASES DE DATOS (CLIENTES, PERSONAL Y KPIs)
# ==============================================================================
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

DATABASE_KPI_ESTRUCTURADA = {
    "Plagas": {
        "Servicio desinsectacion sin señaletica calavera, medidas preventivas en el mes": 8,
        "Servicio sanitizacion baños sin sanitizar y marcaje durante el mes": 4,
        "Servicio sanitizacion baños sin sanitizar y marcaje por 2 vez": 8,
        "Servicio de desinsectacion y sanitizacion desprolijo (durante el mes)": 4,
        "Servicio de desinsectacion y sanitizacion desprolijo (por 2 vez)": 8,
        "Mantencion desprolija de dispositivos de control, feromonas (durante el mes)": 4,
        "Mantencion desprolija de dispositivos de control, feromonas (por 2 vez)": 8,
        "Mantencion desprolija de dispositivos de control, tuv (durante el mes)": 4,
        "Mantencion desprolija de dispositivos de control, tuv (por 2 vez)": 8,
        "Mantencion desprolija de dispositivos de control, en mal estado (durante el mes)": 4,
        "Mantencion desprolija de dispositivos de control, en mal estado (por 2 vez)": 8,
        "No realización de planos durante la instalacion/emergencia (durante el mes)": 4,
        "No realización de planos durante la instalacion/emergencia (por 2 vez)": 8,
        "Devolucion de guia de despacho (durante el mes)": 4,
        "Devolucion de guia de despacho (por 2 vez)": 8
    },
    "Fumigaciones": {
        "No realizar inyeccion/ventilacion según proc. (Sin fugas, en el mes)": 4,
        "No realizar inyeccion/ventilacion según proc. (Sin fugas, por 2 vez)": 8,
        "No realizar inyeccion/ventilacion según proc. (Con fugas o riesgo)": 8
    },
    "Rapaces": {
        "Mantencion desprolija de dispositivos de control de aves (durante el mes)": 4,
        "Mantencion desprolija de dispositivos de control de aves (por 2 vez)": 8
    },
    "Seguridad": {
        "No realiza Check List de Vehículos durante el mes": 8,
        "Tener accidentes de responsabilidad directa": 8,
        "Uso incorrecto de EPP": 8,
        "No usar EPP para los riesgos asociados en el lugar de trabajo": 8,
        "Reclamo de cliente asociado a la Seguridad o mala conducción (durante el mes)": 4,
        "Reclamo de cliente asociado a la Seguridad o mala conducción (2 vez)": 8,
        "No dar aviso de manera inmediata cuando ocurra un accidente o incidente": 8,
        "Realiza trabajo en altura/confinado sin examenes medicos al dia": 8,
        "Conducir a exceso de velocidad 1 a 5 km/h (1 min)": 4,
        "Conducir a exceso de velocidad 6 a 9 km/h (1 min)": 8,
        "No dar correcta disposición a los residuos generados": 8,
        "Disposición de residuos no autorizados en clientes/particulares": 8,
        "Conducir a exceso de velocidad > 10 km/h": 8,
        "Reclamo de cliente asociado a mala gestión/calidad/puntualidad (durante el mes)": 4,
        "Reclamo de cliente asociado a mala gestión/calidad/puntualidad (2 vez)": 8
    },
    "Calidad": {
        "Reprogramacion directo con cliente": 4,
        "No comunica via correo si no cumple la ruta asignada": 4,
        "No cumple en realizar servicios programados sin justificacion": 4,
        "Certificados sin informacion o incompleta o ilegible": 6,
        "Certificado no cumple indicaciones tecnicas": 6,
        "No envio de informes asociados al certificado": 6,
        "No ingresa mínimo dos recomendaciones por visita": 6,
        "Guia de despacho sin nombre, rut y firma": 6,
        "Reducion de la jornada y no cumplimiento de los procedimientos": 6,
        "Falta de insumos, herramientas y/o equipos en camioneta": 6,
        "No Utilizar ropa corporativa al iniciar la jornada": 6,
        "No Respetar la normativa de los clientes (EPP, uso joyas)": 6,
        "Vehiculo sucio, equipos mal almacenados": 6,
        "Baja de Cliente asociada a mala gestión (<= 2%)": 0,
        "Baja de Cliente asociada a mala gestión (> 2%)": 8,
        "No usar Movil Form / Mala efectividad de llenado": 4,
        "No notifica alarmas por Formulario o correo (1 vez)": 2,
        "No notifica alarmas por Formulario o correo (2 vez)": 4
    }
}

# ==============================================================================
# ENCABEZADO DE LA APP
# ==============================================================================
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
with col_logo2:
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_AZUL_OSCURO};'>🛡️ Portal de Supervisión</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: {COLOR_CELESTE};'>Investigación de Incidentes y KPIs</h4>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# SECCIONES DEL FORMULARIO
# ==============================================================================

# --- 1. DATOS GENERALES ---
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

# --- 2. PERSONAL INVOLUCRADO ---
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

# --- 3. DESCRIPCIÓN DE LOS HECHOS ---
st.subheader("3. Descripción de los Hechos")
st.markdown("Registre la declaración del técnico o el relato objetivo de la desviación encontrada.")
descripcion_hechos = st.text_area("Detalle de la situación:", height=150, placeholder="Ej: Durante la inspección de rutina, se detectó que el técnico...")

st.markdown("---")

# --- 4. MOTOR KPI ---
st.subheader("📊 4. Clasificación de la Desviación (Motor KPI)")
st.markdown("Seleccione el Área/Categoría para desplegar las faltas. **Puede seleccionar múltiples faltas.**")

col_k1, col_k2 = st.columns(2)
with col_k1:
    tipo_area = st.selectbox("1. Seleccione Origen de la Falta", ["Área Específica (Plagas, Fumigaciones, etc.)", "Categoría General (Seguridad, Calidad, etc.)"])
    
with col_k2:
    if tipo_area == "Área Específica (Plagas, Fumigaciones, etc.)":
        filtro_2 = st.selectbox("2. Seleccione Área", ["Plagas", "Fumigaciones", "Rapaces", "Termitas", "Bioservicios", "Higiene"])
    else:
        filtro_2 = st.selectbox("2. Seleccione Categoría General", ["Seguridad", "Calidad", "RIOHS y Contrato"])

opciones_faltas = []
if filtro_2 in DATABASE_KPI_ESTRUCTURADA:
    opciones_faltas = list(DATABASE_KPI_ESTRUCTURADA[filtro_2].keys())
    
faltas_seleccionadas = st.multiselect("3. Seleccione la(s) Desviación(es) Cometida(s)", opciones_faltas)

# Cálculo matemático del bono
puntos_acumulados = 0
for falta in faltas_seleccionadas:
    puntos_acumulados += DATABASE_KPI_ESTRUCTURADA[filtro_2][falta]

if puntos_acumulados == 0:
    bono_resultado = "100% Bono"
    accion_kpi = "Sin Acción (OK)"
    color_kpi = "#28a745" # Verde
    icono = "✅"
elif 1 <= puntos_acumulados <= 2:
    bono_resultado = "100% Bono"
    accion_kpi = "Correo resultado final"
    color_kpi = "#ffc107" # Amarillo
    icono = "⚠️"
elif 3 <= puntos_acumulados <= 4:
    bono_resultado = "80% Bono"
    accion_kpi = "Correo resultado final"
    color_kpi = "#fd7e14" # Naranja
    icono = "⚠️"
elif 5 <= puntos_acumulados <= 7:
    bono_resultado = "50% Bono"
    accion_kpi = "Carta amonestación (RRHH)"
    color_kpi = "#dc3545" # Rojo
    icono = "🚨"
else: # 8 o más
    bono_resultado = "0% Bono (Pérdida Total)"
    accion_kpi = "A definir con jefatura (RRHH)"
    color_kpi = "#8b0000" # Rojo oscuro
    icono = "❌"

st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 8px solid {color_kpi}; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top:15px; margin-bottom:15px;">
        <h3 style="margin-top:0; color: {COLOR_AZUL_OSCURO};">{icono} Veredicto del Sistema de Puntuación</h3>
        <p style="font-size: 16px; margin:5px 0;"><b>Puntaje de Penalización Acumulado:</b> <span style="color: {color_kpi}; font-size: 20px; font-weight: bold;">{puntos_acumulados} pts</span></p>
        <p style="font-size: 16px; margin:5px 0;"><b>Impacto en Bono de Gestión:</b> {bono_resultado}</p>
        <p style="font-size: 16px; margin:0;"><b>Acción Normativa a Tomar:</b> {accion_kpi}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- 5. ANÁLISIS DE CAUSAS ---
st.subheader("🔍 5. Análisis de Causas")
col_c1, col_c2 = st.columns(2)
with col_c1:
    causa_inmediata = st.text_area("Causas Inmediatas (Acciones/Condiciones Subestándares)", height=100)
with col_c2:
    causa_raiz = st.text_area("Causas Raíz (Factores Personales/Trabajo)", height=100)

st.markdown("---")

# --- 6. PLAN DE ACCIÓN ---
st.subheader("✅ 6. Plan de Acción (Medidas Correctivas)")
col_pa1, col_pa2, col_pa3 = st.columns(3)
with col_pa1:
    accion_inv = st.text_area("Acción Correctiva a Implementar", height=68)
with col_pa2:
    responsable_inv = st.text_input("Responsable de ejecución (Supervisor/Técnico)")
with col_pa3:
    fecha_accion_inv = st.date_input("Fecha límite de Cumplimiento", datetime.date.today() + datetime.timedelta(days=7))

st.markdown("---")

# --- 7. EVIDENCIAS ---
st.subheader("📎 7. Anexo de Evidencias")
fotos_incidentes = st.file_uploader("Sube fotos o archivos (Imágenes, PDF, etc.)", accept_multiple_files=True, type=['png','jpg','jpeg','heic','pdf','docx'])

st.markdown("<br>", unsafe_allow_html=True)

# --- BOTÓN FINAL ---
if st.button("🚀 GUARDAR Y GENERAR REPORTE", use_container_width=True, type="primary"):
    st.success("¡Formulario completado! (La generación de PDF se conectará en el próximo paso).")
