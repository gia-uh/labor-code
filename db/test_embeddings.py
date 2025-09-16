#!/usr/bin/env python3
"""
Test script to verify the OpenAI-compatible embedding service works correctly.
"""

from openai import OpenAI


def test_embedding_service():
    """Test the embedding service with sample text."""
    print("Testing OpenAI-compatible embedding service...")
    
    # Initialize client with custom base URL and no API key
    client = OpenAI(base_url="http://10.6.125.217:8080/v1", api_key='')
    
    # Test embeddings
    test_texts = [
        "Embed this string for me!",
        "Also embed this one!",
        "This is a test of the labor code paragraph embedding system."
    ]
    
    try:
        print("Generating embeddings...")
        embed_response = client.embeddings.create(
            model="text-embedding-nomic-embed-text-v2-moe",
            input=test_texts
        )
        
        print(f"Successfully generated {len(embed_response.data)} embeddings")
        print(f"Embedding dimension: {len(embed_response.data[0].embedding)}")
        
        for i, data in enumerate(embed_response.data):
            print(f"Text {i+1}: {test_texts[i][:50]}...")
            print(f"Embedding length: {len(data.embedding)}")
            print(f"First 5 values: {data.embedding[:5]}")
            print()
        
        return True
        
    except Exception as e:
        print(f"Error testing embedding service: {e}")
        return False


if __name__ == "__main__":
    success = test_embedding_service()
    if success:
        print("✅ Embedding service test passed!")
    else:
        print("❌ Embedding service test failed!")
