import streamlit as st
from pages.project import get_titles, get_chapters, get_sections

questions = st.session_state["questions"]

preamble = st.session_state.project["preamble"]
pars = st.session_state.project["paragraphs"]
books = st.session_state.project["books"]
titles = st.session_state.project["titles"]
chapters = st.session_state.project["chapters"]
sections = st.session_state.project["sections"]
articles = st.session_state.project["articles"]
pblocks = st.session_state.project["provisions_blocks"]
provisions = st.session_state.project["provisions"]
abs_books = st.session_state["abstract"]["books"]
abs_titles = st.session_state["abstract"]["titles"]
abs_chapters = st.session_state["abstract"]["chapters"]
abs_sections = st.session_state["abstract"]["sections"]

open_blocks = False if ("open_blocks" not in st.session_state) else st.session_state["open_blocks"]

def render_section_questions(id):
    qsection = questions["sections_questions"][id]
    with st.expander("Palabras Clave"):
        keywords = abs_sections[id]["keywords"][0] 
        for k in abs_sections[id]["keywords"][1:]:
            keywords += ", " + k
        st.markdown(keywords)
    with st.expander("Resumen"):
        st.markdown(abs_sections[id]["summary"])
    with st.expander("Ideas Generales"):
        for i in abs_sections[id]["ideas"]:
            st.markdown("* "+i)
    with st.expander("Preguntas relacionadas"):
        for q in qsection:
            st.markdown("***"+q["question"]+"***")
            st.markdown(q["answer"])
            
def render_sections(bsections):
    for sid,section in bsections:
        with st.expander(section["title"],expanded=open_blocks):
            render_chapter_questions(sid)

def render_chapter_questions(id):
    qchapter = questions["chapters_questions"][id]
    with st.expander("Palabras Clave"):
        keywords = abs_chapters[id]["keywords"][0] 
        for k in abs_chapters[id]["keywords"][1:]:
            keywords += ", " + k
        st.markdown(keywords)
    with st.expander("Resumen"):
        st.markdown(abs_chapters[id]["summary"]) 
    with st.expander("Ideas Generales"):
        for i in abs_chapters[id]["ideas"]:
            st.markdown("* "+i)
    with st.expander("Preguntas relacionadas"):
        for q in qchapter:
            st.markdown("***"+q["question"]+"***")
            st.markdown(q["answer"])

def render_chapters(bchatpers):
    for cid,chapter in bchatpers:
        with st.expander(chapter["title"],expanded=open_blocks):
            render_chapter_questions(cid)
            bsections = get_sections(chapter)
            if len(bsections)!=0:
                render_sections(bsections)

def render_title_questions(id):
    qtitle = questions["titles_questions"][id]
    with st.expander("Palabras Clave"):
        keywords = abs_titles[id]["keywords"][0] 
        for k in abs_titles[id]["keywords"][1:]:
            keywords += ", " + k
        st.markdown(keywords) 
    with st.expander("Resumen"):
        st.markdown(abs_titles[id]["summary"])
    with st.expander("Ideas Generales"):
        for i in abs_titles[id]["ideas"]:
            st.markdown("* "+i)
    with st.expander("Preguntas relacionadas"):
        for q in qtitle:
            st.markdown("***"+q["question"]+"***")
            st.markdown(q["answer"])

def render_titles(btitles):
    for tid,title in btitles:
        with st.expander(title["title"],expanded=open_blocks):
            render_title_questions(tid)
            bchatpers = get_chapters(title)
            if len(bchatpers)!=0:
                render_chapters(bchatpers)

def render_book_questions(id):
    qbook = questions["books_questions"][id]
    with st.expander("Palabras Clave"):
        keywords = abs_books[id]["keywords"][0] 
        for k in abs_books[id]["keywords"][1:]:
            keywords += ", " + k
        st.markdown(keywords)
    with st.expander("Resumen"):
        st.markdown(abs_books[id]["summary"]) 
    with st.expander("Ideas Generales"):
        for i in abs_books[id]["ideas"]:
            st.markdown("* "+i)
    with st.expander("Preguntas relacionadas"):
        for q in qbook:
            st.markdown("***"+q["question"]+"***")
            st.markdown(q["answer"])
        

def render_books():
    with st.container(horizontal=True,horizontal_alignment="right"):
        obutton = st.button("Abrir los bloques")
        if obutton:
            st.session_state["open_blocks"] = True
            st.rerun()
        cbutton = st.button("Cerrar los bloques")
        if cbutton:
            st.session_state["open_blocks"] = False
            st.rerun()
    for bid,book in books.items():
        with st.expander(book["title"],expanded=open_blocks):
            render_book_questions(bid)
            btitles = get_titles(book)
            if len(btitles)!=0:
                render_titles(btitles)
            
            
render_books()
                