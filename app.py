import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os
import numpy as np

# ---------- FUNCIONES DE CÁLCULO ----------
def calcular_viga(long_luz):
    h = long_luz / 10
    b = h / 2
    return h, b

def calcular_columna(Pu, fc):
    return Pu / (0.35 * fc)

def calcular_cortante_sismica(W, Cs):
    return Cs * W

def calcular_distribucion_sismica(Vb, num_pisos):
    pesos = np.linspace(1, 2, num_pisos)
    pesos /= pesos.sum()
    return Vb * pesos

def calcular_escalares(contrahuella=0.17, huella=0.28, altura_total=3):
    num_gradas = round(altura_total / contrahuella)
    return num_gradas, num_gradas * huella

def calcular_fp(ap, Sds, Wp):
    return 0.4 * ap * Sds * Wp

class PDF(FPDF):
    def header(self):
        self.set_fill_color(255, 192, 203)
        self.rect(0, 0, 210, 20, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0)
        self.cell(0, 10, 'Informe de Predimensionamiento Estructural', ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-20)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(100)
        self.cell(0, 10, 'Documento automatizado - Arq. Maria Jose Duarte Torres', ln=True, align='C')
        self.cell(0, 10, f'Pagina {self.page_no()}', align='C')

def generar_informe_pdf(datos, resultados, grafico_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_fill_color(255, 240, 245)
    pdf.set_text_color(0)

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
        pdf.cell(0, 10, "3. Diagramas", ln=True)
        pdf.image(grafico_path, x=10, y=pdf.get_y()+5, w=180)
        pdf.ln(90)

    pdf.ln(6)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(0, 10, "4. Notas Normativas (NSR-10)", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, "Este informe automatizado aplica recomendaciones de la NSR-10:\n- Vigas: h ≈ L/10, b ≈ h/2.\n- Columnas: A >= Pu / (0.35·fc).\n- Fuerza sismica: V = Cs·W, distribuida por piso.\n- Elementos no estructurales: Fp = 0.4·ap·Sds·Wp.\n- Escaleras: Contrahuella ~17cm, Huella ~28cm.\nRevisar con ingenieria estructural detallada antes de ejecucion.")

    return pdf

# ---------- INTERFAZ STREAMLIT RESTAURADA ----------
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
fc = st.number_input("Resistencia del concreto fc (MPa)", min_value=14.0, value=21.0)
Cs = st.number_input("Coeficiente sísmico Cs", min_value=0.05, value=0.1)
ap = st.number_input("Coeficiente ap del elemento no estructural", min_value=0.5, value=1.0)
Sds = st.number_input("Aceleración espectral Sds", min_value=0.1, value=0.6)
Wp = st.number_input("Peso del elemento no estructural (kN)", min_value=1.0, value=50.0)

if st.button("Calcular y Generar Informe"):
    peso_total = (carga_muerta + carga_viva) * altura_piso * num_pisos
    h_viga, b_viga = calcular_viga(long_luz)
    area_col = calcular_columna(Pu, fc)
    V_sismica = calcular_cortante_sismica(peso_total, Cs)
    distribucion = calcular_distribucion_sismica(V_sismica, num_pisos)
    num_gradas, long_escalera = calcular_escalares(altura_total=altura_piso)
    carga_fp = calcular_fp(ap, Sds, Wp)

    # Crear gráfico
    fig, axs = plt.subplots(2, 1, figsize=(6, 8))
    axs[0].barh(range(num_gradas), [(i+1)*0.28 for i in range(num_gradas)], height=0.15, color='gray')
    axs[0].set_title("Diagrama de Escalera")
    axs[0].invert_yaxis()
    axs[0].set_xlabel("Huella (m)")
    axs[0].set_ylabel("Grada")

    pisos = [f"Piso {i+1}" for i in range(num_pisos)]
    axs[1].bar(pisos, distribucion[::-1], color='#ff69b4')
    axs[1].set_title("Distribución de Fuerza Sísmica por Piso")
    axs[1].set_ylabel("Fuerza (kN)")
    axs[1].set_xticklabels(pisos, rotation=45)

    grafico_path = "diagrama_temp.png"
    plt.tight_layout()
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

    with open("informe_predimensionamiento.pdf", "rb") as f:
        st.download_button("Descargar Informe en PDF", f, file_name="informe_predimensionamiento.pdf")

    os.remove(grafico_path)
