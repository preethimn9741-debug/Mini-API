# Mini-API
# CSV Validation API

This project is a FastAPI-based application that allows users to upload CSV files, validate data quality, and download validation reports.

---

## Features

- Upload CSV files through an API
- Validate CSV files for missing values
- Generate a CSV error report
- Download validation reports
- Automatic folder creation for uploads and reports
- Simple REST API design
- Fast execution using FastAPI

---

## API Endpoints

- `GET /`  
  Check if the API is running.

- `POST /upload`  
  Upload a CSV file to the server.

- `POST /validate`  
  Validate an uploaded CSV file and generate an error report.

- `GET /download`  
  Download the generated validation report.

---

## How to Run

1. Install required dependencies:
   
2. Start the API server:
   uvicorn main:app --reload

3. Open the application:
   http://127.0.0.1:8000

## Output

Uploaded files are stored in the uploads folder

Validation reports are stored in the reports folder

The total number of errors is returned after validation

## conclusion

This project provides a simple and efficient way to validate CSV files using a REST API.

It is suitable for learning, backend practice, and basic data validation tasks.
  
pip install fastapi uvicorn pandas

