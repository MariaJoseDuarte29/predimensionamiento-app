import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import os
import numpy as np

# ---------- CLASE PDF PERSONALIZADO ----------
class PDF(FPDF):
    def header(self):
        self.set_fill_color(255, 192, 203)  # fondo rosado
        self.rect(0, 0, 210, 297, 'F')
        self.set_font("Arial", "B", 14)
        self.set_text_color(0)
        self.cell(0, 10, "Informe de Predimensionamiento Estructural", 0, 1, "C")
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, "Arq. María José Duarte Torres - Proceso automatizado en etapa de revisión", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()} - Informe generado automáticamente", 0, 0, "C")

# ---------- FUNCIONES DE CÁLCULO ----------
def calcular_viga(long_luz):
    h = long_luz / 10
    b = h / 2
    return h, b

def calcular_columna(Pu, fc, ancho_aferente):
    return Pu / (0.35 * fc * ancho_aferente)

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

def sugerencia_ensamble(zona, tipo):
    if tipo == "Cielorrasos":
        return {
            "Baja": "Suspension ligera o anclaje flexible.",
            "Moderada": "Perfil metálico con fijación resiliente.",
            "Alta": "Perfil metálico reforzado con elementos de anclaje sísmico."
        }[zona]
    elif tipo == "Muros divisorios":
        return {
            "Baja": "Bloques ligeros con refuerzo ocasional.",
            "Moderada": "Bloques anclados a elementos estructurales.",
            "Alta": "Muros anclados con refuerzo horizontal cada 60 cm y conexión a losa."
        }[zona]
    elif tipo == "Fachadas":
        return {
            "Baja": "Fijación convencional por gravedad.",
            "Moderada": "Fijación mecánica con doble punto de anclaje.",
            "Alta": "Fijación mecánica con refuerzo cruzado, junta flexible."
        }[zona]
    else:
        return "Consultar norma NSR-10 capítulo E para detalles específicos."

# ---------- INTERFAZ DE USUARIO ----------
st.set_page_config(page_title="Predimensionamiento Estructural", layout="centered")
st.title("Predimensionamiento Automatizado")
st.markdown("Sistema en revisión - resultados orientativos basados en la NSR-10")

with st.expander("Datos Generales del Proyecto"):
    altura_total = st.number_input("Altura total del proyecto (m)", value=12.0)
    long_luz = st.number_input("Luz libre de la viga (m)", value=5.0)
    peso_total = st.number_input("Peso total estimado (kN)", value=1200.0)
    Pu = st.number_input("Carga axial Pu (kN)", value=250.0)
    fc = st.number_input("Resistencia del concreto fc (MPa)", value=21.0)
    ancho_aferente = st.number_input("Ancho aferente de columna (m)", value=0.5)
    num_pisos = st.slider("Número de pisos", 1, 10, 4)

with st.expander("Datos Sísmicos y del Material"):
    zona_sismica = st.selectbox("Zona de amenaza sísmica", ["Baja", "Moderada", "Alta"])
    tipo_sistema = st.selectbox("Tipo de sistema estructural", ["Porticado", "Mampostería", "Dual", "Mixto"])
    material_estructural = st.selectbox("Material principal", ["Concreto reforzado", "Acero estructural", "Mampostería"], index=0)
    ap = st.number_input("Coeficiente de amplificación ap", value=1.0)
    Sds = st.number_input("Aceleración espectral Sds", value=0.9)
    Wp = st.number_input("Peso del elemento no estructural (kN)", value=2.0)

if st.button("Generar Informe"):
    st.success("Procesando datos... espera unos segundos")
    # Aquí se colocará el resto del script original, que genera el PDF y los resultados.
    st.rerun()
