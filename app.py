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
