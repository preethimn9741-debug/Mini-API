import os
import pytest
from fastapi.testclient import TestClient
from app.main import app, UPLOAD_DIR, REPORT_DIR

client = TestClient(app)

def test_invalid_http_method():
    response = client.put("/")
    assert response.status_code == 405

def test_invalid_endpoint():
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

def test_upload_without_multipart_form():
    response = client.post("/upload", data={"file": "abc"})
    assert response.status_code == 422

def test_upload_with_empty_body():
    response = client.post("/upload")
    assert response.status_code == 422

def test_upload_file_with_no_extension():
    response = client.post(
        "/upload",
        files={"file": ("file", b"a,b\n1,2")}
    )
    assert response.status_code == 400

def test_upload_csv_with_double_extension():
    response = client.post(
        "/upload",
        files={"file": ("file.csv.exe", b"a,b\n1,2")}
    )
    assert response.status_code == 400

def test_upload_csv_with_unicode_filename():
    response = client.post(
        "/upload",
        files={"file": ("测试.csv", b"a,b\n1,2")}
    )
    assert response.status_code in [200, 400]

def test_upload_csv_with_newline_in_filename():
    response = client.post(
        "/upload",
        files={"file": ("bad\nname.csv", b"a,b\n1,2")}
    )
    assert response.status_code in [400, 422]

def test_upload_csv_with_null_byte_in_filename():
    response = client.post(
        "/upload",
        files={"file": ("bad\x00name.csv", b"a,b\n1,2")}
    )
    assert response.status_code in [400, 500]

def test_upload_csv_overwrite_attack():
    response1 = client.post(
        "/upload",
        files={"file": ("overwrite.csv", b"a,b\n1,2")}
    )
    response2 = client.post(
        "/upload",
        files={"file": ("overwrite.csv", b"x,y\n9,9")}
    )
    assert response1.status_code == 200
    assert response2.status_code == 200

def test_upload_extremely_large_file_simulated():
    big_content = b"a,b\n" + b"1,2\n" * 100000
    response = client.post(
        "/upload",
        files={"file": ("big.csv", big_content)}
    )
    assert response.status_code in [200, 413]

def test_validate_with_sql_injection_like_filename():
    response = client.post(
        "/validate",
        params={"filename": "test.csv; DROP TABLE users;"}
    )
    assert response.status_code == 404

def test_validate_with_path_traversal_attack():
    response = client.post(
        "/validate",
        params={"filename": "../../windows/system.ini"}
    )
    assert response.status_code in [400, 404]

def test_validate_with_absolute_path():
    response = client.post(
        "/validate",
        params={"filename": "C:\\Windows\\system.ini"}
    )
    assert response.status_code in [400, 404]

def test_validate_empty_csv_file():
    file_path = os.path.join(UPLOAD_DIR, "empty.csv")
    with open(file_path, "w") as f:
        f.write("")

    response = client.post("/validate", params={"filename": "empty.csv"})
    assert response.status_code in [400, 200]

def test_validate_csv_with_only_commas():
    file_path = os.path.join(UPLOAD_DIR, "commas.csv")
    with open(file_path, "w") as f:
        f.write(",,\n,,\n")

    response = client.post("/validate", params={"filename": "commas.csv"})
    assert response.status_code in [200, 400]

def test_validate_csv_with_inconsistent_columns():
    file_path = os.path.join(UPLOAD_DIR, "badcols.csv")
    with open(file_path, "w") as f:
        f.write("a,b,c\n1,2\n1,2,3,4")

    response = client.post("/validate", params={"filename": "badcols.csv"})
    assert response.status_code in [200, 400]

def test_validate_csv_with_only_whitespace():
    file_path = os.path.join(UPLOAD_DIR, "space.csv")
    with open(file_path, "w") as f:
        f.write("   \n   ")

    response = client.post("/validate", params={"filename": "space.csv"})
    assert response.status_code in [400, 200]

def test_download_with_wrong_http_method():
    response = client.post("/download")
    assert response.status_code == 405

def test_download_when_reports_folder_deleted():
    if os.path.exists(REPORT_DIR):
        os.rename(REPORT_DIR, REPORT_DIR + "_tmp")

    response = client.get("/download")
    assert response.status_code == 404

    os.rename(REPORT_DIR + "_tmp", REPORT_DIR)

def test_download_report_with_no_permissions():
    report_path = os.path.join(REPORT_DIR, "errors.csv")
    with open(report_path, "w") as f:
        f.write("test")

    os.chmod(report_path, 0o000)
    response = client.get("/download")
    assert response.status_code in [403, 500]

    os.chmod(report_path, 0o644)

def test_download_when_report_is_empty():
    report_path = os.path.join(REPORT_DIR, "errors.csv")
    with open(report_path, "w") as f:
        f.write("")

    response = client.get("/download")
    assert response.status_code == 200

def test_rapid_multiple_uploads():
    for _ in range(10):
        response = client.post(
            "/upload",
            files={"file": ("spam.csv", b"a,b\n1,2")}
        )
        assert response.status_code == 200

def test_rapid_validate_calls():
    for _ in range(10):
        response = client.post(
            "/validate",
            params={"filename": "no-file.csv"}
        )
        assert response.status_code == 404
