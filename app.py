import streamlit as st
from fpdf import FPDF

# ---------- FUNCIONES ----------
def calcular_predimensionamiento(carga_muerta, carga_viva, altura_piso, num_pisos):
    # Ejemplo simple de cálculo estructural
    peso_total = (carga_muerta + carga_viva) * altura_piso * num_pisos
    return peso_total

def generar_informe_pdf(datos, resultado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt="Informe de Predimensionamiento Estructural", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="1. Datos del Proyecto", ln=True)
    for k, v in datos.items():
        pdf.cell(200, 10, txt=f"- {k}: {v}", ln=True)

    pdf.ln(5)
    pdf.cell(200, 10, txt="2. Resultado del Predimensionamiento", ln=True)
    pdf.cell(200, 10, txt=f"- Peso Total Estimado: {resultado:.2f} kN", ln=True)

    return pdf

# ---------- APP STREAMLIT ----------
st.title("Predimensionamiento Estructural - Plataforma Académica")

st.header("Datos del Proyecto")
nombre_proyecto = st.text_input("Nombre del Proyecto")
ubicacion = st.text_input("Ubicación")
zona_sismica = st.selectbox("Zona de amenaza sísmica", ["Baja", "Moderada", "Alta"])
clase_uso = st.selectbox("Clase de uso", ["I", "II", "III", "IV"])
tipo_suelo = st.selectbox("Tipo de suelo", ["A", "B", "C", "D"])

st.header("Datos de Carga y Geometría")
carga_muerta = st.number_input("Carga muerta (kN/m²)", min_value=0.0)
carga_viva = st.number_input("Carga viva (kN/m²)", min_value=0.0)
altura_piso = st.number_input("Altura entre pisos (m)", min_value=2.0, value=3.0)
num_pisos = st.number_input("Número de pisos", min_value=1, step=1)

if st.button("Calcular y Generar Informe"):
    resultado = calcular_predimensionamiento(carga_muerta, carga_viva, altura_piso, num_pisos)

    datos = {
        "Nombre del Proyecto": nombre_proyecto,
        "Ubicación": ubicacion,
        "Zona Sísmica": zona_sismica,
        "Clase de Uso": clase_uso,
        "Tipo de Suelo": tipo_suelo,
        "Carga Muerta (kN/m²)": carga_muerta,
        "Carga Viva (kN/m²)": carga_viva,
        "Altura entre Pisos (m)": altura_piso,
        "Número de Pisos": num_pisos,
    }

    pdf = generar_informe_pdf(datos, resultado)
    pdf.output("informe_predimensionamiento.pdf")
    with open("informe_predimensionamiento.pdf", "rb") as f:
        st.download_button("Descargar Informe en PDF", f, file_name="informe_predimensionamiento.pdf")
