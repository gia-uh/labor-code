import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
from tqdm import tqdm
# import utils # Asegúrate de que utils.py esté en la misma carpeta

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


def get_embeddings(texts: List[str]) -> np.ndarray:
    """Obtiene los embeddings para una lista de textos usando el cliente configurado."""
    if not texts or not any(texts):
        return np.array([])
    # Reemplaza cadenas vacías o None con un espacio para evitar errores de la API
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

def find_simple_matches(
    source_items: Dict[str, str],
    target_items: Dict[str, str],
    similarity_threshold: float = 0.7
) -> Dict:
    """
    Encuentra coincidencias semánticas directas entre dos diccionarios de texto simple (ID: texto).
    Es ideal para comparaciones planas como párrafo vs. párrafo.
    """
    print("Iniciando comparación simple (párrafo vs. párrafo)...")
    
    # 1. Preparar textos y calcular embeddings en lotes para eficiencia
    source_ids, source_texts = zip(*source_items.items()) if source_items else ([], [])
    target_ids, target_texts = zip(*target_items.items()) if target_items else ([], [])

    print("Calculando embeddings para los párrafos de origen...")
    source_embeddings = get_embeddings(list(source_texts))
    
    print("Calculando embeddings para los párrafos de destino...")
    target_embeddings = get_embeddings(list(target_texts))

    if source_embeddings.size == 0 or target_embeddings.size == 0:
        print("No se pudieron generar los embeddings. Abortando comparación.")
        return {"matches": []}

    all_matches = []
    print("Comparando todos los párrafos de origen con todos los de destino...")
    
    # 2. Realizar la comparación
    for i, source_id in enumerate(tqdm(source_ids, desc="Procesando párrafos de origen")):
        matches_for_current_source = []
        for j, target_id in enumerate(target_ids):
            similarity = cosine_similarity(source_embeddings[i], target_embeddings[j])
            
            if similarity >= similarity_threshold:
                matches_for_current_source.append({
                    "target_id": target_id,
                    "target_text": target_texts[j],
                    "similarity": round(similarity, 4)
                })
        
        if matches_for_current_source:
            sorted_matches = sorted(matches_for_current_source, key=lambda x: x['similarity'], reverse=True)
            
            all_matches.append({
                "source_id": source_id,
                "source_text": source_texts[i],
                "matches": sorted_matches
            })

    return {"matches": all_matches}


def get_paragraph_ids_from_article(article_data: Dict) -> List[str]:
    """
    Obtiene los IDs de párrafos de un artículo basándose en begin y end.
    
    Args:
        article_data: Diccionario con información del artículo que incluye begin y end
    
    Returns:
        Lista de IDs de párrafos
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
    
    Args:
        source_article: Artículo del anteproyecto con begin/end
        target_article: Artículo de la ley actual con begin/end
        source_paragraphs_data: Diccionario con todos los párrafos del anteproyecto
        target_paragraphs_data: Diccionario con todos los párrafos de la ley actual
        similarity_threshold: Umbral de similitud para párrafos
    
    Returns:
        Dict con IDs de párrafos relacionados
    """
    # Obtener IDs de párrafos para cada artículo
    source_para_ids = get_paragraph_ids_from_article(source_article)
    target_para_ids = get_paragraph_ids_from_article(target_article)
    
    if not source_para_ids or not target_para_ids:
        return {"source_paragraphs": [], "target_paragraphs": []}
    
    # Obtener textos de los párrafos
    source_texts = [source_paragraphs_data.get(para_id, '') for para_id in source_para_ids]
    target_texts = [target_paragraphs_data.get(para_id, '') for para_id in target_para_ids]
    
    # Calcular embeddings para párrafos
    source_embeddings = get_embeddings(source_texts)
    target_embeddings = get_embeddings(target_texts)
    
    if source_embeddings.size == 0 or target_embeddings.size == 0:
        return {"source_paragraphs": [], "target_paragraphs": []}
    
    # Encontrar coincidencias entre párrafos
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


def find_matches(
    source_items: Dict[str, Dict],
    target_items: Dict[str, Dict],
    source_paragraphs: Dict[str, str],
    target_paragraphs: Dict[str, str],
    similarity_threshold: float = 0.7
) -> Dict:
    # Función de ayuda para obtener el texto de forma robusta
    def get_text(item):
        return item.get('full_text', item.get('text', ''))

    # --- 1. Pre-cálculo de embeddings (solo para artículos completos) ---
    print("Pre-calculando embeddings para los textos de los artículos...")

    all_source_texts = [get_text(v) for v in source_items.values()]
    all_target_texts = [get_text(v) for v in target_items.values()]
    
    source_embeddings_flat = get_embeddings(all_source_texts)
    target_embeddings_flat = get_embeddings(all_target_texts)

    if source_embeddings_flat.size == 0 or target_embeddings_flat.size == 0:
        print("No se pudieron generar los embeddings para los artículos. Abortando comparación.")
        return {"pairs": []}

    # Asignar embeddings de artículo a cada item
    for i, item in enumerate(source_items.values()):
        item['embedding'] = source_embeddings_flat[i]
    for i, item in enumerate(target_items.values()):
        item['embedding'] = target_embeddings_flat[i]

    print("Embeddings pre-calculados. Iniciando comparación...")
    # --- Fin del pre-cálculo ---

    all_pairs = []
    
    # --- 2. Comparar artículos entre sí ---
    for source_id, source_item in tqdm(source_items.items(), desc="Procesando artículos de origen"):
        source_article_embedding = source_item['embedding']
        
        all_similarities = []
        for target_id, target_item in target_items.items():
            similarity = cosine_similarity(source_article_embedding, target_item['embedding'])
            all_similarities.append({"id": target_id, "similarity": similarity})

        if not all_similarities:
            continue

        matches_above_threshold = [s for s in all_similarities if s['similarity'] >= similarity_threshold]
        
        articles_to_process = []
        if matches_above_threshold:
            articles_to_process = matches_above_threshold
        else:
            best_match = max(all_similarities, key=lambda x: x['similarity'])
            articles_to_process.append(best_match)

        processed_articles = []
        for match in articles_to_process:
            target_id = match['id']
            target_item = target_items[target_id]
            
            # Encontrar párrafos relacionados entre los artículos
            paragraph_matches = find_paragraph_matches(source_item, target_item, source_paragraphs, target_paragraphs)
            
            processed_articles.append({
                "id": target_id,
                "similarity": round(match['similarity'], 4),
                "IDS_PAR_ACTUAL_LAW": paragraph_matches["target_paragraphs"],
                "IDS_PAR_PROJECT_LAW": paragraph_matches["source_paragraphs"]
            })

        if processed_articles:
            all_pairs.append({
                "Project_Law": {
                    "id": source_id,
                    "title": source_item.get('title', ''),
                },
                "Actual_Law": sorted(processed_articles, key=lambda x: x['similarity'], reverse=True)
            })

    return {"pairs": all_pairs}


def transform_to_paragraph_structure(pairs_result: Dict) -> Dict:
    """
    Transforma el resultado de find_matches a la estructura específica solicitada:
    {
        "ID_ART_ANTEPROYECTO": [
            {
                "ID": "ID_ART_LEY_ACTUAL",
                "IDS_PAR_ACTUAL_LAW": ["ID1","ID2","ID3"],
                "IDS_PAR_PROJECT_LAW": ["ID1","ID2","ID3"]
            }
        ]
    }
    """
    result = {}
    
    for pair in pairs_result.get("pairs", []):
        project_article_id = pair["Project_Law"]["id"]
        actual_law_articles = pair["Actual_Law"]
        
        # Crear la estructura para este artículo del anteproyecto
        article_structure = []
        
        for actual_article in actual_law_articles:
            article_structure.append({
                "ID": actual_article["id"],
                "IDS_PAR_ACTUAL_LAW": actual_article.get("IDS_PAR_ACTUAL_LAW", []),
                "IDS_PAR_PROJECT_LAW": actual_article.get("IDS_PAR_PROJECT_LAW", [])
            })
        
        result[project_article_id] = article_structure
    
    return result