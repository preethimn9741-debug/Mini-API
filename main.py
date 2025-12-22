from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import shutil
import os

app = FastAPI()

# --- SAFE folder creation ---
def ensure_folder(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            os.remove(path)   # delete file if exists
    os.makedirs(path, exist_ok=True)

ensure_folder("uploads")
ensure_folder("reports")
# ----------------------------

@app.get("/")
def home():
    return {"message": "API working"}

@app.post("/upload")
def upload_csv(file: UploadFile = File(...)):
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"message": "File uploaded", "filename": file.filename}

@app.post("/validate")
def validate_csv(filename: str):
    file_path = os.path.join("uploads", filename)

    if not os.path.exists(file_path):
        return {"error": "File not found"}

    df = pd.read_csv(file_path)
    errors = []

    for i, row in df.iterrows():
        if row.isnull().any():
            errors.append({"row": i + 1, "error": "Missing value"})

    report_path = os.path.join("reports", "errors.csv")
    pd.DataFrame(errors).to_csv(report_path, index=False)

    return {"total_errors": len(errors)}

@app.get("/download")
def download_report():
    report_path = os.path.join("reports", "errors.csv")
    if not os.path.exists(report_path):
        return {"error": "No report found"}
    return FileResponse(report_path, filename="errors.csv")
