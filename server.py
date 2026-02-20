import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from dotenv import load_dotenv
import torch
import json
import clip
from PIL import Image

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = "composbench-coco-unlabled2017"
pinecone_index = pc.Index(index_name)

device = "mps" if torch.mps.is_available() else "cpu"
clip_model_name = "ViT-L/14"

searle, encode_with_pseudo_tokens = torch.hub.load(repo_or_dir='miccunifi/SEARLE', source='github', model='searle',
                                                   backbone=clip_model_name)
searle.to(device)

# load CLIP model and preprocessing function
clip_model, preprocess = clip.load(clip_model_name)
clip_model.to(device)

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of allowed origins
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all headers
)

val_set = []
val_file_path = "./CIRCO/annotations/val.json"
with open(val_file_path, 'r') as f:
    val_set = json.load(f)

@app.get("/image/{image_id}")
def read_image(image_id: str):
    # Construct the path to the image
    image_path = f"./CIRCO/COCO2017_unlabeled/unlabeled2017/{image_id}"
    
    # Check if the file actually exists to prevent server errors
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
        
    # Return the file
    # FileResponse will automatically infer the media type (e.g., image/jpeg) from the file extension
    return FileResponse(image_path)

@app.get("/val.json")
def read_val_json():
    if not os.path.exists(val_file_path):
        raise HTTPException(status_code=404, detail="val.json file not found")
    
    return FileResponse(val_file_path)

@app.get("/search-val")
def search_val(val_id: int, algo: str):
    ref_img_id = val_set[val_id]["reference_img_id"]
    modification_text = val_set[val_id]["relative_caption"]
    ref_img_id_str = str(ref_img_id)
    ref_img_filename = "0"*(12-len(ref_img_id_str)) + ref_img_id_str + ".jpg"
    image_path = f"./CIRCO/COCO2017_unlabeled/unlabeled2017/{ref_img_filename}"

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    image_features = clip_model.encode_image(image).float()

    extimated_tokens = searle(image_features.to(device))

    prompt = "a photo of $ that " + modification_text 

    tokenized_prompt = clip.tokenize([prompt]).to(device)
    text_features = encode_with_pseudo_tokens(clip_model, tokenized_prompt, extimated_tokens)

    text_features.to("cpu")

    embedding = text_features.detach().cpu().numpy().tolist()

    response = pinecone_index.query(
                vector=embedding[0],
                top_k=100,
                include_metadata=True,
            )
    results = []
    for match in response["matches"]:
        results.append({
            "filename": match["id"],
            "score": match["score"]
        })
    return results

