import os
import pandas as pd
import glob
from google.cloud import storage
from google import genai
from google.genai import types
from google.genai import errors
import time
from semantic_splitter import SemanticChunker
import chromadb
import hashlib
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
gcp_project = "apcomp215-group88"
bucket_name = "88-data"
EMBEDDING_MODEL = "text-embedding-004"
source_blob_name = "Mock_policy_RAG/policy.txt" 
OUTPUT_FOLDER = "RAG_outputs"
GCP_LOCATION = "us-central1"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-2.0-flash-001"
chunk_file = "semantic-chunks-policy.jsonl"
book_mappings = {
    "policy": {"author": "LLM", "year": 2025},
}


#############################################################################
#                       Initialize the LLM Client                           #
llm_client = genai.Client(vertexai=True, project=gcp_project, location="us-central1")
storage_client = storage.Client()#############################################################################

def generate_text_embeddings(chunks, dimensionality: int = 256, batch_size=250, max_retries=5, retry_delay=5):
    # Max batch size is 250 for Vertex AI
    all_embeddings = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        # Retry logic with exponential backoff
        retry_count = 0
        while retry_count <= max_retries:
            try:
                response = llm_client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        output_dimensionality=dimensionality),
                )
                all_embeddings.extend(
                    [embedding.values for embedding in response.embeddings])
                break

            except errors.APIError as e:
                retry_count += 1
                if retry_count > max_retries:
                    print(
                        f"Failed to generate embeddings after {max_retries} attempts. Last error: {str(e)}")
                    raise

                # Calculate delay with exponential backoff
                wait_time = retry_delay * (2 ** (retry_count - 1))
                print(
                    f"API error (code: {e.code}): {e.message}. Retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})...")
                time.sleep(wait_time)

    return all_embeddings

def get_data_do_chunks():
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("Mock_policy_RAG/policy.txt")
    full_text = blob.download_as_text()

    print("Performing semantic chunking...")
    text_splitter = SemanticChunker(
        embedding_function=generate_text_embeddings,
        breakpoint_threshold_type="percentile",  
        breakpoint_threshold_amount=90           # lower = more chunks
    )

    text_chunks = text_splitter.create_documents([full_text])
    text_chunks = [doc.page_content for doc in text_chunks]
    print("✅ Number of semantic chunks:", len(text_chunks))
    
    if text_chunks is not None:
        # Save the chunks
        data_df = pd.DataFrame(text_chunks, columns=["chunk"])
        data_df["book"] = "policy.txt"
        print("Shape:", data_df.shape)
        print(data_df.head())

        jsonl_filename = os.path.join(
            OUTPUT_FOLDER, chunk_file)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        with open(jsonl_filename, "w") as json_file:
            json_file.write(data_df.to_json(orient='records', lines=True))

def embd():
    jsonl_files = glob.glob(os.path.join(
    OUTPUT_FOLDER, chunk_file))
    print("Number of files to process:", len(jsonl_files))
    # Process
    for jsonl_file in jsonl_files:
        print("Processing file:", jsonl_file)
        data_df = pd.read_json(jsonl_file, lines=True)
        # drop empty chunck
        data_df = data_df[data_df["chunk"].apply(lambda x: isinstance(x, str) and x.strip() != "")]
        print("Shape:", data_df.shape)
        print(data_df.head())
        chunks = data_df["chunk"].values
        chunks = chunks.tolist()
        embeddings = generate_text_embeddings(
            chunks, EMBEDDING_DIMENSION, batch_size=15)
        data_df["embedding"] = embeddings

        time.sleep(5)

        jsonl_filename = jsonl_file.replace("semantic-chunks-", "embeddings-")
        with open(jsonl_filename, "w") as json_file:
            json_file.write(data_df.to_json(orient='records', lines=True))

def load_text_embeddings(df, collection, batch_size=500):
    # Generate ids
    df["id"] = df.index.astype(str)
    hashed_books = df["book"].apply(
        lambda x: hashlib.sha256(x.encode()).hexdigest()[:16])
    df["id"] = hashed_books + "-" + df["id"]

    metadata = {
        "book": df["book"].tolist()[0]
    }
    if metadata["book"] in book_mappings:
        book_mapping = book_mappings[metadata["book"]]
        metadata["author"] = book_mapping["author"]
        metadata["year"] = book_mapping["year"]

    # Process data in batches
    total_inserted = 0
    for i in range(0, df.shape[0], batch_size):
        # Create a copy of the batch and reset the index
        batch = df.iloc[i:i+batch_size].copy().reset_index(drop=True)

        ids = batch["id"].tolist()
        documents = batch["chunk"].tolist()
        metadatas = [metadata for item in batch["book"].tolist()]
        embeddings = batch["embedding"].tolist()

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        total_inserted += len(batch)
        print(f"Inserted {total_inserted} items...")

    print(
        f"Finished inserting {total_inserted} items into collection '{collection.name}'")
    

def load(method="semantic-chunks"):
    print("load()")

    # Clear Cache
    chromadb.api.client.SharedSystemClient.clear_system_cache()

    # Connect to chroma DB
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

    # Get a collection object from an existing collection, by name. If it doesn't exist, create it.
    collection_name = f"{method}-collection"
    print("Creating collection:", collection_name)

    try:
        # Clear out any existing items in the collection
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        print(f"Collection '{collection_name}' did not exist. Creating new.")

    collection = client.create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"})
    print(f"Created new empty collection '{collection_name}'")
    print("Collection:", collection)

    # Get the list of embedding files
    jsonl_files = glob.glob(os.path.join(
        OUTPUT_FOLDER, f"embeddings-policy.jsonl"))
    print("Number of files to process:", len(jsonl_files))

    # Process
    for jsonl_file in jsonl_files:
        print("Processing file:", jsonl_file)

        data_df = pd.read_json(jsonl_file, lines=True)
        print("Shape:", data_df.shape)
        print(data_df.head())

        # Load data
        load_text_embeddings(data_df, collection)

def main():
    get_data_do_chunks()
    embd()
    load()


if __name__ == "__main__":
    main()
