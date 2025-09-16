from openai import OpenAI
from typing import List
import json
import os

client = OpenAI(base_url="http://10.6.125.217:8080/v1", api_key='')

def build_context(path: str, key: str) -> List[str]:
    with open(path, 'r', encoding='utf-8') as fd:
        data = json.load(fd)
    
    with open("jsons/anteproyecto/law/paragraphs.json", 'r', encoding='utf-8') as fd:
        paragraph = json.load(fd)

    docs = []
    for i in range(int(data[key]["begin"]), int(data[key]["end"])+1):
        docs.append(paragraph[str(i)])
    
    return docs

TASK = "Resumen"
FILES = ["sections.json", "chapters.json","titles.json", "books.json"]
PATH = "jsons/anteproyecto/law/"
OUTPATH = "jsons/anteproyecto/updated_law/"
SYSTEM_PROMPT = """
Eres un asistente experto especializado en leyes cuya tarea es responder preguntas usando solo la información proporcionada en el contexto. 

1. Analiza cuidadosamente el contexto dado.
2. Contesta la pregunta de manera clara, precisa y relevante.
3. Usa un tono formal según lo indicado.
4. No agregues información externa ni supongas datos no presentes.
"""

USER_PROMPT = {
    "1": ["Por favor, lee el siguiente texto y crea un resumen claro y conciso que capture las ideas principales y la información más relevante del contexto presentado.", "sumary"],
    "2":["Analiza el texto a continuación y extrae las ideas esenciales, aquellas que fundamentan el contenido y que son imprescindibles para entender el mensaje principal.", "ideas"],
    "3":["Identifica y enumera las palabras clave más importantes del siguiente texto, aquellas que mejor representan los temas y conceptos centrales tratados en él.", "keywords"]
}

if not os.path.exists(OUTPATH):
    os.mkdir(OUTPATH)

for file in FILES:
     
    with open(f"{PATH}{file}", 'r', encoding='utf-8') as fd:
        data = json.load(fd)

    for prompt in USER_PROMPT:

        for key in data:

            docs = build_context(f"{PATH}{file}", key)

            # Pasar prompt para generar respuesta
            chat_response = client.chat.completions.create(
                model="qwen/qwen3-14b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "Contexto relevante:\n" + "\n".join(docs)},
                    {"role": "user", "content": USER_PROMPT[prompt][0]}
                ],
                temperature=0.7,
                max_tokens=512,
            )

            result = chat_response.choices[0].message.content
            data[key][USER_PROMPT[prompt][1]] = result
        with open(f"{OUTPATH}{file}", 'w', encoding='utf-8') as fd:
                json.dump(data, fd, indent=4)
