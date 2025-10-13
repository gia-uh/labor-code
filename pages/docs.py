import streamlit as st

pdf_current_law = st.secrets["doc"]["current"]["law"]
pdf_project_law = st.secrets["doc"]["project"]["law"]

st.markdown("**Código de Trabajo Vigente**")
with open(pdf_current_law, "rb") as file:
    pdf_bytes = file.read()
st.download_button(label="Descargar PDF",data=pdf_bytes, file_name="codigo_vigente.pdf", mime="application/pdf")

st.pdf(pdf_current_law,height=600)

st.markdown("**Antepoyecto Código de Trabajo**")
with open(pdf_project_law, "rb") as file:
    pdf_bytes = file.read()
st.download_button(label="Descargar PDF",data=pdf_bytes, file_name="anteproyecto_codigo.pdf", mime="application/pdf")

st.pdf(pdf_project_law,height=600)