# Vector Database Service for RAG Pipeline

This service manages the vector database (ChromaDB) for the Safety Event Classification system's Retrieval-Augmented Generation (RAG) pipeline.

## Purpose

The RAG pipeline retrieves relevant department-specific policy documents from the vector database and integrates them into the safety event classification prompts. This ensures that classifications are informed by official hospital policies and procedures.

## Architecture

```
Department Policy Documents
    ↓
Text Chunking (CharacterTextSplitter)
    ↓
Embedding Generation (Vertex AI text-embedding-004)
    ↓
ChromaDB Vector Storage
    ↓
Query by Department → Retrieve Relevant Chunks
    ↓
Augment Classification Prompts
```

## Setup

### 1. Start ChromaDB

```bash
cd src/vector-db
docker-compose up -d
```

This starts ChromaDB on `localhost:8000` with persistent storage.

### 2. Prepare Policy Documents

Place your department policy documents in `input-dataset/`:
- `Medicine.txt` → Internal Medicine policies
- `Surgery.txt` → Surgery department policies
- `OB_GYN_NICU.txt` → OB/GYN/NICU policies
- `Radiology_Imaging.txt` → Radiology/Imaging policies
- `Outpatient_ER.txt` → Outpatient/ER policies

### 3. Process and Load Documents

```bash
# Start the vector-db container
./docker-shell.sh

# Inside container:
# Step 1: Chunk documents
python cli.py --chunk --chunk_type char-split

# Step 2: Generate embeddings
python cli.py --embed --chunk_type char-split

# Step 3: Load to ChromaDB
python cli.py --load --chunk_type char-split

# Step 4: Test query
python cli.py --query --chunk_type char-split --department internal_medicine
```

## Department Mappings

| File Name | Normalized Name | Display Name |
|-----------|----------------|--------------|
| Medicine.txt | internal_medicine | Internal Medicine |
| Surgery.txt | surgery | Surgery |
| OB_GYN_NICU.txt | ob_gyn_nicu | OB/GYN/NICU |
| Radiology_Imaging.txt | radiology_imaging | Radiology/Imaging |
| Outpatient_ER.txt | outpatient_er | Outpatient/ER |

## Integration with API

The API service automatically queries the vector database during classification:

1. User submits incident with department
2. RAG service retrieves top 3 relevant policy chunks for that department
3. Policy context is integrated into classification prompts
4. LLM makes informed decision based on policies + incident

### API Response Fields

When RAG is active, classification responses include:
- `rag_context_retrieved`: `true` if policy context was retrieved
- `rag_chunks_count`: Number of policy chunks retrieved

## Configuration

Environment variables:
- `CHROMADB_HOST`: ChromaDB host (default: `localhost`)
- `CHROMADB_PORT`: ChromaDB port (default: `8000`)
- `GCP_PROJECT`: Google Cloud project for embeddings
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key

## Chunking Strategies

### Character Split (Recommended)
- **Chunk size**: 500 characters
- **Overlap**: 50 characters
- **Separator**: Newline
- **Best for**: Policy documents with clear section breaks

### Recursive Split
- **Chunk size**: 500 characters
- **Overlap**: 50 characters
- **Best for**: Mixed content with varying structure

## Testing

```bash
# Test department-specific query
python cli.py --query --chunk_type char-split --department surgery

# Expected output:
# - Query text
# - Department filter applied
# - Top 5 relevant policy chunks
```

## Troubleshooting

### ChromaDB Connection Error
```
Error: Could not connect to ChromaDB
```
**Solution**: Ensure ChromaDB is running:
```bash
docker-compose up -d
docker ps | grep chroma
```

### No Results for Department
```
Warning: No policy context found for department
```
**Solution**: Verify department name matches normalized format:
```python
# Valid departments
"internal_medicine", "surgery", "ob_gyn_nicu", 
"radiology_imaging", "outpatient_er"
```

### Embedding Generation Fails
```
Error: API Error during embedding generation
```
**Solution**: Check GCP credentials and API quota:
```bash
echo $GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default print-access-token
```

## Collection Structure

Collection name: `safety-policies-char-split`

**Document Structure:**
```json
{
  "id": "hash-index",
  "document": "Policy text chunk...",
  "metadata": {
    "department": "internal_medicine",
    "display_name": "Internal Medicine"
  },
  "embedding": [0.123, 0.456, ...]
}
```

## Performance

- **Embedding dimension**: 256 (optimized for speed)
- **Embedding model**: `text-embedding-004` (Vertex AI)
- **Batch size**: 100 chunks per API call
- **Query time**: ~200-500ms per retrieval
- **Storage**: ~10MB per 1000 documents

## Maintenance

### Update Policies

1. Update text files in `input-dataset/`
2. Re-run chunking, embedding, and loading steps
3. Old data is automatically replaced

### Clear Database

```bash
# Inside container
python cli.py --load --chunk_type char-split
# (This automatically deletes and recreates the collection)
```

### Backup Database

```bash
# Backup ChromaDB data
cp -r chroma-data chroma-data-backup-$(date +%Y%m%d)
```

## References

This implementation follows patterns from:
- `references/cheese-app-v2/src/vector-db/` - ChromaDB integration
- `references/llm-rag/` - RAG pipeline architecture
