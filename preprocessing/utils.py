# utils.py
import json
import os
from typing import Dict, List

def load_json(file_path: str) -> Dict | List:
    """Carga un archivo JSON desde la ruta especificada."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo en {file_path} no es un JSON válido.")
        return {}

def save_json(data: Dict, file_path: str):
    """Guarda un diccionario en un archivo JSON."""
    # Asegurarse de que el directorio de destino existe
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Resultados guardados en: {file_path}")

def reconstruct_complex_text(metadata_path: str, paragraphs_path: str) -> Dict[str, Dict]:
    """
    Reconstruye el texto completo de artículos o disposiciones usando sus metadatos.
    Devuelve un diccionario con id, título y texto completo.
    """
    metadata = load_json(metadata_path)
    paragraphs = load_json(paragraphs_path)
    
    reconstructed = {}
    if not metadata or not paragraphs:
        return reconstructed

    for item_id, data in metadata.items():
        start_para = data.get('begin')
        end_para = data.get('end')
        title = data.get('title', '')
        
        if start_para is not None and end_para is not None:
            # Concatenar los párrafos correspondientes al rango
            text_parts = [paragraphs.get(str(i), '') for i in range(start_para, end_para + 1)]
            full_text = ' '.join(text_parts).strip()
            reconstructed[item_id] = {
                'title': title, 
                'text': full_text,
                'begin': start_para,
                'end': end_para
            }
            
    return reconstructed

def load_simple_text(file_path: str) -> Dict[str, Dict]:
    """
    Carga textos simples (preámbulo, diagnosis, políticas) donde cada entrada es un documento.
    Devuelve un diccionario con id (key del json) y texto.
    """
    data = load_json(file_path)
    
    formatted_data = {}
    if not data:
        return formatted_data
        
    for item_id, text in data.items():
        formatted_data[item_id] = {'title': f"Elemento {item_id}", 'text': text}
        
    return formatted_data

def normalize_text(text: str) -> str:
    """Normaliza el texto para comparaciones exactas (minúsculas y sin espacios extra)."""
    return ' '.join(text.lower().split())

import json

def load_and_structure_data(base_path: str) -> Dict[str, Dict]:
    """
    Carga los datos desde articles.json y paragraphs.json y los combina
    en una estructura anidada.

    Args:
        base_path (str): La ruta a la carpeta que contiene los archivos
                         (ej. 'anteproyecto/law/').

    Returns:
        Dict[str, Dict]: Un diccionario donde cada clave es un ID de artículo
                         y el valor contiene su título, texto completo y un
                         diccionario anidado de sus párrafos.
    """
    articles_path = os.path.join(base_path, 'articles.json')
    paragraphs_path = os.path.join(base_path, 'paragraphs.json')

    try:
        with open(articles_path, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        with open(paragraphs_path, 'r', encoding='utf-8') as f:
            paragraphs_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error: No se encontró el archivo {e.filename}. Verifica las rutas.")
        return {}

    structured_data = {}
    print(f"Estructurando datos desde: {base_path}")
    
    for article_id, article_info in tqdm(articles_data.items(), desc="Procesando artículos"):
        # Asegurarse de que el artículo tiene un rango de párrafos definido
        if 'begin' not in article_info or 'end' not in article_info:
            continue

        begin = article_info['begin']
        end = article_info['end']
        
        article_paragraphs = {}
        full_text_list = []
        
        # Recorrer el rango de párrafos para este artículo
        for para_num in range(begin, end + 1):
            para_id = str(para_num)
            if para_id in paragraphs_data:
                paragraph_text = paragraphs_data[para_id]
                article_paragraphs[para_id] = paragraph_text
                full_text_list.append(paragraph_text)
        
        structured_data[article_id] = {
            'title': article_info.get('title', f'Artículo {article_id}'),
            'paragraphs': article_paragraphs,
            'full_text': " ".join(full_text_list)
        }
        
    return structured_data