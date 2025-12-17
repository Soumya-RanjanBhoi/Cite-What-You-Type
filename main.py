import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from conversion import convert_to_pdf 
from Multi_Modal.main_pdf import get_ans

app = FastAPI()

UPLOAD_DIR = Path("upload_files")
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_file(file: UploadFile):
    file_path = UPLOAD_DIR / file.filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return file_path
    except Exception as e:
        print(f"Unable to save file: {e}")
        raise

@app.post("/process")
async def processing(query:str,file: UploadFile = File(...)):
    try:
        saved_path = await save_file(file)
        
        if file.filename.lower().endswith(".pdf"):
            final_path = saved_path
        else:
            final_path = await convert_to_pdf(str(saved_path), str(UPLOAD_DIR))
            saved_path.unlink()

            ans = get_ans(final_path,query,vector_dir="Vector Stores")

        
        
        return {
            "status": "success",
            "pdf_path": str(final_path),
            "ans":ans
        }
    except Exception as e:
        return {"error": str(e)}