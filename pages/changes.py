import streamlit as st
import json
import os
from pathlib import Path
import markdown
import pdfkit
import io

user = st.session_state.username

file = Path(f"data/{user}.json")

if file.exists():
        user_data = json.loads(file.read_bytes())
        text=  "|Párrafo No.|Clasificación|Propuesta|\n"
        text+= "|-----------|-------------|---------|\n"
        for pid,item in user_data.items():
            if "additions" in item:
                for d in item["deletions"]:
                    text+="|"+pid+"|Adición|"+d+"|\n"
            if "deletions" in item:
                for d in item["deletions"]:
                    text+="|"+pid+"|Eliminación|"+d+"|\n"
            if "modifications" in item:
                for d in item["modifications"]:
                    text+="|"+pid+"|Modificación|"+d+"|\n"
            if "questions" in item:
                for d in item["questions"]:
                    text+="|"+pid+"|Duda|"+d+"|\n"
        
        st.markdown(text)
        # md_text = "# Hola\nEste es un texto en **Markdown**"

        # html = f"""
        # <html>
        # <head><meta charset="utf-8"></head>
        # <body>{markdown.markdown(text)}</body>
        # </html>
        # """
        
        # pdf_bytes = pdfkit.from_string(html, False)
        # st.download_button(
        #     label="Descargar propuesta en PDF",
        #     data=pdf_bytes,
        #     file_name="propuesta.pdf",
        #     mime="application/pdf"
        # )
else:
    st.markdown("**Aún no se han realizado propuestas**")