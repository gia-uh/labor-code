import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import re

# Page settings
st.set_page_config(
    page_title="Análisis de Interacciones - Anteproyecto de Ley",
    page_icon="📊",
    layout="wide"
)

# Areas based on email domains
AREAS = {
    "AREA CENTRAL": "ac",
    "BIOMAT": "biomat",
    "CEAP": "ceap",
    "CEDEM": "cedem",
    "CEEC": "ceec",
    "CEHSEU": "cehseu",
    "CEPES": "cepes",
    "CETED": "ceted",
    "CIEI": "ciei",
    "CIM": "cim",
    "COLEGIO GRADO 12": "grado12",
    "CONFUCIO": "confucio",
    "FACULTAD DE ARTES Y LETRAS": "fayl",
    "FACULTAD DE BIOLOGIA": "fbio",
    "FACULTAD DE COMUNICACION": "fcom",
    "FACULTAD DE CONTABILIDAD Y FINANZAS": "fcf",
    "FACULTAD DE DERECHO": "lex",
    "FACULTAD DE ECONOMIA": "fec",
    "FACULTAD DE ESPAÑOL PARA NO HISPANOHABLANTES": "fenhi",
    "FACULTAD DE FILOSOFIA E HISTORIA": "ffh",
    "FACULTAD DE FISICA": "fisica",
    "FACULTAD DE GEOGRAFIA": "geo",
    "FACULTAD DE LENGUAS EXTRANJERAS": "flex",
    "FACULTAD DE MATEMATICA Y COMPUTACION": "matcom",
    "FACULTAD DE PSICOLOGIA": "psico",
    "FACULTAD DE QUIMICA": "fq",
    "FACULTAD DE TURISMO": "ftur",
    "FACULTAD PREPARATORIA": "fpi",
    "FLACSO": "flacso",
    "FUNDACION": "fundacion",
    "IMRE": "imre",
    "INSTEC": "instec",
    "INSTITUTO DE FARMACIA Y ALIMENTOS": "ifal",
    "IRIS": "iris",
    "ISDI": "isdi",
    "JBN": "jbn",
    "RECTORADO": "rect",
    "SAN GERONIMO": "sangeronimo",
    "UPA": "upa"
}

# Interaction categories
CAT = {
    "additions": "AGREGAR",
    "deletions": "ELIMINAR",
    "modifications": "MODIFICAR",
    "questions": "DUDAS"
}

# Book structure
BOOKS = {
    1 : "PREAMBULO",
    2: "LIBRO PRIMERO",
    3: "LIBRO SEGUNDO", 
    4: "LIBRO TERCERO",
    5: "LIBRO CUARTO",
    6: "DISPOSICIONES ESPECIALES",
    7: "DISPOSICIONES TRANSITORIAS",
    8: "DISPOSICIONES FINALES"
}

def extract_domain(email):
    """
    Extract the specific domain from a UH email
    """
    pattern = r'@(?:estudiantes\.)?([^\.]+)\.uh\.cu'
    match = re.search(pattern, email)
    return match.group(1) if match else None


def load_project_structure():
    """
    Load the project structure from session_state
    """
    if "project" not in st.session_state:
        st.error("No se ha cargado la estructura del proyecto")
        return None
    
    project = st.session_state.project
    return {
        "books": project.get("books", {}),
        "titles": project.get("titles", {}),
        "chapters": project.get("chapters", {}),
        "sections": project.get("sections", {}),
        "articles": project.get("articles", {}),
        "paragraphs": project.get("paragraphs", {}),
        "provisions_blocks": project.get("provisions_blocks", {}),
        "provisions": project.get("provisions", {})
    }


def get_paragraph_location(pid, structure):
    """
    Determina la ubicación de un párrafo en la estructura de la ley
    """
    paragraphs = structure["paragraphs"]
    articles = structure["articles"]
    provisions = structure["provisions"]
    
    # Search in articles
    for article_id, article in articles.items():
        if int(article["begin"]) <= int(pid) <= int(article["end"]):
            book_id = article.get("book")
            title_id = article.get("title")
            chapter_id = article.get("chapter")
            section_id = article.get("section")
            print(book_id)
            book_name = BOOKS.get(book_id, f"Libro {book_id}") if book_id else None
            title_name = structure["titles"].get(title_id, {}).get("title") if title_id else None
            chapter_name = structure["chapters"].get(chapter_id, {}).get("title") if chapter_id else None
            section_name = structure["sections"].get(section_id, {}).get("title") if section_id else None
            
            return {
                "book": book_name,
                "title": title_name,
                "chapter": chapter_name,
                "section": section_name,
                "article": f"Artículo {article_id}",
                "type": "article"
            }
    
    # Search in layouts
    for provision_id, provision in provisions.items():
        if int(provision["begin"]) <= int(pid) <= int(provision["end"]):
            book_id = None
            for block_id, block in structure["provisions_blocks"].items():
                if int(block["begin"]) <= int(provision_id) <= int(block["end"]):
                    book_id = block_id
                    break
            
            book_name = BOOKS.get(str(int(book_id) + 5)) if book_id else None
            
            return {
                "book": book_name,
                "title": None,
                "chapter": None,
                "section": None,
                "article": f"Disposición {provision_id}",
                "type": "provision"
            }
    
    # Paragraph not found in structure
    return {
        "book": "No identificado",
        "title": None,
        "chapter": None,
        "section": None,
        "article": None,
        "type": "unknown"
    }


def load_all_interactions():
    """
    Load all interactions from all users
    """
    data = []
    structure = load_project_structure()
    
    if not structure:
        return pd.DataFrame()
    
    # Go through all area folders
    data_dir = Path("data")
    if not data_dir.exists():
        st.warning("No se encontró el directorio 'data'")
        return pd.DataFrame()
    
    for area_folder in data_dir.iterdir():
        if area_folder.is_dir():
            area_name = area_folder.name
            # Find the legible name of the area
            readable_area = next((k for k, v in AREAS.items() if v == area_name), area_name)
            
            # Iterate through user JSON files in this area
            for user_file in area_folder.glob("*.json"):
                try:
                    with open(user_file, 'r', encoding='utf-8') as f:
                        user_data = json.load(f)
                    
                    # Process each paragraph from the user
                    for paragraph_id, interactions in user_data.items():
                        if paragraph_id.isdigit():  # Numbered paragraphs only
                            location = get_paragraph_location(paragraph_id, structure)
                            
                            # Process each type of interaction
                            for interaction_type, texts in interactions.items():
                                if interaction_type in CAT and texts:
                                    for text in texts:
                                        if text.strip():  #Only non-empty text
                                            data.append({
                                                "Area": readable_area,
                                                "Parrafo_ID": paragraph_id,
                                                "Texto_Parrafo": structure["paragraphs"].get(paragraph_id, ""),
                                                "Categoria": CAT[interaction_type],
                                                "Informacion": text.strip(),
                                                "Libro": location["book"],
                                                "Titulo": location["title"],
                                                "Capitulo": location["chapter"],
                                                "Seccion": location["section"],
                                                "Articulo": location["article"],
                                                #"Usuario": user_file.stem,
                                                "Tipo_Texto": location["type"]
                                            })
                except Exception as e:
                    st.warning(f"Error al cargar {user_file}: {str(e)}")
    
    return pd.DataFrame(data)


def get_available_areas():
    """
    It retrieves the available areas (that have data)
    """
    areas = ["TODAS"]
    data_dir = Path("data")
    
    if data_dir.exists():
        for area_folder in data_dir.iterdir():
            if area_folder.is_dir():
                area_name = area_folder.name
                readable_area = next((k for k, v in AREAS.items() if v == area_name), area_name)
                areas.append(readable_area)
    
    return areas


def main():
    st.title("📊 Análisis de Interacciones - Anteproyecto de Ley")
    st.markdown("Analiza las interacciones de usuarios con el anteproyecto de ley")
    
    # Load data
    if st.button("🔄 Cargar Datos de Interacciones"):
        with st.spinner("Cargando interacciones..."):
            df = load_all_interactions()
            if not df.empty:
                st.session_state.df = df
                st.success(f"Datos cargados: {len(df)} interacciones")
            else:
                st.error("No se encontraron datos de interacciones")
    
    # Check if data has been loaded
    if 'df' not in st.session_state or st.session_state.df.empty:
        st.info("""
        ### Instrucciones:
        1. Asegúrate de que exista el directorio 'data' con las interacciones de usuarios
        2. Haz clic en 'Cargar Datos de Interacciones'
        3. Los datos se organizarán automáticamente por:
           - Área del usuario
           - Tipo de interacción (Agregar, Eliminar, Modificar, Dudas)
           - Estructura de la ley (Libros, Títulos, Capítulos, Artículos)
        """)
        return
    
    df = st.session_state.df
    
    # FILTERS
    st.sidebar.header("🔍 Filtros")
    
    # FILTERS by Area
    available_areas = get_available_areas()
    area_filter = st.sidebar.selectbox(
        "Área:",
        options=available_areas,
        index=0
    )
    
    # Filter by Interaction Type
    interaction_types = ["TODAS"] + list(CAT.values())
    interaction_filter = st.sidebar.selectbox(
        "Tipo de Interacción:",
        options=interaction_types,
        index=0
    )
    
    # Filters by Law Structure
    available_books = ["TODOS"] + sorted(df['Libro'].dropna().unique())
    book_filter = st.sidebar.selectbox(
        "Libro:",
        options=available_books,
        index=0
    )
    
    # Filter titles based on selected book
    if book_filter != "TODOS":
        titles_df = df[df['Libro'] == book_filter]
        available_titles = ["TODOS"] + sorted(titles_df['Titulo'].dropna().unique())
    else:
        available_titles = ["TODOS"] + sorted(df['Titulo'].dropna().unique())
    
    title_filter = st.sidebar.selectbox(
        "Título:",
        options=available_titles,
        index=0
    )
    
    # Filter chapters based on selected title
    if title_filter != "TODOS":
        chapters_df = df[df['Titulo'] == title_filter]
        available_chapters = ["TODOS"] + sorted(chapters_df['Capitulo'].dropna().unique())
    else:
        if book_filter != "TODOS":
            chapters_df = df[df['Libro'] == book_filter]
            available_chapters = ["TODOS"] + sorted(chapters_df['Capitulo'].dropna().unique())
        else:
            available_chapters = ["TODOS"] + sorted(df['Capitulo'].dropna().unique())
    
    chapter_filter = st.sidebar.selectbox(
        "Capítulo:",
        options=available_chapters,
        index=0
    )
    
    # APPLY FILTERS
    df_filtered = df.copy()
    
    if area_filter != "TODAS":
        df_filtered = df_filtered[df_filtered['Area'] == area_filter]
    
    if interaction_filter != "TODAS":
        df_filtered = df_filtered[df_filtered['Categoria'] == interaction_filter]
    
    if book_filter != "TODOS":
        df_filtered = df_filtered[df_filtered['Libro'] == book_filter]
    
    if title_filter != "TODOS":
        df_filtered = df_filtered[df_filtered['Titulo'] == title_filter]
    
    if chapter_filter != "TODOS":
        df_filtered = df_filtered[df_filtered['Capitulo'] == chapter_filter]
    
    # SHOW RESULTS
    st.header("📈 Resumen de Interacciones")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Interacciones", len(df_filtered))
    
    with col2:
        st.metric("Áreas Representadas", df_filtered['Area'].nunique())
    
    with col3:
        st.metric("Tipos de Interacción", df_filtered['Categoria'].nunique())
    
    with col4:
        st.metric("Párrafos Únicos", df_filtered['Parrafo_ID'].nunique())
    
    # TABS FOR DIFFERENT VIEWS
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Datos Detallados", 
        "📊 Análisis por Área", 
        "📈 Análisis por Tipo",
        "🏛️ Análisis por Estructura"
    ])
    
    with tab1:
        st.subheader("Interacciones Detalladas")
        
        if not df_filtered.empty:
            # Show dataframe with relevant columns
            display_columns = [
                'Area', 'Categoria', 'Libro', 'Titulo', 'Capitulo', 'Articulo', 
                'Parrafo_ID', 'Texto_Parrafo', 'Informacion'#, 'Usuario'
            ]
            
            display_df = df_filtered[display_columns]
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Download option
            csv = display_df.to_csv(index=False, encoding='utf-8')
            st.download_button(
                label="📥 Descargar datos filtrados (CSV)",
                data=csv,
                file_name="interacciones_anteproyecto.csv",
                mime="text/csv"
            )
        else:
            st.info("No hay datos que coincidan con los filtros seleccionados")
    
    with tab2:
        st.subheader("Análisis por Área")
        
        if not df_filtered.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Summary by area
                area_summary = df_filtered.groupby('Area').agg({
                    'Parrafo_ID': 'count',
                    'Categoria': 'nunique',
                #    'Usuario': 'nunique'
                }).rename(columns={
                    'Parrafo_ID': 'Total_Interacciones',
                    'Categoria': 'Tipos_Interaccion',
                #    'Usuario': 'Usuarios_Unicos'
                }).reset_index()
                
                st.write("**Resumen por Área:**")
                st.dataframe(area_summary, use_container_width=True)
            
            with col2:
                # Distribution chart by area
                if len(area_summary) > 0:
                    st.write("**Distribución por Área:**")
                    chart_data = area_summary.set_index('Area')['Total_Interacciones']
                    st.bar_chart(chart_data)
    
    with tab3:
        st.subheader("Análisis por Tipo de Interacción")
        
        if not df_filtered.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Summary by type
                type_summary = df_filtered.groupby('Categoria').agg({
                    'Parrafo_ID': 'count',
                    'Area': 'nunique',
                #    'Usuario': 'nunique'
                }).rename(columns={
                    'Parrafo_ID': 'Total_Interacciones',
                    'Area': 'Areas_Unicas',
                #    'Usuario': 'Usuarios_Unicos'
                }).reset_index()
                
                st.write("**Resumen por Tipo:**")
                st.dataframe(type_summary, use_container_width=True)
            
            with col2:
                # Distribution chart by type
                if len(type_summary) > 0:
                    st.write("**Distribución por Tipo:**")
                    chart_data = type_summary.set_index('Categoria')['Total_Interacciones']
                    st.bar_chart(chart_data)
            
            # Most frequent interactions by type
            st.write("**Interacciones Más Frecuentes por Tipo:**")
            for categoria in df_filtered['Categoria'].unique():
                df_cat = df_filtered[df_filtered['Categoria'] == categoria]
                if not df_cat.empty:
                    # Show the most common interactions for this type
                    common_interactions = df_cat['Informacion'].value_counts().head(5)
                    if not common_interactions.empty:
                        st.write(f"**{categoria} - Top 5 Interacciones:**")
                        st.dataframe(
                            common_interactions.reset_index().rename(
                                columns={'index': 'Texto', 'Informacion': 'Frecuencia'}
                            ), 
                            use_container_width=True
                        )
    
    with tab4:
        st.subheader("Análisis por Estructura de la Ley")
        
        if not df_filtered.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Summary by book
                book_summary = df_filtered.groupby('Libro').agg({
                    'Parrafo_ID': 'count',
                    'Categoria': 'nunique',
                    'Area': 'nunique'
                }).rename(columns={
                    'Parrafo_ID': 'Total_Interacciones',
                    'Categoria': 'Tipos_Interaccion',
                    'Area': 'Areas_Unicas'
                }).reset_index()
                
                st.write("**Resumen por Libro:**")
                st.dataframe(book_summary, use_container_width=True)
            
            with col2:
                # Gráfico de distribución por libro
                if len(book_summary) > 0:
                    st.write("**Distribución por Libro:**")
                    chart_data = book_summary.set_index('Libro')['Total_Interacciones']
                    st.bar_chart(chart_data)
            
            # Show articles with more interactions
            st.write("**Artículos/Disposiciones con Más Interacciones:**")
            article_summary = df_filtered.groupby('Articulo').agg({
                'Parrafo_ID': 'count',
                'Categoria': lambda x: ', '.join(sorted(x.unique())),
                'Area': lambda x: ', '.join(sorted(x.unique()))
            }).rename(columns={
                'Parrafo_ID': 'Total_Interacciones',
                'Categoria': 'Tipos_Presentes',
                'Area': 'Areas_Presentes'
            }).sort_values('Total_Interacciones', ascending=False).head(10)
            
            if not article_summary.empty:
                st.dataframe(article_summary, use_container_width=True)

if __name__ == "__main__":
    main()