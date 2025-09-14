#!/usr/bin/env python3
"""
Setup script for the Milvus database.
This script initializes the database and populates it with paragraph data.
"""

import os
import streamlit as st
from pprint import pprint
import sys
from milvus_client import MilvusParagraphClient


def main():
    """Main setup function."""
    print("Setting up Milvus database for labor code paragraphs...")
    
    # Check if data files exist
    data_path = st.secrets["dirs"]["project"]["law"]
    required_files = [
        "paragraphs.json",
        "preamble.json", 
        "articles.json",
        "books.json",
        "chapters.json",
        "sections.json",
        "titles.json",
        "provisions.json",
        "provisions_blocks.json"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(data_path, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"Error: Missing required files: {missing_files}")
        print(f"Please ensure all JSON files are present in {data_path}")
        sys.exit(1)
    
    try:
        # Initialize client
        print("Initializing Milvus client...")
        client = MilvusParagraphClient()
        
        # Insert all paragraphs
        print("Inserting paragraphs into database...")
        client.insert_paragraphs()
        
        # Get and display stats
        stats = client.get_collection_stats()
        print(f"\nDatabase setup complete!")
        print(f"Collection: {stats.get('collection_name', 'N/A')}")
        print(f"Total paragraphs: {stats.get('total_entities', 0)}")
        
        # Test search functionality
        print("\nTesting search functionality...")
        test_queries = [
            "trabajo digno",
            "derechos laborales", 
            "contrato de trabajo"
        ]
        
        for query in test_queries:
            print(f"\nSearching for: '{query}'")
            results = client.search_similar_paragraphs(query, limit=3)
            print(f"Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['similarity_score']:.4f}")
                print(f"     Source: {result['source']}")
                print(f"     Content: {result['content'][:80]}...")
                pprint(result)
        
        client.close()
        print("\nSetup completed successfully!")
        
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
