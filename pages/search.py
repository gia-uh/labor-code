from db.milvus_client import MilvusParagraphClient
import streamlit as st
import json

client = MilvusParagraphClient()

def search(query: str, limit: int = 10):
    return client.search_similar_paragraphs(query, limit=limit)

def load_articles_data():
    """Load articles.json data"""
    articles_path = "./jsons/anteproyecto/law/articles.json"
    try:
        with open(articles_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading articles data: {e}")
        return {}

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
        
        # Debug: Show all metadata
        with st.expander("🔍 Debug: Show Metadata", expanded=False):
            st.json(metadata)
        
        # Show content preview
        content = result.get('content', '')
        if content:
            st.markdown(f"**Preview:** {content[:300]}{'...' if len(content) > 300 else ''}")
        
        # Add click handler
        if article_id and article_id in articles_data:
            if st.button(f"📖 View Full Article {article_id}", key=f"view_{result['id']}"):
                article_content = get_article_content(article_id, articles_data, paragraphs_data)
                if article_content:
                    st.session_state[f"show_article_{result['id']}"] = article_content
                else:
                    st.error(f"Failed to load article content for ID: {article_id}")
        else:
            # Debug information
            st.info(f"Article ID not available for this result. Found article_id: '{article_id}', Available keys: {list(articles_data.keys())[:10]}...")
        
        st.markdown("---")

def show_article_modal(article_content, result_id):
    """Show article content in a modal-like container"""
    # Create an expandable container for the article
    with st.expander(f"📄 {article_content['title']} (Lines {article_content['begin']}-{article_content['end']})", expanded=True):
        st.markdown("---")
        
        # Display the full content with better formatting
        content_lines = article_content['content'].split('\n')
        for line in content_lines:
            if line.strip():  # Only display non-empty lines
                st.markdown(line)
        
        st.markdown("---")
        
        # Close button
        if st.button("❌ Close Article", key=f"close_{result_id}"):
            if f"show_article_{result_id}" in st.session_state:
                del st.session_state[f"show_article_{result_id}"]
                st.rerun()

if ("logged_in" in st.session_state) and st.session_state.logged_in:

    st.title("Labor Code Search")

    # Load data
    articles_data = load_articles_data()
    paragraphs_data = load_paragraphs_data()

    # Debug: Show data loading status
    with st.expander("🔧 Debug: Data Loading Status", expanded=False):
        st.write(f"Articles loaded: {len(articles_data)} articles")
        st.write(f"Paragraphs loaded: {len(paragraphs_data)} paragraphs")
        if articles_data:
            st.write("Sample article keys:", list(articles_data.keys())[:5])
            st.write("Sample article data:", {k: v for k, v in list(articles_data.items())[:2]})
        
        # Test article loading
        if st.button("🧪 Test Article Loading (Article 1)"):
            test_article = get_article_content("1", articles_data, paragraphs_data)
            if test_article:
                st.success("✅ Article 1 loaded successfully!")
                st.write("Title:", test_article['title'])
                st.write("Lines:", f"{test_article['begin']}-{test_article['end']}")
                st.write("Content preview:", test_article['content'][:200] + "...")
            else:
                st.error("❌ Failed to load Article 1")

    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Search for articles, provisions, or legal concepts", placeholder="e.g., trabajo, salario, vacaciones...")
    with col2:
        limit = st.number_input("Results", min_value=1, max_value=50, value=10)

    # Search button
    if st.button("Search", type="primary") or query:
        if query.strip():
            with st.spinner("Searching..."):
                results = search(query, limit)
            
            if results:
                st.markdown(f"### Found {len(results)} results")
                
                # Display results
                for i, result in enumerate(results):
                    display_search_result(result, articles_data, paragraphs_data)
                    
                    # Check if this article should be shown
                    if f"show_article_{result['id']}" in st.session_state:
                        show_article_modal(st.session_state[f"show_article_{result['id']}"], result['id'])
            else:
                st.info("No results found. Try different keywords.")
        else:
            st.info("Please enter a search query.")