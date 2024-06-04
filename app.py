import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
from io import StringIO
from extractor import *
import pandas as pd
# Función para extraer información del PDF


def parser_remito(data_json: dict):
    persona = pd.DataFrame.from_dict([data_json["persona"]])
    persona = persona[["nombre", "direccion", "codigo_postal"]]
    persona = persona.rename(columns={
                             "nombre": "Nombre Apellido", "direccion": "Direccion", "codigo_postal": "CP"})
    factura_detalle = pd.DataFrame.from_dict(data_json["detalle"])
    factura_detalle.loc[factura_detalle["cantidad"].isna(
    ), "importe"] = factura_detalle["precio"]
    factura_detalle["cantidad"] = factura_detalle["cantidad"].fillna(1)
    monto_total = data_json["monto_total"]

    return persona, factura_detalle, monto_total


def parser_cv(data_json: dict):
    cv = {}
    cv["persona"] = pd.DataFrame([data_json["persona"]]).dropna(axis=1)
    cv["experiencias_trabajo"] = pd.DataFrame(
        data_json["experiencias_trabajo"]).dropna(axis=1)
    cv["educacion"] = pd.DataFrame(data_json["educacion"]).dropna(axis=1)
    cv["skills"] = pd.DataFrame(data_json["skills"], columns=[
                                "skills"]).dropna(axis=1)
    cv["idiomas"] = pd.DataFrame(data_json["idiomas"]).dropna(axis=1)
    return cv


def extract_information():
    app = graph()
    app = app.app
    inputs = {"question": ""}
    result = app.invoke(inputs)
    entity = result.get("extractor")
    route = result.get("route")
    message = f"### Información extraida de `{route}`."
    if route == "Other":
        message = "Archivo no Identificado, por favor cargue un Documento (Remito-Factura o CV)."
        st.warning(message)
    elif route == "Remito-Factura":
        persona, factura_detalle, monto_total = parser_remito(entity)
        st.write(message)
        st.write("### Persona:")
        st.write(persona)
        st.write(f"### Total Facturado: `{monto_total}`")
        st.write("### Detalle:")
        st.write(factura_detalle)
    elif route == "Curriculum Vitae-Hoja de Vida":
        cv = parser_cv(entity)
        st.write(message)
        st.write("### Curriculum Datos Personales:")
        st.write(cv["persona"])
        st.write("### Curriculum Experiencias de Trabajo:")
        st.write(cv["experiencias_trabajo"])
        st.write("### Curriculum Educación:")
        st.write(cv["educacion"])
        st.write("### Curriculum Skills:")
        st.write(cv["skills"])
        st.write("### Curriculum Idiomas:")
        st.write(cv["idiomas"])
    else:
        st.write(message)
        st.write(entity)


# Configuración de la página
st.set_page_config(page_title="Visualizador de PDF", page_icon="📄")

# Barra lateral para cargar el archivo PDF
uploaded_file = st.sidebar.file_uploader("Elige un archivo PDF", type="pdf")
if uploaded_file is not None:
    # To read file as bytes:
    with open("data/data_extractor/data.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

# Variable de estado para controlar la visibilidad del visualizador de PDF
show_pdf_viewer = False

# Dividir la página en dos columnas: 70% para el visualizador y 30% para el extractor
col1, col2 = st.columns([6, 4])

# Sección del visualizador de PDF
with col1:
    if uploaded_file is not None:
        # Leer el archivo PDF
        pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        # Mostrar el número de páginas
        num_pages = pdf_document.page_count
        st.info(f"El documento tiene {num_pages} página(s).")

        # Variable de estado para controlar la visibilidad del visualizador
        # Botón para alternar la visualización del PDF
        toggle_viz_doc = st.toggle("Visualizar")

        # Visualización del PDF (mostrado si show_pdf_viewer es True)
        if toggle_viz_doc:
            # Seleccionar el número de página
            page_num = st.number_input(
                "Número de página", min_value=1, max_value=num_pages, step=1, key="page_num") - 1

            # Cargar la página seleccionada
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()

            # Convertir a imagen
            image = Image.open(io.BytesIO(pix.tobytes()))

            # Mostrar la imagen en el visualizador
            st.image(
                image, caption=f"Página {page_num + 1}", use_column_width=True)
    else:
        st.info("Por favor, carga un archivo PDF para visualizarlo.")

# Sección del extractor de información
with col2:
    st.info("Extractor de Información")
    if st.button("Extraer Información"):
        # Mostrar la información extraída
        extract_information()
