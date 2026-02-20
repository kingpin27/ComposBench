from pandas.io import json
import pandas as pd
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
import os
import tqdm

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "composbench-coco-unlabled2017"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        vector_type="dense",
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        deletion_protection="disabled",
        tags={
            "environment": "development"
        }
    )

pinecone_index = pc.Index(index_name)

df = pd.read_parquet("clip_embeddings.parquet")

# Convert the DataFrame and save filename and embedding to pinecone index
batch = []
for index, row in tqdm.tqdm(df.iterrows(), total=df.shape[0]):
    filename = row["filename"]
    embedding = row["embedding"].tolist()  # Convert numpy array to list
    batch.append({
        "id": filename,
        "values": embedding
    })
    if len(batch) == 500:  # Pinecone has a limit of 100 vectors per upsert call
        pinecone_index.upsert(vectors=batch)
        batch = []

if batch:  # Upsert any remaining vectors
    pinecone_index.upsert(vectors=batch)