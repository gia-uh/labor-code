from utils.models import intents

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
