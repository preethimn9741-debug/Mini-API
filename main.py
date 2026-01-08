from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import shutil
import os

app = FastAPI()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
REPORT_DIR = os.getenv("REPORT_DIR", "reports")
REPORT_FILE = "errors.csv"

def ensure_folder(path: str):
    os.makedirs(path, exist_ok=True)

ensure_folder(UPLOAD_DIR)
ensure_folder(REPORT_DIR)

@app.get("/")
def home():
    return {"message": "API working"}

@app.post("/upload")
def upload_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception:
        raise HTTPException(status_code=500, detail="File upload failed")

    return {"message": "File uploaded", "filename": file.filename}

@app.post("/validate")
def validate_csv(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    try:
        df = pd.read_csv(file_path)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    errors = []

    for i, row in df.iterrows():
        if row.isnull().any():
            errors.append({"row": i + 1, "error": "Missing value"})

    report_path = os.path.join(REPORT_DIR, REPORT_FILE)
    pd.DataFrame(errors).to_csv(report_path, index=False)

    return {"total_errors": len(errors)}

@app.get("/download")
def download_report():
    report_path = os.path.join(REPORT_DIR, REPORT_FILE)

    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="No report found")

    return FileResponse(report_path, filename=REPORT_FILE)
