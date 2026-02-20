from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware

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
    val_file_path = "./CIRCO/annotations/val.json"

    if not os.path.exists(val_file_path):
        raise HTTPException(status_code=404, detail="val.json file not found")
    
    return FileResponse(val_file_path)