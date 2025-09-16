import streamlit as st


bopened = st.session_state.bopened
btype = st.session_state.btype

bopened = "14"
btype = "pro"

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
    for title in titles.values():
        if book["begin"] <= title["begin"] and title["end"] <= book["end"]:
            btitles.append(title)
    return btitles

def get_chapters(title):
    tchapters = []
    for chapter in chapters.values():
        if title["begin"] <= chapter["begin"] and chapter["end"] <= title["end"]:
            tchapters.append(chapter)
    return tchapters

def get_sections(chapter):
    csections = []
    for section in sections.values():
        if chapter["begin"] <= section["begin"] and section["end"] <= chapter["end"]:
            csections.append(section)
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

def render_paragraph(id):
    st.markdown(pars[id])

def render_article(aid, article):
    # st.markdown('<div id="art-' + aid + '"></div>', unsafe_allow_html=True)
    for i in range(int(article["begin"]), int(article["end"]) + 1):
        render_paragraph(str(i))

def render_provision(pid, provision):
    # st.markdown('<div id="pro-' + pid + '">prueba</div>', unsafe_allow_html=True)
    for i in range(int(provision["begin"]), int(provision["end"]) + 1):
        render_paragraph(str(i))

def render_tree(block=None, opened=None):
    openart = None
    openpro = None
    if block == "art":
        openart = opened
    elif block == "pro":
        openpro = opened
    tree = {}
    for book in books.values():
        with st.expander(book["title"], expanded=inside(book, openart)):
            render_paragraph(str(book["begin"]))
            render_paragraph(str(int(book["begin"]) + 1))
            for title in get_titles(book):
                with st.expander(title["title"], expanded=inside(title, openart)):
                    render_paragraph(str(title["begin"]))
                    render_paragraph(str(int(title["begin"]) + 1))
                    for chapter in get_chapters(title):
                        with st.expander(
                            chapter["title"], expanded=inside(chapter, openart)
                        ):
                            render_paragraph(str(chapter["begin"]))
                            render_paragraph(str(int(chapter["begin"]) + 1))
                            csections = get_sections(chapter)
                            if len(csections) > 0:
                                for section in csections:
                                    with st.expander(
                                        section["title"],
                                        expanded=inside(chapter, openart),
                                    ):
                                        render_paragraph(str(section["begin"]))
                                        render_paragraph(str(int(section["begin"]) + 1))
                                        for item in get_block_articles(section):
                                            with st.expander(
                                                "Artículo " + item[0],
                                                expanded=item[0] == openart,
                                            ):
                                                render_article(item[0], item[1])
                            else:
                                for item in get_block_articles(chapter):
                                    with st.expander(
                                        "Artículo " + item[0],
                                        expanded=item[0] == openart,
                                    ):
                                        render_article(item[0], item[1])
    for block in pblocks.values():
        with st.expander(block["title"],expanded=pinside(block,openpro)):
            render_paragraph(str(block["begin"]))
            for item in get_block_provisions(block):
                with st.expander(
                    item[1]["title"],
                    expanded=item[0] == openpro,
                ):
                    render_provision(item[0],item[1])

with st.expander("Preámbulo"):
    for p in preamble.values():
        st.markdown(p)

with st.expander("Ley", expanded=True):
    render_paragraph("1")
    render_paragraph("2")
    # render_tree(st.session_state.open_art)
    render_tree("pro","14")

