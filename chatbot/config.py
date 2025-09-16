import os
import streamlit as st

config = {
    "OPENAI_BASE_URL": st.secrets["llm"]["base_url"],
    "OPENAI_MODEL": st.secrets["llm"]["model"],
    "OPENAI_KEY": st.secrets["llm"]["api_key"]
    **os.environ,
}
