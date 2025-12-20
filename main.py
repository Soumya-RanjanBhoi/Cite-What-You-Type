import os
import shutil
from pathlib import Path
import uuid
from fastapi import FastAPI, File, UploadFile,HTTPException
from conversion import convert_to_pdf 
from google.cloud import storage
from Multi_Modal.main_pdf import get_ans
from dotenv import load_dotenv



load_dotenv()


app = FastAPI()

UPLOAD_DIR = Path("upload_files")
UPLOAD_DIR.mkdir(exist_ok=True)
PROJECT_iD= os.environ['PROJECT_ID']
PDF_BUCKET_NAME = os.environ['PDF_BUCKET_NAME']

async def upload_file_to_gcp(source_file_path):
    try:
        unique_value = str(uuid.uuid4())
        
        file_name = Path(source_file_path).name
        dest_name = f"uploads/{unique_value}_{file_name}"
        
        storage_client = storage.Client(project=PROJECT_iD)
        bucket = storage_client.bucket(PDF_BUCKET_NAME)

        blob = bucket.blob(dest_name)

        blob.upload_from_filename(str(source_file_path))
        print(f"File {source_file_path} uploaded to gs://{PDF_BUCKET_NAME}/{dest_name}.")
        return f"gs://{PDF_BUCKET_NAME}/{dest_name}"

    except Exception as e:
        print("Could not upload file to GCP:", e)


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
            # final_path = await upload_file_to_gcp(saved_path)
            # saved_path.unlink()
            final_path=saved_path

        else:
            final_path = await convert_to_pdf(str(saved_path), str(UPLOAD_DIR))
            # final_path=await upload_file_to_gcp(final_path)
            saved_path.unlink()

        return {
            "status": "success",
            "pdf_path": str(final_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500,detail=e)