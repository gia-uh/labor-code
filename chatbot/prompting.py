import json
from pathlib import Path
from chatbot.models import intents
from db.milvus_client import MilvusParagraphClient
import streamlit as st

BASE_PROMPT = """Eres un burócrata del ministerio de justicia encargado de clasificar consultas que se realizan sobre el nuevo proyecto de ley de código de trabajo que se está evaluando implementar.
El tema de esta conversación es únicamente sobre el anteproyecto del código de trabajo y si acaso sobre el código actual."""


def build_intent_classifier_prompt(q: str):
    return (
        f"""{BASE_PROMPT}
Un usuario nos escribió con la siguiente consulta:

{q}

Tu tarea es clasificar esta consulta. Debes responder únicamente con un json con dos campos: `reasoning` con el razonamiento que permite conocer que tipo de consulta es; y `classification` donde estableces la categoría correcta de esta.
Las posibles categorías son:
{''.join([f'- {key}: {value}\n' for key,value in intents.INTENTS.items()])}
""",
    )


def build_rag_chat_system_prompt():
    return (
        f"""{BASE_PROMPT}
Tu tarea es conversar en español con el usuario basado en el contenido del anteproyecto. Para que puedas responder con conocimiento y no asumir nada junto al mensaje del usuario, separado por "====" se envían fragmentos del anteproyecto que se relacionan con lo mencionado por este.""",
    )


def _fetch_paragraphs_info(q: str, db_client: MilvusParagraphClient):
    data = [p for p in db_client.search_similar_paragraphs(q, limit=5)]

    context_tree = {}

    for d in data:
        context_tree[d["title_id"]] = context_tree.get(
            d["title_id"], {"name": d["title_title"]}
        )
        chps = context_tree[d["title_id"]]["chapters"] = context_tree[
            d["title_id"]
        ].get("chapters", {})
        chps[d["chapter_id"]] = chps.get(d["chapter_id"], {"name": d["chapter_title"]})
        articles = chps[d["chapter_id"]]["articles"] = chps[d["chapter_id"]].get(
            "articles", {}
        )
        articles[d["article_id"]] = articles.get(
            d["article_id"], {"name": d["article_title"]}
        )
        articles[d["article_id"]]["paragraphs"] = articles[d["article_id"]].get(
            "paragraphs", []
        )
        articles[d["article_id"]]["paragraphs"].append(d["content"])

    context_text = ""

    db_path = Path(st.secrets["dirs"]["project.intro"]) / "updated_law"
    db_path.mkdir(parents=True, exist_ok=True)

    titles_sums = None
    chapters_sums = None

    if (tjson := db_path / "titles.json") and tjson.exists():
        titles_sums = json.load(open(tjson))
    if (cjson := db_path / "chapters.json") and cjson.exists():
        chapters_sums = json.load(open(cjson))

    for title_id, title in context_tree.items():
        # Search the title summary in db
        if titles_sums:
            title_summary = titles_sums.get(title_id, {}).get("summary", "")
        else:
            title_summary = ""

        # Store the summary
        context_text += f"{title["name"]}. {title_summary}\n"

        for chapter_id, chapter in title["chapters"].items():
            # Search the chapter summary in db
            if chapters_sums:
                chapter_summary = chapters_sums.get(chapter_id, {}).get("summary", "")
            else:
                chapter_summary = ""

            # Store the summary
            context_text += f"{chapter["name"]}. {chapter_summary}\n"

            for article_id, article in chapter["articles"].items():
                # Store the article name and paragraphs
                context_text += f"{article['name']}\n"
                for paragraph in article["paragraphs"]:
                    context_text += f"{paragraph}\n"

                context_text += "\n"

    return context_text, context_tree


def build_rag_chat_user_prompt(q: str, db_client: MilvusParagraphClient):
    whole_text, context_tree = _fetch_paragraphs_info(q, db_client)
    return (
        f"""{q}

====

{whole_text}""",
        context_tree,
    )
