import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os

# ---------- FUNCIONES DE CÁLCULO ----------
def calcular_viga(long_luz):
    h = long_luz / 10  # Altura mínima (m)
    b = h / 2  # Ancho mínimo (m)
    return h, b

def calcular_columna(Pu, fc):
    area_min = Pu / (0.35 * fc)
    return area_min

def calcular_cortante_sismica(W, Cs):
    return Cs * W

def calcular_escalares(contrahuella=0.17, huella=0.28, altura_total=3):
    num_gradas = round(altura_total / contrahuella)
    long_total = num_gradas * huella
    return num_gradas, long_total

def calcular_fp(ap, Sds, Wp):
    return 0.4 * ap * Sds * Wp

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Informe de Predimensionamiento Estructural', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def generar_informe_pdf(datos, resultados, grafico_path):
    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "1. Datos del Proyecto", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in datos.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "2. Resultados de Predimensionamiento", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in resultados.items():
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    if grafico_path:
        pdf.ln(6)
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "3. Diagrama de Escalera", ln=True)
        pdf.image(grafico_path, x=10, y=pdf.get_y()+5, w=180)
        pdf.ln(85)

    pdf.ln(6)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "4. Notas Normativas (NSR-10)", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, "Los resultados presentados siguen los lineamientos básicos de la Norma NSR-10.\n- Vigas: Se sugiere altura mínima h = L/10 y ancho b = h/2.\n- Columnas: Área mínima A = Pu / (0.35·f'c).\n- Cortante sísmico: V = Cs · W.\n- Elementos no estructurales: Fp = 0.4·ap·Sds·Wp.\n- Escaleras: Contrahuella ~17cm, Huella ~28cm.\nEstos cálculos son de aproximación inicial y deben verificarse con diseño estructural detallado.")

    return pdf

# ---------- INTERFAZ STREAMLIT ----------
st.title("Predimensionamiento Estructural - Plataforma Académica")

st.header("Datos del Proyecto")
nombre_proyecto = st.text_input("Nombre del Proyecto")
ubicacion = st.text_input("Ubicación")
zona_sismica = st.selectbox("Zona de amenaza sísmica", ["Baja", "Moderada", "Alta"])
clase_uso = st.selectbox("Clase de uso", ["I", "II", "III", "IV"])
tipo_suelo = st.selectbox("Tipo de suelo", ["A", "B", "C", "D"])

st.header("Cargas y Geometría")
carga_muerta = st.number_input("Carga muerta (kN/m²)", min_value=0.0)
carga_viva = st.number_input("Carga viva (kN/m²)", min_value=0.0)
altura_piso = st.number_input("Altura entre pisos (m)", min_value=2.0, value=3.0)
num_pisos = st.number_input("Número de pisos", min_value=1, step=1)
long_luz = st.number_input("Longitud de luz de viga (m)", min_value=1.0, value=5.0)
Pu = st.number_input("Carga axial en columna (kN)", min_value=1.0, value=200.0)
fc = st.number_input("Resistencia del concreto f'c (MPa)", min_value=14.0, value=21.0)
Cs = st.number_input("Coeficiente sísmico Cs", min_value=0.05, value=0.1)
ap = st.number_input("Coeficiente ap del elemento no estructural", min_value=0.5, value=1.0)
Sds = st.number_input("Aceleración espectral Sds", min_value=0.1, value=0.6)
Wp = st.number_input("Peso del elemento no estructural (kN)", min_value=1.0, value=50.0)

if st.button("Calcular y Generar Informe"):
    peso_total = (carga_muerta + carga_viva) * altura_piso * num_pisos
    h_viga, b_viga = calcular_viga(long_luz)
    area_col = calcular_columna(Pu, fc)
    V_sismica = calcular_cortante_sismica(peso_total, Cs)
    num_gradas, long_escalera = calcular_escalares(altura_total=altura_piso)
    carga_fp = calcular_fp(ap, Sds, Wp)

    # Generar gráfico simple de escalera y guardarlo como imagen
    fig, ax = plt.subplots()
    for i in range(num_gradas):
        ax.plot([0, (i+1)*0.28], [i*0.17, i*0.17], color='black')
        ax.plot([(i+1)*0.28, (i+1)*0.28], [i*0.17, (i+1)*0.17], color='black')
    ax.set_title("Diagrama de Escalera")
    ax.set_xlabel("Huella (m)")
    ax.set_ylabel("Altura (m)")
    ax.axis("equal")
    grafico_path = "escalera_temp.png"
    plt.savefig(grafico_path)
    plt.close()

    datos = {
        "Nombre del Proyecto": nombre_proyecto,
        "Ubicación": ubicacion,
        "Zona Sísmica": zona_sismica,
        "Clase de Uso": clase_uso,
        "Tipo de Suelo": tipo_suelo
    }

    resultados = {
        "Peso Total (kN)": f"{peso_total:.2f}",
        "Altura de Viga (m)": f"{h_viga:.2f}",
        "Ancho de Viga (m)": f"{b_viga:.2f}",
        "Área de Columna (cm²)": f"{area_col*10000:.2f}",
        "Fuerza Sísmica Total (kN)": f"{V_sismica:.2f}",
        "Número de Gradas": num_gradas,
        "Longitud de Escalera (m)": f"{long_escalera:.2f}",
        "Carga Sísmica Elemento No Estructural (Fp)": f"{carga_fp:.2f} kN"
    }

    pdf = generar_informe_pdf(datos, resultados, grafico_path)
    pdf.output("informe_predimensionamiento.pdf")

    # Mostrar botón para descarga del informe
    with open("informe_predimensionamiento.pdf", "rb") as f:
        st.download_button("Descargar Informe en PDF", f, file_name="informe_predimensionamiento.pdf")

    # Eliminar imagen temporal
    os.remove(grafico_path)
