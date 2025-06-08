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

# ... (continúa todo el contenido del código anterior sin cambios hasta justo antes de crear el PDF) ...

    resultados = {
        "Peso Total (kN)": f"{peso_total:.2f}",
        "Altura de Viga (m)": f"{h_viga:.2f}",
        "Ancho de Viga (m)": f"{b_viga:.2f}",
        "Area de Columna (m2)": f"{area_col:.4f}",
        "Fuerza Sismica Total (kN)": f"{V_sismica:.2f}",
        "Numero de Gradas": num_gradas,
        "Longitud de Escalera (m)": f"{long_escalera:.2f}",
        "Carga Sismica Elemento No Estructural (Fp)": f"{carga_fp:.2f} kN",
        "Tipo de Sistema Estructural": tipo_sistema,
        "Material Principal": material_estructural,
        "Ensamble cielorrasos": ensambles["Cielorrasos"],
        "Ensamble muros divisorios": ensambles["Muros divisorios"],
        "Ensamble fachadas": ensambles["Fachadas"],
        "Distancia mínima a vecinos (m)": normativas["Distancia mínima a vecinos (m)"],
        "Recubrimiento mínimo vigas (cm)": normativas["Recubrimiento mínimo vigas (cm)"],
        "Recubrimiento mínimo columnas por fuego (cm)": normativas["Recubrimiento mínimo columnas por fuego (cm)"],
        "Tipos de sistema estructural en mampostería": normativas["Tipos de sistema estructural en mampostería"]
    }

    # ---------- SUGERENCIAS DE MEJORAS FUTURAS ----------
    mejoras = [
        "Integración con modelos BIM (Revit, ArchiCAD) para leer geometrías directamente.",
        "Compatibilidad con bases de datos ambientales para análisis ACV.",
        "Exportación de resultados a formatos DXF o IFC.",
        "Módulo de comparación entre alternativas de diseño.",
        "Simulación de comportamiento estructural con recomendaciones normativas dinámicas.",
        "Visualización 3D básica del predimensionamiento en la app."
    ]

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    for k, v in resultados.items():
        if isinstance(v, (list, tuple)):
            pdf.multi_cell(0, 8, f"{k}:\n" + "\n".join(f" - {i}" for i in v))
        else:
            pdf.multi_cell(0, 8, f"{k}: {v}")
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.multi_cell(0, 10, "Sugerencias de mejoras futuras para arquitectos:")
    pdf.set_font("Arial", size=11)
    for item in mejoras:
        pdf.multi_cell(0, 8, f"- {item}")

    pdf.output("informe_predimensionamiento.pdf", 'F')

    with open("informe_predimensionamiento.pdf", "rb") as f:
        st.download_button("Descargar Informe en PDF", f, file_name="informe_predimensionamiento.pdf")

    os.remove(grafico_path)

