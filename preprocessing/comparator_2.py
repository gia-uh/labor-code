import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from tqdm import tqdm

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# --- Lógica de cliente dinámico ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if LLM_PROVIDER == 'local':
    print(f"INFO: Conectando al servidor LLM local en {os.getenv('LLM_BASE_URL')}")
    client = OpenAI(base_url=os.getenv("LLM_BASE_URL"), api_key='')
    MODEL_NAME = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
else:
    print("INFO: Conectando a la API de OpenAI")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    MODEL_NAME = "text-embedding-3-large"

print(f"INFO: Usando el modelo de embeddings: {MODEL_NAME}")


# ======================================================
# FUNCIONES AUXILIARES
# ======================================================

def get_embeddings(texts: List[str]) -> np.ndarray:
    """Obtiene los embeddings para una lista de textos usando el cliente configurado."""
    if not texts or not any(texts):
        return np.array([])
    processed_texts = [text if text and text.strip() else " " for text in texts]
    try:
        response = client.embeddings.create(input=processed_texts, model=MODEL_NAME)
        return np.array([item.embedding for item in response.data])
    except Exception as e:
        print(f"Error al obtener embeddings: {e}")
        return np.array([])


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calcula la similitud coseno entre dos vectores."""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)


def get_paragraph_ids_from_article(article_data: Dict) -> List[str]:
    """
    Obtiene los IDs de párrafos de un artículo basándose en begin y end.
    """
    begin = article_data.get('begin')
    end = article_data.get('end')
    if begin is None or end is None:
        return []
    return [str(i) for i in range(begin, end + 1)]


def find_paragraph_matches(
    source_article: Dict,
    target_article: Dict,
    source_paragraphs_data: Dict,
    target_paragraphs_data: Dict,
    similarity_threshold: float = 0.6
) -> Dict:
    """
    Encuentra coincidencias entre párrafos de dos artículos relacionados.
    """
    source_para_ids = get_paragraph_ids_from_article(source_article)
    target_para_ids = get_paragraph_ids_from_article(target_article)

    if not source_para_ids or not target_para_ids:
        return {"source_paragraphs": [], "target_paragraphs": []}

    source_texts = [source_paragraphs_data.get(para_id, '') for para_id in source_para_ids]
    target_texts = [target_paragraphs_data.get(para_id, '') for para_id in target_para_ids]

    source_embeddings = get_embeddings(source_texts)
    target_embeddings = get_embeddings(target_texts)

    if source_embeddings.size == 0 or target_embeddings.size == 0:
        return {"source_paragraphs": [], "target_paragraphs": []}

    related_source_paragraphs = []
    related_target_paragraphs = []

    for i, source_id in enumerate(source_para_ids):
        best_similarity = 0
        best_target_id = None

        for j, target_id in enumerate(target_para_ids):
            similarity = cosine_similarity(source_embeddings[i], target_embeddings[j])
            if similarity > best_similarity and similarity >= similarity_threshold:
                best_similarity = similarity
                best_target_id = target_id

        if best_target_id:
            if source_id not in related_source_paragraphs:
                related_source_paragraphs.append(source_id)
            if best_target_id not in related_target_paragraphs:
                related_target_paragraphs.append(best_target_id)

    return {
        "source_paragraphs": related_source_paragraphs,
        "target_paragraphs": related_target_paragraphs
    }


# ======================================================
# FUNCIÓN PRINCIPAL DE COMPARACIÓN
# ======================================================

def find_matches(
    source_items: Dict[str, Dict],
    target_items: Dict[str, Dict],
    source_paragraphs: Dict[str, str],
    target_paragraphs: Dict[str, str],
    similarity_threshold: float = 0.7,
    mode: str = "article_vs_article"   # 👈 nuevo parámetro
) -> Dict:
    """
    Compara elementos de origen (anteproyecto) contra destino (ley actual).
    El parámetro `mode` define la salida:
      - article_vs_article → devuelve IDS_PAR_ACTUAL_LAW y IDS_PAR_PROJECT_LAW
      - simple_vs_article  → devuelve solo IDS_PAR_ACTUAL_LAW
    """

    def get_text(item):
        return item.get('full_text', item.get('text', '')) if isinstance(item, dict) else str(item)

    print("Pre-calculando embeddings para los textos de los ítems...")

    all_source_texts = [get_text(v) for v in source_items.values()]
    all_target_texts = [get_text(v) for v in target_items.values()]

    source_embeddings_flat = get_embeddings(all_source_texts)
    target_embeddings_flat = get_embeddings(all_target_texts)

    if source_embeddings_flat.size == 0 or target_embeddings_flat.size == 0:
        print("No se pudieron generar los embeddings. Abortando comparación.")
        return {"pairs": []}

    for i, item in enumerate(source_items.values()):
        if isinstance(item, dict):
            item['embedding'] = source_embeddings_flat[i]
        else:
            source_items[list(source_items.keys())[i]] = {
                "text": item,
                "embedding": source_embeddings_flat[i]
            }

    for i, item in enumerate(target_items.values()):
        if isinstance(item, dict):
            item['embedding'] = target_embeddings_flat[i]
        else:
            target_items[list(target_items.keys())[i]] = {
                "text": item,
                "embedding": target_embeddings_flat[i]
            }

    print("Embeddings pre-calculados. Iniciando comparación...")

    all_pairs = []

    for source_id, source_item in tqdm(source_items.items(), desc="Procesando ítems de origen"):
        source_embedding = source_item['embedding']

        all_similarities = []
        for target_id, target_item in target_items.items():
            similarity = cosine_similarity(source_embedding, target_item['embedding'])
            all_similarities.append({"id": target_id, "similarity": similarity})

        if not all_similarities:
            continue

        matches_above_threshold = [s for s in all_similarities if s['similarity'] >= similarity_threshold]

        articles_to_process = matches_above_threshold if matches_above_threshold else [
            max(all_similarities, key=lambda x: x['similarity'])
        ]

        processed_articles = []
        for match in articles_to_process:
            target_id = match['id']
            target_item = target_items[target_id]

            # Solo tiene sentido buscar párrafos si ambos son artículos
            paragraph_matches = (
                find_paragraph_matches(source_item, target_item, source_paragraphs, target_paragraphs)
                if mode == "article_vs_article" else {"target_paragraphs": []}
            )

            if mode == "article_vs_article":
                processed_articles.append({
                    "id": target_id,
                    "similarity": round(match['similarity'], 4),
                    "IDS_PAR_ACTUAL_LAW": paragraph_matches["target_paragraphs"],
                    "IDS_PAR_PROJECT_LAW": paragraph_matches["source_paragraphs"]
                })
            else:  # simple_vs_article
                processed_articles.append({
                    "id": target_id,
                    "similarity": round(match['similarity'], 4),
                    "IDS_PAR_ACTUAL_LAW": paragraph_matches["target_paragraphs"]
                })

        if processed_articles:
            all_pairs.append({
                "Project_Law": {
                    "id": source_id,
                    "title": source_item.get('title', '') if isinstance(source_item, dict) else ''
                },
                "Actual_Law": sorted(processed_articles, key=lambda x: x['similarity'], reverse=True)
            })

    return {"pairs": all_pairs}


# ======================================================
# TRANSFORMACIÓN DE RESULTADOS
# ======================================================

def transform_to_paragraph_structure(pairs_result: Dict) -> Dict:
    """
    Transforma el resultado de find_matches a la estructura solicitada.
    """
    result = {}

    for pair in pairs_result.get("pairs", []):
        project_article_id = pair["Project_Law"]["id"]
        actual_law_articles = pair["Actual_Law"]

        article_structure = []
        for actual_article in actual_law_articles:
            entry = {
                "ID": actual_article["id"],
                "IDS_PAR_ACTUAL_LAW": actual_article.get("IDS_PAR_ACTUAL_LAW", [])
            }
            if "IDS_PAR_PROJECT_LAW" in actual_article:
                entry["IDS_PAR_PROJECT_LAW"] = actual_article["IDS_PAR_PROJECT_LAW"]

            article_structure.append(entry)

        result[project_article_id] = article_structure

    return result
