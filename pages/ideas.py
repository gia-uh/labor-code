import streamlit as st

polmap = st.session_state["mappings"]["policies"]
diamap = st.session_state["mappings"]["diagnosis"]

# st.write(polmap)
# st.write(diamap)

def render_diagnosis(did):
    diag = st.session_state.intro["diagnosis"][did]
    st.markdown(diag)
    if did in diamap and did!="1":
        with st.expander("Algunos artículos relacionados en el proyecto"):
            with st.container(horizontal=True,horizontal_alignment="left"):
                for art in diamap[did]:
                    art_button = st.button("Art. "+ art,key="d-"+did+"-"+art)
                    if art_button:
                        st.session_state.text_block = ("art", art)
                        st.switch_page("pages/project.py")
    
def render_policy(pid):
    pol = st.session_state.intro["policies"][pid]
    st.markdown(pol)
    if pid in polmap:
        with st.expander("Algunos artículos relacionados en el proyecto"):
            with st.container(horizontal=True,horizontal_alignment="left"):
                for art in polmap[pid]:
                    art_button = st.button("Art. "+ art,key="p-"+pid+"-"+art)
                    if art_button:
                        st.session_state.text_block = ("art", art)
                        st.switch_page("pages/project.py")
    

with st.expander("Introducción"):
    for p in st.session_state.intro["intro"].values():
        st.markdown(p)
        
with st.expander("Antecentes"):
    for p in st.session_state.intro["background"].values():
        st.markdown(p)
        
with st.expander("Diagnóstico"):
    for did in st.session_state.intro["diagnosis"].keys():
        render_diagnosis(did)
        
with st.expander("Políticas"):
    for did in st.session_state.intro["policies"].keys():
        render_policy(did)