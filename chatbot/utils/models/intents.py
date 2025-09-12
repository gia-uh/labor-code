from enum import StrEnum
from pydantic import BaseModel


INTENTS = {
    # "comparative": "La consulta del usuario se basa en diferencias entre la nueva ley propuesta en comparación con la ley anterior (anteproyecto vs. ley actual)",
    # "old": "La consulta del usuario se basa únicamente en lo expresado en la ley actual",
    # "new": "La consulta del usuario se basa únicamente en lo expresado en la ley actual",
    "not_related": "La consulta del usuario no tiene relación con el anteproyecto del código de trabajo y debería evitar ser respondida debido a esto. (Ejemplo: Cuál es el sentido de la vida?, Qué es la democracia?, Es Cuba una dictadura?, etc.)",
    "law": "La consulta del usuario está relacionada con el Código de trabajo y los cambios propuestos a este.",
    "neutral": "El usuario escribió un mensaje neutral que tiene que ver con el flujo normal de una conversación. Sin preguntas extras o información necesaria de otros dominios. (Ejemplo: un saludo, una petición de una explicación más detallada, etc.)",
}


# Create IntentType enum dynamically from INTENTS keys
IntentType = StrEnum("IntentType", {key.upper(): key for key in INTENTS.keys()})


class IntentOutput(BaseModel):
    reasoning: str
    classification: IntentType  # type: ignore
