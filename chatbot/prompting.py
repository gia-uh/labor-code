from chatbot.models import intents
from db.milvus_client import MilvusParagraphClient

BASE_PROMPT = """Eres un burócrata del ministerio de justicia encargado de clasificar consultas que se realizan sobre el nuevo proyecto de ley de código de trabajo que se está evaluando implementar.
El tema de esta conversación es únicamente sobre el anteproyecto del código de trabajo y si acaso sobre el código actual."""


def build_intent_classifier_prompt(q: str):
    return f"""{BASE_PROMPT}
Un usuario nos escribió con la siguiente consulta:

{q}

Tu tarea es clasificar esta consulta. Debes responder únicamente con un json con dos campos: `reasoning` con el razonamiento que permite conocer que tipo de consulta es; y `classification` donde estableces la categoría correcta de esta.
Las posibles categorías son:
{''.join([f'- {key}: {value}\n' for key,value in intents.INTENTS.items()])}
"""


def build_rag_chat_system_prompt():
    return f"""{BASE_PROMPT}
Tu tarea es conversar en español con el usuario basado en el contenido del anteproyecto. Para que puedas responder con conocimiento y no asumir nada junto al mensaje del usuario, separado por "====" se envían fragmentos del anteproyecto que se relacionan con lo mencionado por este."""


def build_rag_chat_user_prompt(q: str, db_client: MilvusParagraphClient):
    return f"""{q}

====

{'\n\n'.join(v for p in db_client.search_similar_paragraphs(q,limit=5) for _,v in p)}"""
