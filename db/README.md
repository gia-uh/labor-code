# Milvus Database for Labor Code Paragraphs

This directory contains the Milvus vector database implementation for storing and searching paragraphs from the labor code documents.

## Overview

The system stores paragraphs from two main sources:
- **paragraphs.json**: Main content paragraphs with hierarchical metadata (books, titles, chapters, sections, articles)
- **preamble.json**: Preamble paragraphs with special marking

Each paragraph is stored with:
- Vector embedding for semantic search
- Complete metadata from the hierarchical structure
- Source identification (paragraphs vs preamble)

## Files

- `milvus_client.py`: Main Milvus client with CRUD operations
- `setup_database.py`: Database initialization and population script
- `query_examples.py`: Example queries and interactive search
- `requirements.txt`: Python dependencies
- `README.md`: This documentation

## Installation

1. Install dependencies:
```bash
cd db
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python setup_database.py
```

## Usage

### Basic Search
```python
from milvus_client import MilvusParagraphClient

client = MilvusParagraphClient()

# Search for similar paragraphs
results = client.search_similar_paragraphs("trabajo digno", limit=5)

# Search only in main paragraphs (exclude preamble)
results = client.search_similar_paragraphs("derechos laborales", 
                                         limit=3, 
                                         source_filter="paragraphs")

# Search only in preamble
results = client.search_similar_paragraphs("constitución", 
                                         limit=3, 
                                         source_filter="preamble")

client.close()
```

### Get Specific Paragraph
```python
# Get paragraph by ID
paragraph = client.get_paragraph_by_id("10")
if paragraph:
    print(paragraph['content'])
    print(paragraph['metadata'])
```

### Collection Statistics
```python
stats = client.get_collection_stats()
print(f"Total paragraphs: {stats['total_entities']}")
```

## Collection Schema

The `anteproy_paragraphs` collection contains the following fields:

- `id`: Auto-generated primary key
- `paragraph_id`: Original paragraph ID from JSON
- `content`: Paragraph text content
- `embedding`: 768-dimensional vector embedding
- `source`: "paragraphs" or "preamble"
- `book_id`, `book_title`: Book metadata
- `title_id`, `title_title`: Title metadata
- `chapter_id`, `chapter_title`: Chapter metadata
- `section_id`, `section_title`: Section metadata
- `article_id`, `article_title`: Article metadata
- `provision_id`, `provision_title`: Provision metadata
- `provision_block_id`, `provision_block_title`: Provision block metadata

## Metadata Mapping

The system automatically maps paragraph IDs to their hierarchical metadata:

1. **For paragraphs.json**: Maps to books, titles, chapters, sections, and articles based on begin/end ranges
2. **For provisions**: Maps to provisions and provision blocks based on begin/end ranges
3. **For preamble.json**: All metadata fields are empty, source is marked as "preamble"

## Examples

Run the example queries:
```bash
python query_examples.py
```

This will demonstrate various search capabilities and provide an interactive search interface.

## Database Location

The Milvus Lite database is stored locally as `./milvus_lite.db` in the db directory.

## Performance Notes

- Embeddings are generated using OpenAI-compatible service with `text-embedding-nomic-embed-text-v2-moe` model (768 dimensions)
- Search uses cosine similarity with IVF_FLAT index
- Data is inserted in batches of 100 for efficiency
- Embeddings are generated in batches of 100 for API efficiency
- Collection is automatically loaded into memory for fast queries
