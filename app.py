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
    h_viga, b_viga = calcular_viga(long_luz)
    area_columna = calcular_columna(Pu, fc, ancho_aferente)
    Vb = calcular_cortante_sismica(peso_total, 0.1)
    distrib_sismo = calcular_distribucion_sismica(Vb, num_pisos)
    gradas, longitud_escalera = calcular_escalares(altura_total=altura_total)
    fp = calcular_fp(ap, Sds, Wp)

    st.write("**Altura recomendada de viga:**", round(h_viga, 2), "m")
    st.write("**Ancho recomendado de viga:**", round(b_viga, 2), "m")
    st.write("**Área mínima de columna:**", round(area_columna, 3), "m²")
    st.write("**Cortante sísmico basal Vb:**", round(Vb, 2), "kN")
    st.write("**Distribución sísmica por piso:**", distrib_sismo.round(2).tolist())
    st.write("**Número de gradas:**", gradas)
    st.write("**Longitud total de la escalera:**", round(longitud_escalera, 2), "m")
    st.write("**Fuerza sísmica sobre elemento no estructural:**", round(fp, 2), "kN")

    st.write("---")
    st.write("**Sugerencias por zona sísmica:**")
    for tipo in ["Cielorrasos", "Muros divisorios", "Fachadas"]:
        st.write(f"- {tipo}: {sugerencia_ensamble(zona_sismica, tipo)}")

    # ----- DESCARGA DE PDF OPCIONAL -----
    if st.button("Descargar informe en PDF"):
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"Altura recomendada de viga: {round(h_viga, 2)} m")
        pdf.multi_cell(0, 10, f"Ancho recomendado de viga: {round(b_viga, 2)} m")
        pdf.multi_cell(0, 10, f"Área mínima de columna: {round(area_columna, 3)} m²")
        pdf.multi_cell(0, 10, f"Cortante sísmico basal Vb: {round(Vb, 2)} kN")
        pdf.multi_cell(0, 10, f"Distribución sísmica por piso: {distrib_sismo.round(2).tolist()}")
        pdf.multi_cell(0, 10, f"Número de gradas: {gradas}")
        pdf.multi_cell(0, 10, f"Longitud total de la escalera: {round(longitud_escalera, 2)} m")
        pdf.multi_cell(0, 10, f"Fuerza sísmica sobre elemento no estructural: {round(fp, 2)} kN")

        for tipo in ["Cielorrasos", "Muros divisorios", "Fachadas"]:
            pdf.multi_cell(0, 10, f"{tipo}: {sugerencia_ensamble(zona_sismica, tipo)}")

        buffer = io.BytesIO()
        pdf.output(buffer)
        st.download_button(
            label="📄 Descargar PDF",
            data=buffer.getvalue(),
            file_name="informe_predimensionamiento.pdf",
            mime="application/pdf"
        )
