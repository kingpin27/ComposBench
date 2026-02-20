from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os

app = FastAPI()

@app.get("/image/{image_id}")
def read_item(image_id: str):
    # Construct the path to the image
    image_path = f"./CIRCO/COCO2017_unlabeled/unlabeled2017/{image_id}"
    
    # Check if the file actually exists to prevent server errors
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
        
    # Return the file
    # FileResponse will automatically infer the media type (e.g., image/jpeg) from the file extension
    return FileResponse(image_path)