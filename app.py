import streamlit as st
import datetime
import os
import tempfile
import gc
import io
import fitz  # PyMuPDF para lectura de PDFs
from fpdf import FPDF
from PIL import Image, ImageOps

# --- SOPORTE HEIC (Para fotos de iPhone) ---
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

# ==============================================================================
# CONFIGURACIÓN INICIAL Y TEMA CORPORATIVO
# ==============================================================================
st.set_page_config(layout="wide", page_title="Rentokil - Panel de Supervisión")

COLOR_ROJO = "#CC0000"
COLOR_CELESTE = "#00A0E0"
COLOR_AZUL_OSCURO = "#002B49"

st.markdown(f"""
    <style>
    .stApp header {{background-color: transparent;}}
    h1, h2, h3, h4 {{color: {COLOR_AZUL_OSCURO};}}
    div[data-testid="stForm"] {{ border: 2px solid {COLOR_ROJO}; border-radius: 10px; padding: 20px; }}
    button[kind="primary"] {{ 
        background-color: {COLOR_ROJO} !important; 
        border-color: {COLOR_ROJO} !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 8px; 
    }}
    button[kind="primary"]:hover {{ 
        background-color: {COLOR_AZUL_OSCURO} !important; 
        border-color: {COLOR_AZUL_OSCURO} !important; 
    }}
    </style>
""", unsafe_allow_html=True)

if "hora_incidente_def" not in st.session_state: st.session_state.hora_incidente_def = datetime.datetime.now().time()
if "pdf_supervision" not in st.session_state: st.session_state.pdf_supervision = None

# ==============================================================================
# FUNCIONES PARA IMÁGENES Y PDF
# ==============================================================================
def procesar_archivo_evidencia(uploaded_file):
    try:
        uploaded_file.seek(0)
        file_bytes = uploaded_file.read()
        
        if uploaded_file.name.lower().endswith('.pdf'):
            doc = fitz.open("pdf", file_bytes)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            doc.close()
        else:
            image = Image.open(io.BytesIO(file_bytes))
            image = ImageOps.exif_transpose(image)
            if image.mode != 'RGB': image = image.convert('RGB')
            
        if image.width > 1600 or image.height > 1600:
            image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
            
        w, h = image.size
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        image.save(tmp.name, format='JPEG', quality=85, optimize=True)
        image.close(); del image; gc.collect()
        return tmp.name, w, h
    except Exception as e:
        st.error(f"Error procesando archivo {uploaded_file.name}: {e}")
        return None, 0, 0

class SupervisionPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_draw_color(220, 220, 220) # Gris suave para bordes modernos

    def header(self):
        if os.path.exists('logo.png'):
            try: self.image('logo.png', 10, 8, 33)
            except: pass
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 43, 73)
        self.cell(0, 8, "INFORME DE INVESTIGACION Y KPI", ln=1, align="R")
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "RENTOKIL INITIAL CHILE SPA - SUPERVISION", ln=1, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()} - Documento Confidencial", align="C")

    def t_seccion(self, numero, texto, espacio_necesario=35):
        # Evita títulos huérfanos saltando de página si no hay espacio para el contenido inicial
        if self.get_y() + espacio_necesario > 275:
            self.add_page()
            
        self.ln(6)
        self.set_font("Arial", "B", 10)
        self.set_fill_color(204, 0, 0) # ROJO
        self.set_text_color(255, 255, 255) # BLANCO
        self.cell(0, 8, f"  {numero}. {texto.upper()}", ln=1, fill=True, border=0)
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def tabla(self, header, data, widths):
        self.set_font("Arial", "B", 8)
        self.set_fill_color(0, 160, 224) # CELESTE
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(header): 
            self.cell(widths[i], 8, h, 1, 0, 'C', True)
        self.ln()
        self.set_font("Arial", "", 8)
        self.set_text_color(0, 0, 0)
        self.set_fill_color(248, 249, 250)
        for row in data:
            for i, d in enumerate(row): 
                self.cell(widths[i], 7, str(d), 1, 0, 'C', True)
            self.ln()

    def galeria(self, fotos):
        if not fotos: return
        for i, f in enumerate(fotos):
            tmp, w, h = procesar_archivo_evidencia(f)
            if tmp:
                ratio = h / w if w > 0 else 1
                max_w = 145
                max_h = 195 
                calc_w = max_w
                calc_h = max_w * ratio
                
                if calc_h > max_h:
                    calc_h = max_h
                    calc_w = max_h / ratio
                
                if self.get_y() + calc_h > 275:
                    self.add_page()
                
                x_pos = (210 - calc_w) / 2
                self.image(tmp, x=x_pos, y=self.get_y(), w=calc_w, h=calc_h)
                self.ln(calc_h + 10) 
                os.remove(tmp)

# ==============================================================================
# BASES DE DATOS COMPLETAS
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
    "TALLER GAMMA": "Mapocho # 4573, Quinta Normal.",
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
    "Termitas": {
        "Mantencion desprolija de dispositivos de control de termitas ( Estacion con cebos en mal estado) durante el mes": 4,
        "Mantencion desprolija de dispositivos de control de termitas ( Estacion con cebos en mal estado)  por 2 vez": 8,
        "Procedimiento mal aplicado": 8
    },
    "Bioservicios": {
        "Devolucion de guia de despacho de manera semanal a su ejecutivo o encargada de control documental en el mes": 4,
        "Devolucion de guia de despacho de manera semanal a su ejecutivo o encargada de control documental por 2 vez": 8,
        "Mal uso de equipos o herramientas propias de la linea de negocio en el mes": 4,
        "Mal uso de equipos o herramientas propias de la linea de negocio por 2 vez": 8,
        "Mantencion desprolija o falta de acciones correctivas en el sistema de tratamiento de bioservicio en el mes": 4,
        "Mantencion desprolija o falta de acciones correctivas en el sistema de tratamiento de bioservicio por 2 vez": 8,
        "Mantencion desprolija del servicio, no cumplimiento de las directrices operacionales o documentales 1 vez": 4,
        "Mantencion desprolija del servicio, no cumplimiento de las directrices operacionales o documentales 2 vez": 8
    },
    "Higiene": {
        "No Cumplir en un 100% con el Registro de Devolución de Producto y guías, (Fecha y Forma) en el mes": 4,
        "No Cumplir en un 100% con el Registro de Devolución de Producto y guías, (Fecha y Forma) por 2 vez": 8,
        "No Cumplir en un 100% con el Registro de Devolución de Producto y guías, (Fecha y Forma) por 3 vez": 8,
        "No dejar productos ni residuos en clientes no autorizados por la jefatura ( Bolsas, latas, spray etc ) 1 vez": 4,
        "No dejar productos ni residuos en clientes no autorizados por la jefatura ( Bolsas, latas, spray etc ) 2 vez": 8,
        "Servicios desprolijos (Mantenciones o instalaciones incompletas o incorrectas) en el mes": 4,
        "Servicios desprolijos (Mantenciones o instalaciones incompletas o incorrectas) por 2 vez": 8
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
        "Conducir a exceso de velocidad > 10 km/h": 8
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
    },
    "RIOHS y Contrato": {
        "Presentación de gastos falsos en rendición": 8,
        "Adulterar, falsificar, modificar de cualquier forma o Firmar a nombre de otra persona sin autorizacion un documento, certificado etc": 8,
        "Conducir vehiculo de la compañia sin su licencia de conducir al dia o incumplir norma del transito": 8,
        "Emplear la máxima diligencia en el cuidado de las maquinarias, vehículos, materiales y materias primas de todo tipo y, en general, de todos los bienes": 8,
        "Cumplir con los registros de entrada y salidas por medio del sotware digital dispuesto para ello.": 8,
        "Uso de vehiculo corporativo para uso personales o en horarios no asociados a sus labores sin una autorizacion formal de su jefatura": 8,
        "Prestar servicios a terceros en funciones similares o del mismo giro de la empresa durante el período del contrato": 8,
        "Adulterar firma de servicio o cualquier aspecto de algun documento": 8,
        "No participar de las actividades de capacitacion tecnicas y de seguridad": 8,
        "Dar correcta disposición a los residuos generados por las actividades desarrolladas por la compañía, ya sean residuos industriales, domésticos, reciclables y/o peligrosos.": 8,
        "Faltar el respeto a compañeros. Jefatura y Clientes": 8
    }
}

# ==============================================================================
# ENCABEZADO DE LA APP
# ==============================================================================
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
with col_logo2:
    st.markdown(f"<h1 style='text-align: center; color: {COLOR_AZUL_OSCURO};'>🛡️ Portal de Supervisión</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: {COLOR_ROJO};'>Investigación de Incidentes y KPIs</h4>", unsafe_allow_html=True)
st.markdown("---")

st.subheader("1. Datos Generales del Incidente")
col_c1, col_c2 = st.columns(2)
with col_c1:
    cliente_sel = st.selectbox("Seleccione Cliente / Planta", list(DATABASE_CLIENTES.keys()))
    if cliente_sel == "OTRO":
        cliente_final = st.text_input("Ingrese Razón Social manualmente:")
        direccion_final = st.text_input("Ingrese Dirección manualmente:")
    else:
        cliente_final = cliente_sel
        direccion_final = st.text_input("Dirección", DATABASE_CLIENTES[cliente_sel])
with col_c2:
    fecha_incidente = st.date_input("Fecha del Incidente", datetime.date.today())
    hora_incidente = st.time_input("Hora del Incidente", st.session_state.hora_incidente_def)
    st.session_state.hora_incidente_def = hora_incidente 

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
descripcion_hechos = st.text_area("Detalle de la situación:", height=100)

st.markdown("---")

st.subheader("📊 4. Clasificación de la Desviación (Motor KPI)")
col_k1, col_k2 = st.columns(2)
with col_k1:
    tipo_area = st.selectbox("1. Seleccione Origen de la Falta", ["Área Específica (Plagas, Fumigaciones, etc.)", "Categoría General (Seguridad, Calidad, etc.)"])
with col_k2:
    if tipo_area == "Área Específica (Plagas, Fumigaciones, etc.)":
        filtro_2 = st.selectbox("2. Seleccione Área", ["Plagas", "Fumigaciones", "Rapaces", "Termitas", "Bioservicios", "Higiene"])
    else:
        filtro_2 = st.selectbox("2. Seleccione Categoría General", ["Seguridad", "Calidad", "RIOHS y Contrato"])

opciones_faltas = []
if filtro_2 in DATABASE_KPI_ESTRUCTURADA: opciones_faltas = list(DATABASE_KPI_ESTRUCTURADA[filtro_2].keys())
faltas_seleccionadas = st.multiselect("3. Seleccione la(s) Desviación(es)", opciones_faltas)

puntos_acumulados = sum([DATABASE_KPI_ESTRUCTURADA[filtro_2][f] for f in faltas_seleccionadas])
tabla_faltas_pdf = [[filtro_2, f, str(DATABASE_KPI_ESTRUCTURADA[filtro_2][f])] for f in faltas_seleccionadas]

if puntos_acumulados == 0: bono_resultado, accion_kpi, color_kpi, icono = "100% Bono", "Sin Acción (OK)", "#28a745", "✅"
elif 1 <= puntos_acumulados <= 2: bono_resultado, accion_kpi, color_kpi, icono = "100% Bono", "Correo resultado final", "#ffc107", "⚠️"
elif 3 <= puntos_acumulados <= 4: bono_resultado, accion_kpi, color_kpi, icono = "80% Bono", "Correo resultado final", "#fd7e14", "⚠️"
elif 5 <= puntos_acumulados <= 7: bono_resultado, accion_kpi, color_kpi, icono = "50% Bono", "Carta amonestación (RRHH)", "#dc3545", "🚨"
else: bono_resultado, accion_kpi, color_kpi, icono = "0% Bono (Pérdida Total)", "A definir con jefatura (RRHH)", "#8b0000", "❌"

st.markdown(f"""
    <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 8px solid {color_kpi}; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top:15px; margin-bottom:15px;">
        <h3 style="margin-top:0; color: {COLOR_AZUL_OSCURO};">{icono} Veredicto del Sistema de Puntuación</h3>
        <p style="font-size: 16px; margin:5px 0;"><b>Puntaje de Penalización Acumulado:</b> <span style="color: {color_kpi}; font-size: 20px; font-weight: bold;">{puntos_acumulados} pts</span></p>
        <p style="font-size: 16px; margin:5px 0;"><b>Impacto en Bono de Gestión:</b> {bono_resultado}</p>
        <p style="font-size: 16px; margin:0;"><b>Acción Normativa a Tomar:</b> {accion_kpi}</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

st.subheader("🔍 5. Análisis de Causas")
col_c1, col_c2 = st.columns(2)
with col_c1: causa_inmediata = st.text_area("Causas Inmediatas (Acciones Subestándares)", height=100)
with col_c2: causa_raiz = st.text_area("Causas Raíz (Factores Personales/Trabajo)", height=100)

st.markdown("---")

st.subheader("✅ 6. Plan de Acción (Medidas Correctivas)")
col_pa1, col_pa2, col_pa3 = st.columns(3)
with col_pa1: accion_inv = st.text_area("Acción Correctiva", height=68)
with col_pa2: responsable_inv = st.text_input("Responsable de ejecución")
with col_pa3: fecha_accion_inv = st.date_input("Fecha límite", datetime.date.today() + datetime.timedelta(days=7))

st.markdown("---")

st.subheader("📝 7. Conclusiones Finales")
conclusiones_finales = st.text_area("Ingrese las conclusiones de la investigación:", height=120)

st.markdown("---")

st.subheader("✍️ 8. Firma del Representante Técnico (RT)")
firma_archivo = st.file_uploader("Sube imagen de la firma (JPG, PNG)", type=['png','jpg','jpeg'], key="firma")

st.markdown("---")

st.subheader("📎 9. Anexo de Evidencias")
fotos_incidentes = st.file_uploader("Sube imágenes o documentos PDF de evidencia", accept_multiple_files=True, type=['png','jpg','jpeg','heic','pdf'])

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# GENERADOR DE PDF
# ==============================================================================
if st.button("🚀 GUARDAR Y GENERAR REPORTE (PDF)", use_container_width=True, type="primary"):
    try:
        pdf = SupervisionPDF()
        pdf.add_page()
        
        pdf.t_seccion("1", "DATOS GENERALES DEL INCIDENTE")
        pdf.tabla(["Cliente / Razon Social", "Direccion"], [[cliente_final, direccion_final]], [95, 95])
        pdf.tabla(["Fecha", "Hora"], [[str(fecha_incidente), hora_incidente.strftime("%H:%M")]], [95, 95])
        
        pdf.t_seccion("2", "PERSONAL INVOLUCRADO")
        pdf.tabla(["Nombre", "RUT", "Cargo / Funcion"], [[nombre_personal, rut_personal, cargo_personal]], [70, 40, 80])
        
        pdf.t_seccion("3", "DESCRIPCION DE LOS HECHOS")
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 6, descripcion_hechos if descripcion_hechos else "Sin descripcion registrada.", border=1)
        
        pdf.t_seccion("4", "EVALUACION KPI Y PENALIZACIONES")
        if not tabla_faltas_pdf:
            pdf.set_font("Arial", "I", 9); pdf.cell(0, 6, "No se registraron faltas.", ln=1)
        else:
            pdf.set_font("Arial", "B", 9)
            pdf.set_fill_color(0, 160, 224)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(0, 7, "  Desviaciones Registradas:", border=0, ln=1, fill=True)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", "", 9)
            for row in tabla_faltas_pdf:
                pdf.multi_cell(0, 6, f"> [{row[0]}] {row[1]} ({row[2]} Pts)", border=1)
            
        pdf.ln(3)
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(248, 249, 250)
        pdf.cell(100, 8, f"PUNTAJE TOTAL: {puntos_acumulados} Pts", border=1, fill=True)
        pdf.cell(90, 8, f"RESULTADO BONO: {bono_resultado}", border=1, ln=1, fill=True)
        pdf.cell(190, 8, f"ACCION: {accion_kpi}", border=1, ln=1, fill=True)
        
        pdf.t_seccion("5", "ANALISIS DE CAUSAS", espacio_necesario=50)
        pdf.set_font("Arial", "B", 9); pdf.cell(0, 6, "Causas Inmediatas:", ln=1)
        pdf.set_font("Arial", "", 9); pdf.multi_cell(0, 6, causa_inmediata if causa_inmediata else "N/A", border=1)
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9); pdf.cell(0, 6, "Causas Raiz:", ln=1)
        pdf.set_font("Arial", "", 9); pdf.multi_cell(0, 6, causa_raiz if causa_raiz else "N/A", border=1)
        
        pdf.t_seccion("6", "PLAN DE ACCION (MEDIDAS CORRECTIVAS)", espacio_necesario=50)
        pdf.set_font("Arial", "B", 9); pdf.cell(40, 7, "Responsable:", border=1)
        pdf.set_font("Arial", "", 9); pdf.cell(150, 7, responsable_inv if responsable_inv else "No asignado", border=1, ln=1)
        pdf.set_font("Arial", "B", 9); pdf.cell(40, 7, "Fecha Limite:", border=1)
        pdf.set_font("Arial", "", 9); pdf.cell(150, 7, str(fecha_accion_inv), border=1, ln=1)
        pdf.set_font("Arial", "B", 9); pdf.set_fill_color(0, 160, 224); pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 7, " Accion Correctiva a Implementar:", border=0, ln=1, fill=True)
        pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 7, accion_inv if accion_inv else "Sin acciones registradas.", border=1)
        
        # --- SECCIÓN 7: CONCLUSIONES FINALES ---
        pdf.t_seccion("7", "CONCLUSIONES FINALES DE LA INVESTIGACION", espacio_necesario=45)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 6, conclusiones_finales if conclusiones_finales else "Sin conclusiones registradas.", border=1)

        # --- SECCIÓN 8: FIRMA ---
        if firma_archivo:
            pdf.t_seccion("8", "FIRMA DEL REPRESENTANTE TECNICO (RT)", espacio_necesario=60)
            tmp_firma, _, _ = procesar_archivo_evidencia(firma_archivo)
            if tmp_firma:
                x_firma = (210 - 50) / 2 
                pdf.image(tmp_firma, x=x_firma, y=pdf.get_y(), w=50)
                pdf.ln(40)
                os.remove(tmp_firma)
        
        # --- SECCIÓN 9: EVIDENCIAS ---
        if fotos_incidentes:
            pdf.t_seccion("9", "EVIDENCIA FOTOGRAFICA Y DOCUMENTAL", espacio_necesario=100)
            pdf.galeria(fotos_incidentes)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf.output(tmp_pdf.name)
            with open(tmp_pdf.name, "rb") as f:
                st.session_state.pdf_supervision = f.read()
                
    except Exception as e:
        st.error(f"Error generando el PDF: {e}")

if st.session_state.pdf_supervision is not None:
    st.success("✅ Reporte Generado Exitosamente")
    
    # Formateo del nombre del archivo dinámico
    fecha_str = fecha_incidente.strftime("%d-%m-%Y")
    nombre_archivo_generado = f"{fecha_str}_informe de investigacion-{nombre_personal}.pdf"
    
    st.download_button(
        label="📄 DESCARGAR INFORME DE SUPERVISIÓN (PDF)",
        data=st.session_state.pdf_supervision,
        file_name=nombre_archivo_generado,
        mime="application/pdf",
        use_container_width=True
    )
