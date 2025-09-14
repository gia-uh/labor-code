"""
Milvus client for managing the anteproy_paragraphs collection.
Handles CRUD operations for paragraphs with their metadata.
"""

import json
import os
import streamlit as st 
from typing import List, Dict, Any, Optional
from pymilvus import (
    connections, Collection, CollectionSchema, FieldSchema, DataType,
    utility
)
from openai import OpenAI


class MilvusParagraphClient:
    """Client for managing paragraphs in Milvus vector database."""
    
    def __init__(self, collection_name: str = "anteproy_paragraphs", 
                 data_path: str = st.secrets["dirs"]["project"]["law"],
                 embedding_base_url: str = st.secrets["embedding"]["base_url"],
                 embedding_model: str = st.secrets["embedding"]["model"]):
        """
        Initialize the Milvus client.
        
        Args:
            collection_name: Name of the collection to create/use
            data_path: Path to the JSON data files
            embedding_base_url: Base URL for the OpenAI-compatible embedding service
            embedding_model: Model name for embeddings
        """
        self.collection_name = collection_name
        self.data_path = data_path
        self.collection = None
        self.embedding_client = None
        self.embedding_model = embedding_model
        
        # Connect to Milvus Lite
        self._connect()
        
        # Initialize embedding client
        self._init_embedding_client(embedding_base_url)
        
        # Create or get collection
        self._setup_collection()
    
    def _connect(self):
        """Connect to Milvus Lite."""
        try:
            connections.connect(
                alias="default",
                uri=st.secrets["dbs"]["milvus"]  # Local Milvus Lite database
            )
            print("Connected to Milvus Lite successfully")
        except Exception as e:
            print(f"Failed to connect to Milvus: {e}")
            raise
    
    def _init_embedding_client(self, base_url: str):
        """Initialize the OpenAI-compatible embedding client."""
        try:
            self.embedding_client = OpenAI(base_url=base_url, api_key='', timeout=10.0)
            # Test the connection with a simple request
            test_response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=["test"]
            )
            print("Embedding client initialized and tested successfully")
        except Exception as e:
            print(f"Failed to initialize embedding client: {e}")
            print("Warning: Embedding service is not accessible. The system will use zero vectors as fallback.")
            self.embedding_client = None
    
    def _create_schema(self) -> CollectionSchema:
        """Create the collection schema for paragraphs."""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="paragraph_id", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # OpenAI embedding dimension
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=20),  # "paragraphs" or "preamble"
            FieldSchema(name="book_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="book_title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="title_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="title_title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="chapter_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="chapter_title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="section_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="section_title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="article_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="article_title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="provision_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="provision_title", dtype=DataType.VARCHAR, max_length=200),
            FieldSchema(name="provision_block_id", dtype=DataType.VARCHAR, max_length=10),
            FieldSchema(name="provision_block_title", dtype=DataType.VARCHAR, max_length=200),
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="Collection for storing paragraphs with metadata from labor code"
        )
        return schema
    
    def _setup_collection(self):
        """Create or get the collection."""
        try:
            if utility.has_collection(self.collection_name):
                print(f"Collection {self.collection_name} already exists")
                self.collection = Collection(self.collection_name)
            else:
                print(f"Creating collection {self.collection_name}")
                schema = self._create_schema()
                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema
                )
                
                # Create index on embedding field
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params
                )
                print("Index created successfully")
            
            # Load collection into memory
            self.collection.load()
            print("Collection loaded into memory")
            
        except Exception as e:
            print(f"Failed to setup collection: {e}")
            raise
    
    def _load_json_data(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from file."""
        file_path = os.path.join(self.data_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load {filename}: {e}")
            return {}
    
    def _get_metadata_for_paragraph(self, paragraph_id: str, metadata: Dict[str, Any]) -> Dict[str, str]:
        """Get metadata for a specific paragraph ID."""
        result = {}
        
        # Check each metadata type
        for meta_type, meta_data in metadata.items():
            if meta_type in ['books', 'titles', 'chapters', 'sections', 'articles']:
                for meta_id, meta_info in meta_data.items():
                    if meta_info.get('begin') <= int(paragraph_id) <= meta_info.get('end'):
                        result[f"{meta_type[:-1]}_id"] = meta_id
                        result[f"{meta_type[:-1]}_title"] = meta_info.get('title', '')
                        break
        
        return result
    
    def _get_provision_metadata_for_paragraph(self, paragraph_id: str, 
                                            provisions: Dict[str, Any], 
                                            provision_blocks: Dict[str, Any]) -> Dict[str, str]:
        """Get provision metadata for a specific paragraph ID."""
        result = {}
        
        # Check provisions
        for prov_id, prov_info in provisions.items():
            if prov_info.get('begin') <= int(paragraph_id) <= prov_info.get('end'):
                result['provision_id'] = prov_id
                result['provision_title'] = prov_info.get('title', '')
                break
        
        # Check provision blocks
        for block_id, block_info in provision_blocks.items():
            if block_info.get('begin') <= int(paragraph_id) <= block_info.get('end'):
                result['provision_block_id'] = block_id
                result['provision_block_title'] = block_info.get('title', '')
                break
        
        return result
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI-compatible service."""
        if self.embedding_client is None:
            print("Embedding service not available, using zero vector")
            return [0.0] * 768  # Return zero vector as fallback
        
        try:
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Failed to generate embedding: {e}")
            return [0.0] * 768  # Return zero vector as fallback
    
    def _generate_batch_embeddings(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches."""
        embeddings = []
        
        if self.embedding_client is None:
            print("Embedding service not available, using zero vectors for all texts")
            return [[0.0] * 768 for _ in texts]
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = self.embedding_client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)
                print(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            except Exception as e:
                print(f"Failed to generate embeddings for batch {i//batch_size + 1}: {e}")
                # Add zero vectors as fallback
                embeddings.extend([[0.0] * 768 for _ in batch])
        
        return embeddings
    
    def insert_paragraphs(self):
        """Insert all paragraphs from JSON files into Milvus."""
        print("Starting paragraph insertion...")
        
        # Load all metadata
        books = self._load_json_data('books.json')
        titles = self._load_json_data('titles.json')
        chapters = self._load_json_data('chapters.json')
        sections = self._load_json_data('sections.json')
        articles = self._load_json_data('articles.json')
        provisions = self._load_json_data('provisions.json')
        provision_blocks = self._load_json_data('provisions_blocks.json')
        
        # Load paragraphs
        paragraphs = self._load_json_data('paragraphs.json')
        preamble = self._load_json_data('preamble.json')
        
        # Prepare data for insertion
        data_to_insert = []
        
        # Process paragraphs from paragraphs.json
        print("Processing paragraphs from paragraphs.json...")
        
        # Prepare all content for batch embedding
        all_content = []
        content_to_para_id = {}
        
        for para_id, content in paragraphs.items():
            all_content.append(content)
            content_to_para_id[content] = para_id
        
        # Generate embeddings in batches
        print("Generating embeddings for paragraphs...")
        embeddings = self._generate_batch_embeddings(all_content)
        
        for content, embedding in zip(all_content, embeddings):
            para_id = content_to_para_id[content]
            
            # Get metadata
            metadata = self._get_metadata_for_paragraph(para_id, {
                'books': books, 'titles': titles, 'chapters': chapters, 
                'sections': sections, 'articles': articles
            })
            
            # Get provision metadata
            provision_metadata = self._get_provision_metadata_for_paragraph(
                para_id, provisions, provision_blocks
            )
            
            # Prepare record
            record = {
                'paragraph_id': para_id,
                'content': content,
                'embedding': embedding,
                'source': 'paragraphs',
                'book_id': metadata.get('book_id', ''),
                'book_title': metadata.get('book_title', ''),
                'title_id': metadata.get('title_id', ''),
                'title_title': metadata.get('title_title', ''),
                'chapter_id': metadata.get('chapter_id', ''),
                'chapter_title': metadata.get('chapter_title', ''),
                'section_id': metadata.get('section_id', ''),
                'section_title': metadata.get('section_title', ''),
                'article_id': metadata.get('article_id', ''),
                'article_title': metadata.get('article_title', ''),
                'provision_id': provision_metadata.get('provision_id', ''),
                'provision_title': provision_metadata.get('provision_title', ''),
                'provision_block_id': provision_metadata.get('provision_block_id', ''),
                'provision_block_title': provision_metadata.get('provision_block_title', ''),
            }
            
            data_to_insert.append(record)
        
        # Process paragraphs from preamble.json
        print("Processing paragraphs from preamble.json...")
        preamble_content = list(preamble.values())
        preamble_embeddings = self._generate_batch_embeddings(preamble_content)
        
        for (para_id, content), embedding in zip(preamble.items(), preamble_embeddings):
            # Prepare record for preamble
            record = {
                'paragraph_id': para_id,
                'content': content,
                'embedding': embedding,
                'source': 'preamble',
                'book_id': '',
                'book_title': '',
                'title_id': '',
                'title_title': '',
                'chapter_id': '',
                'chapter_title': '',
                'section_id': '',
                'section_title': '',
                'article_id': '',
                'article_title': '',
                'provision_id': '',
                'provision_title': '',
                'provision_block_id': '',
                'provision_block_title': '',
            }
            
            data_to_insert.append(record)
        
        # Insert data in batches
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(data_to_insert), batch_size):
            batch = data_to_insert[i:i + batch_size]
            
            try:
                # Convert to format expected by Milvus - list of lists
                insert_data = [
                    [record['paragraph_id'] for record in batch],
                    [record['content'] for record in batch],
                    [record['embedding'] for record in batch],
                    [record['source'] for record in batch],
                    [record['book_id'] for record in batch],
                    [record['book_title'] for record in batch],
                    [record['title_id'] for record in batch],
                    [record['title_title'] for record in batch],
                    [record['chapter_id'] for record in batch],
                    [record['chapter_title'] for record in batch],
                    [record['section_id'] for record in batch],
                    [record['section_title'] for record in batch],
                    [record['article_id'] for record in batch],
                    [record['article_title'] for record in batch],
                    [record['provision_id'] for record in batch],
                    [record['provision_title'] for record in batch],
                    [record['provision_block_id'] for record in batch],
                    [record['provision_block_title'] for record in batch],
                ]
                
                self.collection.insert(insert_data)
                total_inserted += len(batch)
                print(f"Inserted batch {i//batch_size + 1}, total: {total_inserted}")
                
            except Exception as e:
                print(f"Failed to insert batch {i//batch_size + 1}: {e}")
        
        # Flush to ensure data is written
        self.collection.flush()
        print(f"Successfully inserted {total_inserted} paragraphs")
    
    def search_similar_paragraphs(self, query: str, limit: int = 10, 
                                source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar paragraphs using vector similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            source_filter: Filter by source ('paragraphs' or 'preamble')
        
        Returns:
            List of similar paragraphs with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self._generate_embedding(query)
            
            # Prepare search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            # Build filter expression if source filter is provided
            filter_expr = None
            if source_filter:
                filter_expr = f'source == "{source_filter}"'
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=filter_expr,
                output_fields=[
                    "paragraph_id", "content", "source", "book_title", 
                    "title_title", "chapter_title", "section_title", 
                    "article_id", "article_title", "provision_title", "provision_block_title"
                ]
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    result = {
                        'id': hit.id,
                        'paragraph_id': hit.entity.get('paragraph_id'),
                        'content': hit.entity.get('content'),
                        'source': hit.entity.get('source'),
                        'similarity_score': hit.score,
                        'metadata': {
                            'book_title': hit.entity.get('book_title'),
                            'title_title': hit.entity.get('title_title'),
                            'chapter_title': hit.entity.get('chapter_title'),
                            'section_title': hit.entity.get('section_title'),
                            'article_id': hit.entity.get('article_id'),
                            'article_title': hit.entity.get('article_title'),
                            'provision_title': hit.entity.get('provision_title'),
                            'provision_block_title': hit.entity.get('provision_block_title'),
                        }
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
    
    def get_paragraph_by_id(self, paragraph_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific paragraph by its ID.
        
        Args:
            paragraph_id: The paragraph ID to search for
        
        Returns:
            Paragraph data if found, None otherwise
        """
        try:
            results = self.collection.query(
                expr=f'paragraph_id == "{paragraph_id}"',
                output_fields=[
                    "paragraph_id", "content", "source", "book_title", 
                    "title_title", "chapter_title", "section_title", 
                    "article_title", "provision_title", "provision_block_title"
                ]
            )
            
            if results:
                result = results[0]
                return {
                    'id': result.get('id'),
                    'paragraph_id': result.get('paragraph_id'),
                    'content': result.get('content'),
                    'source': result.get('source'),
                    'metadata': {
                        'book_title': result.get('book_title'),
                        'title_title': result.get('title_title'),
                        'chapter_title': result.get('chapter_title'),
                        'section_title': result.get('section_title'),
                        'article_title': result.get('article_title'),
                        'provision_title': result.get('provision_title'),
                        'provision_block_title': result.get('provision_block_title'),
                    }
                }
            return None
            
        except Exception as e:
            print(f"Failed to get paragraph by ID: {e}")
            return None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            # Get the number of entities in the collection
            num_entities = self.collection.num_entities
            return {
                'total_entities': num_entities,
                'collection_name': self.collection_name
            }
        except Exception as e:
            print(f"Failed to get collection stats: {e}")
            return {}
    
    def close(self):
        """Close the connection."""
        try:
            connections.disconnect("default")
            print("Disconnected from Milvus")
        except Exception as e:
            print(f"Failed to disconnect: {e}")


if __name__ == "__main__":
    # Example usage
    client = MilvusParagraphClient()
    
    # Insert all paragraphs
    client.insert_paragraphs()
    
    # Example search
    results = client.search_similar_paragraphs("trabajo digno", limit=5)
    print(f"Found {len(results)} similar paragraphs")
    for result in results:
        print(f"Score: {result['similarity_score']:.4f}")
        print(f"Content: {result['content'][:100]}...")
        print("---")
    
    # Get collection stats
    stats = client.get_collection_stats()
    print(f"Collection stats: {stats}")
    
    client.close()
