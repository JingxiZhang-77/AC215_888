# Chunk the input file(text book) for embding use. Sotre the chunk in output folder

import os
import pandas as pd
import glob
from google.cloud import storage
from google import genai
from google.genai import types
from google.genai import errors
import time
from semantic_splitter import SemanticChunker


CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
gcp_project = "apcomp215-group88"
bucket_name = "88-data"
EMBEDDING_MODEL = "text-embedding-004"
INPUTE_FOLDER = 'books'
OUTPUT_FOLDER = "RAG_outputs"
GCP_LOCATION = "us-central1"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-2.0-flash-001"
chunk_file = "semantic-chunks-policy.jsonl"
prefix = "Mock_policy_RAG/"

book_mappings = {
    "Medicine": {"author": "LLM", "year": 2025},
    "Surgery": {"author": "LLM", "year": 2025},
    "OB_GYN_NICU": {"author": "LLM", "year": 2025},
    "Radiology_Imaging": {"author": "LLM", "year": 2025},
    "Outpatient_ER": {"author": "LLM", "year": 2025},
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
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(INPUTE_FOLDER, exist_ok=True)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)

    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        filename = blob.name.replace(prefix, "")
        local_path = os.path.join(INPUTE_FOLDER, filename)
        
        blob.download_to_filename(local_path)
    text_files = glob.glob(os.path.join(INPUTE_FOLDER, "*.txt"))
    for text_file in text_files:
        print("Processing file:", text_file)
        filename = os.path.basename(text_file)
        book_name = filename.split(".")[0]
        with open(text_file, "r", encoding="utf-8") as f:
            input_text = f.read()
        text_chunks = None

        print("Performing semantic chunking...")
        text_splitter = SemanticChunker(
            embedding_function=generate_text_embeddings,
            breakpoint_threshold_type="percentile",  
            breakpoint_threshold_amount=90           # lower = more chunks
        )

        text_chunks = text_splitter.create_documents([input_text])
        text_chunks = [doc.page_content for doc in text_chunks]
        print("✅ Number of semantic chunks:", len(text_chunks))

        if text_chunks is not None:
            # Save the chunks
            data_df = pd.DataFrame(text_chunks, columns=["chunk"])
            data_df["book"] = book_name
            print("Shape:", data_df.shape)
            print(data_df.head())

            jsonl_filename = os.path.join(
                OUTPUT_FOLDER, f"chunks-{book_name}.jsonl")
            with open(jsonl_filename, "w") as json_file:
                json_file.write(data_df.to_json(orient='records', lines=True))

def main():
    get_data_do_chunks()


if __name__ == "__main__":
    main()
