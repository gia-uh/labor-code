from db.milvus_client import MilvusParagraphClient
import streamlit as st
import json

@st.cache_resource
def get_milvus_client():
    return MilvusParagraphClient()

client = get_milvus_client()

def search(query: str, limit: int = 10):
    try:
        return client.search_similar_paragraphs(query, limit=limit)
    except Exception as e:
        st.error("Servicio de busqueda no disponible:")
        return []

def search_articles_with_matching_paragraphs(query: str, limit: int = 10):
    """
    Search for articles that contain paragraphs matching the query.
    Returns articles grouped by article_id with their matching paragraphs.
    """
    try:
        # Get paragraph matches
        paragraph_results = client.search_similar_paragraphs(query, limit=limit * 3)  # Get more to ensure we have enough articles
        
        # Group results by article_id
        articles_dict = {}
        
        for result in paragraph_results:
            article_id = result.get('metadata', {}).get('article_id', '')
            
            if article_id:  # Only process results that have an article_id
                if article_id not in articles_dict:
                    articles_dict[article_id] = {
                        'article_id': article_id,
                        'article_title': result.get('metadata', {}).get('article_title', ''),
                        'matching_paragraphs': [],
                        'max_similarity': 0
                    }
                
                # Add paragraph to the article
                articles_dict[article_id]['matching_paragraphs'].append({
                    'paragraph_id': result.get('paragraph_id'),
                    'content': result.get('content'),
                    'similarity_score': result.get('similarity_score'),
                    'source': result.get('source')
                })
                
                # Track the highest similarity score for this article
                if result.get('similarity_score', 0) > articles_dict[article_id]['max_similarity']:
                    articles_dict[article_id]['max_similarity'] = result.get('similarity_score', 0)
        
        # Convert to list and sort by max similarity score
        articles_list = list(articles_dict.values())
        articles_list.sort(key=lambda x: x['max_similarity'], reverse=True)
        
        # Limit the number of articles returned
        return articles_list[:limit]
    except Exception as e:
        return []
        


@st.cache_data
def load_articles_data():
    """Load articles.json data"""
    articles_path = "./jsons/anteproyecto/law/articles.json"
    try:
        with open(articles_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading articles data: {e}")
        return {}

@st.cache_data
def load_paragraphs_data():
    """Load paragraphs.json data"""
    paragraphs_path = "./jsons/anteproyecto/law/paragraphs.json"
    try:
        with open(paragraphs_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading paragraphs data: {e}")
        return {}

def get_article_content(article_id: str, articles_data: dict, paragraphs_data: dict):
    """Get full article content from paragraphs data"""
    if article_id not in articles_data:
        return None
    
    article_info = articles_data[article_id]
    begin_line = article_info.get('begin')
    end_line = article_info.get('end')
    
    if begin_line is None or end_line is None:
        return None
    
    # Extract content from paragraphs
    content_lines = []
    for line_num in range(begin_line, end_line + 1):
        line_key = str(line_num)
        if line_key in paragraphs_data:
            content_lines.append(paragraphs_data[line_key])
    
    return {
        'title': article_info.get('title', ''),
        'content': '\n'.join(content_lines),
        'begin': begin_line,
        'end': end_line
    }

def display_search_result(result, articles_data, paragraphs_data):
    """Display a single search result as a clickable container"""
    metadata = result.get('metadata', {})
    article_title = metadata.get('article_title', '')
    article_id = metadata.get('article_id', '')
    
    # Create a container for the result
    with st.container():
        # Show article title and metadata
        st.markdown(f"### {article_title}")
        
        # Show metadata in a more organized way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Source:** {result.get('source', 'N/A')}")
        with col2:
            st.markdown(f"**Similarity:** {result.get('similarity_score', 0):.3f}")
        with col3:
            if article_id:
                st.markdown(f"**Article ID:** {article_id}")
        
        # Show content preview
        content = result.get('content', '')
        if content:
            st.markdown(f"**Preview:** {content[:300]}{'...' if len(content) > 300 else ''}")
        
        # Add click handler
        if article_id and article_id in articles_data:
            if st.button(f"View Full Article {article_id}", key=f"view_{result['id']}"):
                article_content = get_article_content(article_id, articles_data, paragraphs_data)
                if article_content:
                    st.session_state[f"show_article_{result['id']}"] = article_content
                else:
                    st.error(f"Failed to load article content for ID: {article_id}")
        
        st.markdown("---")

def display_article_result(article_result, articles_data, paragraphs_data):
    """Display a single article result with its matching paragraphs"""
    article_id = article_result.get('article_id', '')
    article_title = article_result.get('article_title', '')
    matching_paragraphs = article_result.get('matching_paragraphs', [])
    max_similarity = article_result.get('max_similarity', 0)
    
    # Create a container for the result
    with st.container():
        # Show article title and metadata
        st.markdown(f"### {article_title}")
        
        # Show metadata in a more organized way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Article ID:** {article_id}")
        with col2:
            st.markdown(f"**Matching Paragraphs:** {len(matching_paragraphs)}")
        with col3:
            st.markdown(f"**Best Match Score:** {max_similarity:.3f}")
        
        # Show matching paragraphs
        st.markdown("**Matching Paragraphs:**")
        for i, paragraph in enumerate(matching_paragraphs):
            with st.expander(f"Paragraph {paragraph.get('paragraph_id', 'N/A')} (Score: {paragraph.get('similarity_score', 0):.3f})"):
                content = paragraph.get('content', '')
                if content:
                    st.markdown(content)
        
        # Add click handler to view full article
        if article_id and article_id in articles_data:
            if st.button(f"View Full Article {article_id}", key=f"view_article_{article_id}"):
                article_content = get_article_content(article_id, articles_data, paragraphs_data)
                if article_content:
                    st.session_state[f"show_article_{article_id}"] = article_content
                else:
                    st.error(f"Failed to load article content for ID: {article_id}")
        
        st.markdown("---")

def show_article_modal(article_content, result_id):
    """Show article content in a modal-like container"""
    # Create an expandable container for the article
    with st.expander(f"{article_content['title']} (Lines {article_content['begin']}-{article_content['end']})", expanded=True):
        st.markdown("---")
        
        # Display the full content with better formatting
        content_lines = article_content['content'].split('\n')
        for line in content_lines:
            if line.strip():  # Only display non-empty lines
                st.markdown(line)
        
        st.markdown("---")
        
        # Close button
        if st.button("Close Article", key=f"close_{result_id}"):
            if f"show_article_{result_id}" in st.session_state:
                del st.session_state[f"show_article_{result_id}"]
                st.rerun()

if ("logged_in" in st.session_state) and st.session_state.logged_in:

    st.title("Labor Code Search")

    # Load data
    articles_data = load_articles_data()
    paragraphs_data = load_paragraphs_data()

    # Search interface
    query = st.text_input("Search for articles, provisions, or legal concepts", placeholder="e.g., trabajo, salario, vacaciones...")
    
    # Search mode selection
    search_mode = st.radio("Search Mode:", ["Articles (recommended)", "Individual Paragraphs"], horizontal=True)
    
    # Pagination settings
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        results_per_page = st.selectbox("Results per page", [5, 10, 20, 50], index=1)
    with col2:
        page = st.number_input("Page", min_value=1, value=1, step=1)
    
    # Search button
    if st.button("Search", type="primary") or query:
        if query.strip():
            with st.spinner("Searching..."):
                # Calculate offset for pagination
                offset = (page - 1) * results_per_page
                
                if search_mode == "Articles (recommended)":
                    # Search for articles containing matching paragraphs
                    results = search_articles_with_matching_paragraphs(query, results_per_page * 3)  # Get 3 pages worth
                else:
                    # Search for individual paragraphs
                    results = search(query, results_per_page * 3)  # Get 3 pages worth
            
            if results:
                # Apply pagination to results
                start_idx = offset
                end_idx = offset + results_per_page
                paginated_results = results[start_idx:end_idx]
                
                if paginated_results:
                    if search_mode == "Articles (recommended)":
                        st.markdown(f"### Found {len(results)} articles with matching paragraphs (showing {len(paginated_results)} on page {page})")
                    else:
                        st.markdown(f"### Found {len(results)} total paragraph results (showing {len(paginated_results)} on page {page})")
                    
                    # Display paginated results
                    for i, result in enumerate(paginated_results):
                        if search_mode == "Articles (recommended)":
                            display_article_result(result, articles_data, paragraphs_data)
                            
                            # Check if this article should be shown
                            if f"show_article_{result['article_id']}" in st.session_state:
                                show_article_modal(st.session_state[f"show_article_{result['article_id']}"], result['article_id'])
                        else:
                            display_search_result(result, articles_data, paragraphs_data)
                            
                            # Check if this article should be shown
                            if f"show_article_{result['id']}" in st.session_state:
                                show_article_modal(st.session_state[f"show_article_{result['id']}"], result['id'])
                    
                    # Pagination controls
                    if len(results) > results_per_page:
                        st.markdown("---")
                        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                        
                        with col1:
                            if page > 1:
                                if st.button("Previous", key="prev_page"):
                                    st.session_state["current_page"] = page - 1
                                    st.rerun()
                        
                        with col2:
                            if page > 1:
                                st.write(f"Page {page-1}")
                        
                        with col3:
                            st.write(f"**Page {page}**")
                        
                        with col4:
                            if end_idx < len(results):
                                st.write(f"Page {page+1}")
                        
                        with col5:
                            if end_idx < len(results):
                                if st.button("Next", key="next_page"):
                                    st.session_state["current_page"] = page + 1
                                    st.rerun()
                else:
                    st.info("No results on this page. Try going to a previous page.")
            else:
                st.info("No results found. Try different keywords.")
        else:
            st.info("Please enter a search query.")