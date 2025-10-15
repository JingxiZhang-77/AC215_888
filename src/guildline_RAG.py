import os
import io
import argparse
import shutil
import glob
import pandas as pd
from io import BytesIO
import fitz # PyMuPDF package 
import json

from google.cloud import aiplatform
from google.cloud import storage
from pypdf import PdfReader

# Vertex AI
from google import genai
from google.genai import types
from google.genai.types import Content, Part, GenerationConfig, ToolConfig
from google.genai import errors
import time


# Langchain
from semantic_splitter import SemanticChunker


gcp_project = "apcomp215-group88"
bucket_name = "88-data"
EMBEDDING_MODEL = "text-embedding-004"
source_blob_name = "RAG_taxtbook/hpi-sec-sser.pdf" 
OUTPUT_FOLDER = "outputs"


GCP_PROJECT = os.environ["GCP_PROJECT"] # This should be the environment variable for the GCP project ID
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-2.0-flash-001"
INPUT_FOLDER = "input-datasets"
OUTPUT_FOLDER = "outputs"

chunk_file_name = "semantic chunks-hpi-sec-sser.pdf.jsonl"



#############################################################################
#                       Initialize the LLM Client                           #
llm_client = genai.Client(vertexai=True, project=gcp_project, location="us-central1")

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)


# Generate the inputs arguments parser
parser = argparse.ArgumentParser(description="Command description.")

# this function read the file in GCP bucket, convert it to text and put the result in output folder
def chunk(chunksize=40):
    # read the pdf book from gcp bucke
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    pdf_bytes = blob.download_as_bytes()
    pdf_stream = BytesIO(pdf_bytes)

    doc = fitz.open(stream=pdf_stream, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text("text")   # preserves line breaks
        # remove headers and footers
        clean_text = "\n".join([
            line for line in text.splitlines()
            if not line.strip().startswith("WHITE PAPER") and
            not line.strip().startswith("©Press Ganey")
        ])
        pages.append(clean_text.strip())
    full_text = "\n\n".join(pages)
    print("✅ Extracted characters:", len(full_text))


    print("Performing semantic chunking...")
    text_splitter = SemanticChunker(
        embedding_function=generate_text_embeddings,
        breakpoint_threshold_type="percentile",  
        breakpoint_threshold_amount=chunksize           # lower = more chunks
    )

    text_chunks = text_splitter.create_documents([full_text])
    text_chunks = [doc.page_content for doc in text_chunks]
    print("✅ Number of semantic chunks:", len(text_chunks))

    if text_chunks is not None:
        # Save the chunks
        data_df = pd.DataFrame(text_chunks, columns=["chunk"])
        data_df["book"] = "hpi-sec-sser.pdf"
        print("Shape:", data_df.shape)
        print(data_df.head())

        jsonl_filename = os.path.join(
            OUTPUT_FOLDER, chunk_file_name)
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        with open(jsonl_filename, "w") as json_file:
            json_file.write(data_df.to_json(orient='records', lines=True))


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

def embed():
    # Get the list of chunk files
    jsonl_files = glob.glob(os.path.join(
        OUTPUT_FOLDER, chunk_file_name))
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
        # Save
        print("Shape:", data_df.shape)
        print(data_df.head())
        jsonl_filename = jsonl_file.replace("semantic chunks-", "embeddings-")
        with open(jsonl_filename, "w") as json_file:
            json_file.write(data_df.to_json(orient='records', lines=True))

# Load Embeddings into GCP and deploy it
def Vertex_Matching():
    # convert the format to fit for vertex matching 
    emb_file_name = chunk_file_name.replace("semantic chunks-", "embeddings-")
    input_file = os.path.join(OUTPUT_FOLDER, emb_file_name)
    output_file_name = f"vertex-ready-{emb_file_name}"
    output_file = f"outputs/{output_file_name}"

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            obj = json.loads(line)
            record = {
                "id": str(i),
                "embedding": obj["embedding"],
                "data": obj["chunk"]  # or f"{obj['book']}: {obj['chunk']}"
            }
            records.append(record)

    with open(output_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    print(f"✅ Reformatted file saved: {output_file}")

    # upload the jsonl to bucket
    destination_blob_name = f"Embedding/{output_file_name}"
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(output_file)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob_name}")

    # create index in gcp
    index_display_name = "book-embeddings-index"
    aiplatform.init(project=gcp_project, location=GCP_LOCATION)

    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=index_display_name,
        contents_delta_uri=f"gs://{bucket_name}/Embedding/{output_file_name}",
        dimensions=256,   
        approximate_neighbors_count=10,
    )

    print("✅ Created index:", index.resource_name)

    # create endpoint
    endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
    display_name="book-rag-endpoint",
    public_endpoint_enabled=True,
    )

    # need to test
    endpoint.deploy_index(
    index=index,
    deployed_index_id="book_RAG_index" 
    )

if __name__ == "__main__":
    #generate chunk
    chunk(50)
    #geneerate enbedding
    embed()
    # Vertex_Matching() already run and exist in GCP bucket
