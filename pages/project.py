from pathlib import Path
import streamlit as st
import uuid
import json
import os


preamble = st.session_state.project["preamble"]
pars = st.session_state.project["paragraphs"]
books = st.session_state.project["books"]
titles = st.session_state.project["titles"]
chapters = st.session_state.project["chapters"]
sections = st.session_state.project["sections"]
articles = st.session_state.project["articles"]
pblocks = st.session_state.project["provisions_blocks"]
provisions = st.session_state.project["provisions"]


def inside(item, aid):
    if aid == None:
        return False
    art = articles[aid]
    return item["begin"] <= art["begin"] and art["end"] <= item["end"]


def pinside(item, pid):
    if pid == None:
        return False
    pro = provisions[pid]
    return item["begin"] <= pro["begin"] and pro["end"] <= item["end"]


def get_titles(book):
    btitles = []
    for id, title in titles.items():
        if book["begin"] <= title["begin"] and title["end"] <= book["end"]:
            btitles.append((id, title))
    return btitles


def get_chapters(title):
    tchapters = []
    for id, chapter in chapters.items():
        if title["begin"] <= chapter["begin"] and chapter["end"] <= title["end"]:
            tchapters.append((id, chapter))
    return tchapters


def get_sections(chapter):
    csections = []
    for id, section in sections.items():
        if chapter["begin"] <= section["begin"] and section["end"] <= chapter["end"]:
            csections.append((id, section))
    return csections


def get_block_articles(block):
    sarts = []
    for id, article in articles.items():
        if block["begin"] <= article["begin"] and article["end"] <= block["end"]:
            sarts.append((id, article))
    return sarts


def get_block_provisions(block):
    bprovs = []
    for id, provision in provisions.items():
        if block["begin"] <= provision["begin"] and provision["end"] <= block["end"]:
            bprovs.append((id, provision))
    return bprovs


@st.dialog(" ", on_dismiss="rerun")
def user_interaction(action: str, id: str):
    key = f"user_vote_{action}"
    user_input = st.text_area(
        f"{action.capitalize()}",
        height=300,
        width=500,
        key=key,
        placeholder="Por favor introduzca su idea aquí...",
        label_visibility="collapsed",
        # on_change= lambda: st.session_state.update({key: st.session_state[key]})
    )
    if st.button("Guardar") and user_input not in [None, ""]:
        save_user_action(user_input, action, st.session_state.username, id)
        user_input = ""
        st.rerun()


def save_user_action(input: str, action: str, user: str, id: str):
    """
    Saves user input to a JSON file

    Args:
         paragraph_id (str): The paragraph identifier
        action (str): The action type
        text (str): The text to save
    """
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    file = Path(f"data/{user}.json")
    if file.exists():
        user_data = json.loads(file.read_bytes())
    else:
        user_data = {}

    if id not in user_data:
        user_data[id] = {
            "additions": [],
            "deletions": [],
            "modifications": [],
            "questions": [],
        }

    user_data[id][action].append(input)

    output = json.dumps(user_data, indent=4)
    file.write_text(output)


def render_paragraph(id):
    with st.container():
        
        st.markdown(pars[id])

        actions = ["additions", "deletions", "questions", "modifications"]
        icons = [
            ":material/add:",
            ":material/delete:",
            ":material/question_mark:",
            ":material/edit:",
        ]
        helps = ["Adicionar", "Eliminar", "Duda", "Cambiar"]

        with st.container(
            width="stretch",
            height=50,
            gap="small",
            border=False,
            horizontal=True,
            horizontal_alignment="right",
        ):
            for i, (action, icon, help_text) in enumerate(zip(actions, icons, helps)):

                st.button(
                    "",
                    width=8,
                    icon=icon,
                    key=f"{action}_{id}_{uuid.uuid4()}",
                    help=help_text,
                    on_click=user_interaction,
                    args=(action, id),
                )


def render_article(aid, article):
    for i in range(int(article["begin"]), int(article["end"]) + 1):
        render_paragraph(str(i))


def render_provision(pid, provision):
    for i in range(int(provision["begin"]), int(provision["end"]) + 1):
        render_paragraph(str(i))


def render_preamble():
    for p in preamble.values():
        st.markdown(p)


def render_nav_buttons():
    cols = st.columns(2)
    if "text_block" in st.session_state:
        tid = st.session_state.text_block[1]
        ttype = st.session_state.text_block[0]
        if ttype == "pre":
            with cols[1]:
                with st.container(horizontal=True,horizontal_alignment="right"):
                    right = st.button("Próximo ->")
                    if right:
                        st.session_state.text_block = ("art", "1")
                        st.rerun()
        elif ttype == "art":
            if tid == "1":
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("pre", None)
                            st.rerun()
                with cols[1]:
                    with st.container(horizontal=True,horizontal_alignment="right"):
                        right = st.button("Próximo ->")
                        if right:
                            st.session_state.text_block = ("art", "2")
                            st.rerun()
            elif 2 <= int(tid) < 525:
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("art", str(int(tid) - 1))
                            st.rerun()
                with cols[1]:
                    with st.container(horizontal=True,horizontal_alignment="right"):
                        right = st.button("Próximo ->")
                        if right:
                            st.session_state.text_block = ("art", str(int(tid) + 1))
                            st.rerun()
            else:
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("art", str(int(tid) - 1))
                            st.rerun()
                with cols[1]:
                    with st.container(horizontal=True,horizontal_alignment="right"):
                        right = st.button("Próximo ->")
                        if right:
                            st.session_state.text_block = ("pro", "1")
                            st.rerun()
        else:
            if tid == "1":
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("art", "525")
                            st.rerun()
                with cols[1]:
                    with st.container(horizontal=True,horizontal_alignment="right"):
                        right = st.button("Próximo ->")
                        if right:
                            st.session_state.text_block = ("pro", "1")
                            st.rerun()
            elif 2 <= int(tid) < 28:
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("pro", str(int(tid) - 1))
                            st.rerun()
                with cols[1]:
                    with st.container(horizontal=True,horizontal_alignment="right"):
                        right = st.button("Próximo ->")
                        if right:
                            st.session_state.text_block = ("pro", str(int(tid) + 1))
                            st.rerun()
            else:
                with cols[0]:
                    with st.container(horizontal=True,horizontal_alignment="left"):
                        left = st.button("<- Anterior")
                        if left:
                            st.session_state.text_block = ("pro", str(int(tid) - 1))
                            st.rerun()


def render_text_block():
    tid = st.session_state.text_block[1]
    ttype = st.session_state.text_block[0]
    if ttype == "pre":
        render_preamble()
    elif ttype == "pro":
        render_provision(tid, provisions[tid])
    else:
        render_article(tid, articles[tid])


s1v = [i for i in range(1, 9)]
s1d = {
    1: "Preámbulo",
    2: "LIBRO PRIMERO",
    3: "LIBRO SEGUNDO",
    4: "LIBRO TERCERO",
    5: "LIBRO CUARTO",
    6: "DISPOSICIONES ESPECIALES",
    7: "DISPOSICIONES TRANSITORIAS",
    8: "DISPOSICIONES FINALES",
}


def get_blocks_index():
    bindex = {
        "book": None,
        "title": None,
        "chapter": None,
        "section": None,
        "article": None,
        "provision": None,
    }
    if "text_block" not in st.session_state:
        return bindex
    tid = st.session_state.text_block[1]
    ttype = st.session_state.text_block[0]
    if ttype == "pre":
        return bindex
    if ttype == "pro":
        if 1 <= int(tid) <= 10:
            return {
                "book": 6,
                "title": None,
                "chapter": None,
                "section": None,
                "article": None,
                "provision": tid,
            }
        elif 11 <= int(tid) <= 22:
            return {
                "book": 7,
                "title": None,
                "chapter": None,
                "section": None,
                "article": None,
                "provision": tid,
            }
        else:
            return {
                "book": 8,
                "title": None,
                "chapter": None,
                "section": None,
                "article": None,
                "provision": tid,
            }
    else:
        art = articles[tid]
        bindex["book"] = art["book"]
        bindex["title"] = art["title"]
        bindex["chapter"] = art["chapter"]
        bindex["section"] = art["section"]
        bindex["article"] = tid
        return bindex


def get_select_index(values, value):
    if value in values:
        return values.index(value)
    return 0


cols = st.columns(5)

with cols[0]:
    sindex = get_blocks_index()
    s1 = st.selectbox(
        "Libro",
        options=s1v,
        format_func=lambda x: s1d[x],
        index=get_select_index(s1v, sindex["book"]),
    )
    if s1 == 1:
        st.session_state.text_block = ("pre", None)
    elif 2 <= s1 <= 5:
        with cols[1]:
            sbook = books[str(s1 - 1)]
            stitles = get_titles(sbook)
            s2v = [i[0] for i in stitles]
            s2d = {i[0]: i[1]["title"] for i in stitles}
            s2 = st.selectbox(
                "Título",
                options=s2v,
                format_func=lambda x: s2d[x],
                index=get_select_index(s2v, sindex["title"]),
            )
            with cols[2]:
                stitle = titles[s2]
                schapters = get_chapters(stitle)
                if len(schapters) != 0:
                    s3v = [i[0] for i in schapters]
                    s3d = {i[0]: i[1]["title"] for i in schapters}
                    s3 = st.selectbox(
                        "Capítulo",
                        options=s3v,
                        format_func=lambda x: s3d[x],
                        index=get_select_index(s3v, sindex["chapter"]),
                    )
                    with cols[3]:
                        schapter = chapters[s3]
                        ssections = get_sections(schapter)
                        if len(ssections) != 0:
                            s4v = [i[0] for i in ssections]
                            s4d = {i[0]: i[1]["title"] for i in ssections}
                            s4 = st.selectbox(
                                "Sección",
                                options=s4v,
                                format_func=lambda x: s4d[x],
                                index=get_select_index(s4v, sindex["section"]),
                            )
                            with cols[4]:
                                ssection = sections[s4]
                                sarticles = get_block_articles(ssection)
                                s5v = [i[0] for i in sarticles]
                                s5d = {
                                    i[0]: "Artículos " + i[0] + " - " + i[1]["title"]
                                    for i in sarticles
                                }
                                s5 = st.selectbox(
                                    "Artículo",
                                    options=s5v,
                                    format_func=lambda x: s5d[x],
                                    index=get_select_index(s5v, sindex["article"]),
                                )
                                st.session_state.text_block = ("art", s5)
                        else:
                            sarticles = get_block_articles(schapter)
                            s4v = [i[0] for i in sarticles]
                            s4d = {
                                i[0]: "Artículos " + i[0] + " - " + i[1]["title"]
                                for i in sarticles
                            }
                            s4 = st.selectbox(
                                "Artículo",
                                options=s4v,
                                format_func=lambda x: s4d[x],
                                index=get_select_index(s4v, sindex["article"]),
                            )
                            st.session_state.text_block = ("art", s4)
                else:
                    sarticles = get_block_articles(stitle)
                    s3v = [i[0] for i in sarticles]
                    s3d = {
                        i[0]: "Artículos " + i[0] + " - " + i[1]["title"]
                        for i in sarticles
                    }
                    s3 = st.selectbox(
                        "Artículo",
                        options=s3v,
                        format_func=lambda x: s3d[x],
                        index=get_select_index(s3v, sindex["article"]),
                    )
                    st.session_state.text_block = ("art", s3)
    else:
        with cols[1]:
            sbprov = pblocks[str(s1 - 5)]
            sprovs = get_block_provisions(sbprov)
            s2v = [i[0] for i in sprovs]
            s2d = {i[0]: i[1]["title"] for i in sprovs}
            s2 = st.selectbox(
                "Disposición",
                options=s2v,
                format_func=lambda x: s2d[x],
                index=get_select_index(s2v, sindex["provision"]),
            )
            st.session_state.text_block = ("pro", s2)

# st.divider()

render_nav_buttons()

# st.divider()

render_text_block()
