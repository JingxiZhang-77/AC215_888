"""
Vector Database CLI for Safety Event Classification RAG Pipeline

Processes department policy documents into embeddings and loads them into ChromaDB.
"""

import os
import argparse
import pandas as pd
import glob
import hashlib
import chromadb
import time

# Vertex AI
from google import genai
from google.genai import types
from google.genai import errors

# Langchain
from langchain_text_splitters import CharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Setup
GCP_PROJECT = os.environ.get("GCP_PROJECT", "apcomp215-group88")
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-2.0-flash-exp"
INPUT_FOLDER = "input-dataset"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8000"))

# Initialize the LLM Client
llm_client = genai.Client(
    vertexai=True, project=GCP_PROJECT, location=GCP_LOCATION
)

# Department mappings
DEPARTMENT_MAPPINGS = {
    "Medicine": {
        "normalized_name": "internal_medicine",
        "display_name": "Internal Medicine"
    },
    "Surgery": {
        "normalized_name": "surgery",
        "display_name": "Surgery"
    },
    "OB_GYN_NICU": {
        "normalized_name": "ob_gyn_nicu",
        "display_name": "OB/GYN/NICU"
    },
    "Radiology_Imaging": {
        "normalized_name": "radiology_imaging",
        "display_name": "Radiology/Imaging"
    },
    "Outpatient_ER": {
        "normalized_name": "outpatient_er",
        "display_name": "Outpatient/ER"
    }
}


def generate_query_embedding(query):
    """Generate embedding for a query string"""
    kwargs = {
        "output_dimensionality": EMBEDDING_DIMENSION
    }
    response = llm_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(**kwargs)
    )
    return response.embeddings[0].values


def generate_text_embeddings(chunks, dimensionality: int = 256, batch_size=100, max_retries=5, retry_delay=5):
    """Generate embeddings for text chunks with retry logic"""
    all_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        retry_count = 0
        while retry_count <= max_retries:
            try:
                kwargs = {
                    "output_dimensionality": dimensionality
                }
                response = llm_client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(**kwargs)
                )
                
                batch_embeddings = [embedding.values for embedding in response.embeddings]
                all_embeddings.extend(batch_embeddings)
                print(f"Processed batch {i//batch_size + 1}, total embeddings: {len(all_embeddings)}")
                break

            except errors.APIError as e:
                retry_count += 1
                if retry_count > max_retries:
                    print(f"Max retries exceeded for batch starting at index {i}")
                    raise e
                
                wait_time = retry_delay * (2 ** (retry_count - 1))
                print(f"API Error: {e}. Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
                time.sleep(wait_time)

    return all_embeddings


def load_text_embeddings(df, collection, batch_size=500):
    """Load embeddings into ChromaDB collection"""
    
    # Generate ids
    df["id"] = df.index.astype(str)
    hashed_dept = df["department"].apply(
        lambda x: hashlib.sha256(x.encode()).hexdigest()[:16]
    )
    df["id"] = hashed_dept + "-" + df["id"]

    # Get department metadata
    dept_file = df["department"].tolist()[0]
    metadata = {
        "department": DEPARTMENT_MAPPINGS[dept_file]["normalized_name"],
        "display_name": DEPARTMENT_MAPPINGS[dept_file]["display_name"]
    }

    # Process data in batches
    total_inserted = 0
    for i in range(0, df.shape[0], batch_size):
        batch = df.iloc[i:i+batch_size].copy().reset_index(drop=True)

        ids = batch["id"].tolist()
        documents = batch["chunk"].tolist()
        metadatas = [metadata for _ in batch["department"].tolist()]
        embeddings = batch["embedding"].tolist()

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        total_inserted += len(batch)
        print(f"Inserted {total_inserted} items...")

    print(f"Finished inserting {total_inserted} items into collection '{collection.name}'")


def chunk(method="char-split"):
    """Chunk department policy documents"""
    print("=== Chunking Policy Documents ===")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Get the list of text files
    text_files = glob.glob(os.path.join(INPUT_FOLDER, "*.txt"))
    print(f"Number of files to process: {len(text_files)}")

    for text_file in text_files:
        print(f"\nProcessing file: {text_file}")
        filename = os.path.basename(text_file)
        department_name = filename.split(".")[0]

        with open(text_file) as f:
            input_text = f.read()

        text_chunks = None
        if method == "char-split":
            chunk_size = 500
            chunk_overlap = 50
            text_splitter = CharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap, 
                separator='\n', 
                strip_whitespace=True
            )
            text_chunks = text_splitter.create_documents([input_text])
            text_chunks = [doc.page_content for doc in text_chunks]
            print(f"Number of chunks: {len(text_chunks)}")

        elif method == "recursive-split":
            chunk_size = 500
            chunk_overlap = 50
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            text_chunks = text_splitter.create_documents([input_text])
            text_chunks = [doc.page_content for doc in text_chunks]
            print(f"Number of chunks: {len(text_chunks)}")

        if text_chunks is not None:
            data_df = pd.DataFrame(text_chunks, columns=["chunk"])
            data_df["department"] = department_name
            print(f"Shape: {data_df.shape}")
            print(data_df.head())

            jsonl_filename = os.path.join(
                OUTPUT_FOLDER, f"chunks-{method}-{department_name}.jsonl"
            )
            with open(jsonl_filename, "w") as json_file:
                json_file.write(data_df.to_json(orient='records', lines=True))
            print(f"Saved: {jsonl_filename}")


def embed(method="char-split"):
    """Generate embeddings for chunked documents"""
    print("=== Generating Embeddings ===")

    jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"chunks-{method}-*.jsonl"))
    print(f"Number of files to process: {len(jsonl_files)}")

    for jsonl_file in jsonl_files:
        print(f"\nProcessing file: {jsonl_file}")

        data_df = pd.read_json(jsonl_file, lines=True)
        print(f"Shape: {data_df.shape}")
        print(data_df.head())

        chunks = data_df["chunk"].values.tolist()
        embeddings = generate_text_embeddings(chunks, EMBEDDING_DIMENSION, batch_size=100)
        data_df["embedding"] = embeddings

        time.sleep(2)

        print(f"Final shape: {data_df.shape}")
        print(data_df.head())

        jsonl_filename = jsonl_file.replace("chunks-", "embeddings-")
        with open(jsonl_filename, "w") as json_file:
            json_file.write(data_df.to_json(orient='records', lines=True))
        print(f"Saved: {jsonl_filename}")


def load(method="char-split"):
    """Load embeddings into ChromaDB"""
    print("=== Loading to ChromaDB ===")
    print(f"Connecting to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}")

    # Clear cache
    chromadb.api.client.SharedSystemClient.clear_system_cache()

    # Connect to ChromaDB
    try:
        client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
        client.heartbeat()
        print(f"✅ Successfully connected to ChromaDB")
    except Exception as e:
        print(f"❌ ERROR: Cannot connect to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}")
        print(f"   Error: {e}")
        print(f"\n💡 Make sure ChromaDB is running:")
        print(f"   docker ps | grep chromadb")
        print(f"\n   If not running, start it with:")
        print(f"   cd src/vector-db && docker-compose up -d")
        return

    collection_name = f"safety-policies-{method}"
    print(f"Creating collection: {collection_name}")

    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        print(f"Collection '{collection_name}' did not exist. Creating new.")

    collection = client.create_collection(
        name=collection_name, 
        metadata={"hnsw:space": "cosine"}
    )
    print(f"Created new empty collection '{collection_name}'")

    # Get embedding files
    jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"embeddings-{method}-*.jsonl"))
    print(f"Number of files to process: {len(jsonl_files)}")

    for jsonl_file in jsonl_files:
        print(f"\nProcessing file: {jsonl_file}")

        data_df = pd.read_json(jsonl_file, lines=True)
        print(f"Shape: {data_df.shape}")
        print(data_df.head())

        load_text_embeddings(data_df, collection)


def query(method="char-split", department="internal_medicine"):
    """Test querying the vector database"""
    print("=== Testing Query ===")

    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    collection_name = f"safety-policies-{method}"

    query_text = "What are the protocols for patient fall prevention?"
    query_embedding = generate_query_embedding(query_text)

    collection = client.get_collection(name=collection_name)

    # Query with department filter
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"department": department}
    )
    
    print(f"\nQuery: {query_text}")
    print(f"Department filter: {department}")
    print(f"\nResults:")
    for i, doc in enumerate(results["documents"][0]):
        print(f"\n--- Result {i+1} ---")
        print(doc[:200] + "..." if len(doc) > 200 else doc)


def main(args=None):
    """Main CLI entry point"""
    print("CLI Arguments:", args)

    if args.chunk:
        chunk(method=args.chunk_type)

    if args.embed:
        embed(method=args.chunk_type)

    if args.load:
        load(method=args.chunk_type)

    if args.query:
        query(method=args.chunk_type, department=args.department)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vector DB CLI for Safety Policy RAG")

    parser.add_argument("--chunk", action="store_true", help="Chunk policy documents")
    parser.add_argument("--embed", action="store_true", help="Generate embeddings")
    parser.add_argument("--load", action="store_true", help="Load embeddings to vector db")
    parser.add_argument("--query", action="store_true", help="Test query vector db")
    parser.add_argument("--chunk_type", default="char-split", help="char-split | recursive-split")
    parser.add_argument("--department", default="internal_medicine", help="Department to query")

    args = parser.parse_args()
    main(args)
