#!/usr/bin/env python3
"""
Example queries for the Milvus paragraph database.
Demonstrates various search and retrieval operations.
"""

from milvus_client import MilvusParagraphClient


def example_searches():
    """Demonstrate various search capabilities."""
    client = MilvusParagraphClient()
    
    print("=== Milvus Paragraph Database Query Examples ===\n")
    
    # Example 1: General semantic search
    print("1. General semantic search for 'trabajo digno':")
    results = client.search_similar_paragraphs("trabajo digno", limit=5)
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Source: {result['source']}")
        print(f"      Content: {result['content'][:100]}...")
        if result['metadata']['article_title']:
            print(f"      Article: {result['metadata']['article_title']}")
        print()
    
    # Example 2: Search only in paragraphs (exclude preamble)
    print("2. Search only in main paragraphs (excluding preamble):")
    results = client.search_similar_paragraphs("derechos laborales", limit=3, source_filter="paragraphs")
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Content: {result['content'][:100]}...")
        print(f"      Chapter: {result['metadata']['chapter_title']}")
        print()
    
    # Example 3: Search only in preamble
    print("3. Search only in preamble:")
    results = client.search_similar_paragraphs("constitución", limit=3, source_filter="preamble")
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Content: {result['content'][:100]}...")
        print()
    
    # Example 4: Get specific paragraph by ID
    print("4. Get specific paragraph by ID (paragraph 10):")
    paragraph = client.get_paragraph_by_id("10")
    if paragraph:
        print(f"   Content: {paragraph['content']}")
        print(f"   Source: {paragraph['source']}")
        print(f"   Article: {paragraph['metadata']['article_title']}")
    else:
        print("   Paragraph not found")
    print()
    
    # Example 5: Search for specific legal concepts
    print("5. Search for 'contrato de trabajo':")
    results = client.search_similar_paragraphs("contrato de trabajo", limit=3)
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Content: {result['content'][:100]}...")
        print(f"      Section: {result['metadata']['section_title']}")
        print()
    
    # Example 6: Search for workplace safety
    print("6. Search for workplace safety concepts:")
    results = client.search_similar_paragraphs("seguridad laboral", limit=3)
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Content: {result['content'][:100]}...")
        print(f"      Title: {result['metadata']['title_title']}")
        print()
    
    # Example 7: Search for union rights
    print("7. Search for union and collective rights:")
    results = client.search_similar_paragraphs("organizaciones sindicales", limit=3)
    for i, result in enumerate(results, 1):
        print(f"   {i}. Score: {result['similarity_score']:.4f}")
        print(f"      Content: {result['content'][:100]}...")
        print(f"      Book: {result['metadata']['book_title']}")
        print()
    
    # Get collection statistics
    print("8. Collection statistics:")
    stats = client.get_collection_stats()
    print(f"   Total paragraphs: {stats.get('total_entities', 0)}")
    print(f"   Collection name: {stats.get('collection_name', 'N/A')}")
    
    client.close()


def interactive_search():
    """Interactive search interface."""
    client = MilvusParagraphClient()
    
    print("\n=== Interactive Search ===")
    print("Enter search queries (type 'quit' to exit):")
    
    while True:
        query = input("\nSearch query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        # Ask for source filter
        source_filter = input("Source filter (paragraphs/preamble/any): ").strip().lower()
        if source_filter not in ['paragraphs', 'preamble']:
            source_filter = None
        
        # Ask for limit
        try:
            limit = int(input("Number of results (default 5): ") or "5")
        except ValueError:
            limit = 5
        
        # Perform search
        results = client.search_similar_paragraphs(query, limit=limit, source_filter=source_filter)
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result['similarity_score']:.4f}")
            print(f"   Source: {result['source']}")
            print(f"   Content: {result['content']}")
            print(f"   Metadata:")
            for key, value in result['metadata'].items():
                if value:
                    print(f"     {key}: {value}")
    
    client.close()


if __name__ == "__main__":
    # Run example searches
    example_searches()
    
    # Optionally run interactive search
    run_interactive = input("\nRun interactive search? (y/n): ").strip().lower()
    if run_interactive in ['y', 'yes']:
        interactive_search()
