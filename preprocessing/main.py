import utils
import comparator

def main():
    """
    Función principal para ejecutar el proceso de comparación y mapeo entre
    el anteproyecto y la ley actual.
    """
    
    # --- CONFIGURACIÓN DE RUTAS Y PARÁMETROS ---
    BASE_PATH_ACTUAL = "jsons/ley-actual/law/"
    BASE_PATH_PROYECTO = "jsons/anteproyecto/"
    OUTPUT_PATH = "./mappings/"
    SIMILARITY_THRESHOLD = 0.7

    # --- DEFINICIÓN DE TAREAS DE MAPEO (ROLES INTERCAMBIADOS) ---
    # 'source' ahora se refiere al anteproyecto.
    # 'target' ahora se refiere a la ley actual.
    
    mapping_tasks = [
        # 1. Párrafo (anteproyecto) ↔ Párrafo (ley actual)
        # {
        #     "name": "parrafo_vs_parrafo",
        #     "source_type": "simple",
        #     "source_files": (f"{BASE_PATH_PROYECTO}law/paragraphs.json",),
        #     "target_type": "simple",
        #     "target_files": (f"{BASE_PATH_ACTUAL}paragraphs.json",),
        # },
        # 2. Artículo (anteproyecto) ↔ Artículo (ley actual)
        {
            "name": "articulo_vs_articulo",
            "source_type": "complex",
            "source_files": (f"{BASE_PATH_PROYECTO}law/articles.json", f"{BASE_PATH_PROYECTO}law/paragraphs.json"),
            "target_type": "complex",
            "target_files": (f"{BASE_PATH_ACTUAL}articles.json", f"{BASE_PATH_ACTUAL}paragraphs.json"),
        },
        # 3. Preámbulo (anteproyecto) ↔ Preámbulo (ley actual)
        # {
        #     "name": "preambulo_vs_preambulo",
        #     "source_type": "simple",
        #     "source_files": (f"{BASE_PATH_PROYECTO}law/preamble.json",),
        #     "target_type": "simple",
        #     "target_files": (f"{BASE_PATH_ACTUAL}preamble.json",),
        # },
        # # 4. Disposiciones (anteproyecto) ↔ Disposiciones (ley actual)
        # {
        #     "name": "disposicion_vs_disposicion",
        #     "source_type": "complex",
        #     "source_files": (f"{BASE_PATH_PROYECTO}law/provisions.json", f"{BASE_PATH_PROYECTO}law/paragraphs.json"),
        #     "target_type": "complex",
        #     "target_files": (f"{BASE_PATH_ACTUAL}provisions.json", f"{BASE_PATH_ACTUAL}paragraphs.json"),
        # },
        # # 5. Diagnóstico (anteproyecto) ↔ Artículo (ley actual)
        # {
        #     "name": "diagnostico_vs_articulo",
        #     "source_type": "simple",
        #     "source_files": (f"{BASE_PATH_PROYECTO}diagnosis.json",),
        #     "target_type": "complex",
        #     "target_files": (f"{BASE_PATH_ACTUAL}articles.json", f"{BASE_PATH_ACTUAL}paragraphs.json"),
        # },
        # # 6. Políticas (anteproyecto) ↔ Artículo (ley actual)
        # {
        #     "name": "politicas_vs_articulo",
        #     "source_type": "simple",
        #     "source_files": (f"{BASE_PATH_PROYECTO}policies.json",),
        #     "target_type": "complex",
        #     "target_files": (f"{BASE_PATH_ACTUAL}articles.json", f"{BASE_PATH_ACTUAL}paragraphs.json"),
        # },
        # # 7. Párrafo (anteproyecto) ↔ Artículo (ley actual)
        # {
        #     "name": "parrafo_vs_articulo",
        #     "source_type": "simple",
        #     "source_files": (f"{BASE_PATH_PROYECTO}law/paragraphs.json",),
        #     "target_type": "complex",
        #     "target_files": (f"{BASE_PATH_ACTUAL}articles.json", f"{BASE_PATH_ACTUAL}paragraphs.json"),
        # }
    ]

    # --- EJECUCIÓN DEL PROCESO DE COMPARACIÓN ---
    # (Esta parte del código no necesita cambios, ya que es genérica)
    for task in mapping_tasks:
        print(f"\n{'='*25} INICIANDO TAREA: {task['name']} {'='*25}")
        
        # Cargar datos de origen (ahora es el anteproyecto)
        print("Cargando datos de origen...")
        if task['source_type'] == 'complex':
            source_items = utils.reconstruct_complex_text(task['source_files'][0], task['source_files'][1])
            source_paragraphs = utils.load_json(task['source_files'][1])
        else:
            source_items = utils.load_simple_text(task['source_files'][0])
            source_paragraphs = {}
            
        # Cargar datos de destino (ahora es la ley-actual)
        print("Cargando datos de destino...")
        if task['target_type'] == 'complex':
            target_items = utils.reconstruct_complex_text(task['target_files'][0], task['target_files'][1])
            target_paragraphs = utils.load_json(task['target_files'][1])
        else:
            target_items = utils.load_simple_text(task['target_files'][0])
            target_paragraphs = {}

        # Validar que los datos se hayan cargado correctamente
        if not source_items or not target_items:
            print(f"ADVERTENCIA: No se pudieron cargar datos para la tarea '{task['name']}'. Saltando tarea.")
            continue
            
        # Realizar la comparación
        print(f"Realizando comparación con un umbral de similaridad de {SIMILARITY_THRESHOLD}...")
        results = comparator.find_matches(source_items, target_items, source_paragraphs, target_paragraphs, SIMILARITY_THRESHOLD)
        
        # Transformar a la estructura específica solicitada
        if task['name'] == 'articulo_vs_articulo':
            paragraph_structure = comparator.transform_to_paragraph_structure(results)
            # Guardar la estructura de párrafos
            paragraph_output_file = f"{OUTPUT_PATH}{task['name']}_paragraphs.json"
            utils.save_json(paragraph_structure, paragraph_output_file)
            print(f"Estructura de párrafos guardada en: {paragraph_output_file}")
        
        # Guardar resultados originales en un archivo JSON
        output_file = f"{OUTPUT_PATH}{task['name']}.json"
        utils.save_json(results, output_file)
        print(f"Resultados guardados en: {output_file}")
        
        print(f"{'='*25} TAREA FINALIZADA: {task['name']} {'='*25}")

if __name__ == "__main__":
    main()