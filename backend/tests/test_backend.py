import pytest
from fastapi.testclient import TestClient
from main import app
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.ai_detector import detector_service
from app.core.config import settings

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Gaia Detector API"
    assert "version" in data

def test_health_check_liveness():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "google_drive" in data

def test_ready_check_unconfigured_reports_ready_gracefully():
    # When DB is not configured, readiness endpoint safely reports status
    response = client.get("/ready")
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data

def test_security_passwords():
    plain = "SecurePassword123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_security_jwt_token_handling():
    payload = {"sub": "user_id_456", "email": "testuser@example.com", "name": "Test User"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user_id_456"
    assert decoded["email"] == "testuser@example.com"
    assert decoded["name"] == "Test User"
    assert "exp" in decoded

def test_jwt_tampered_token_fails():
    tampered = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"
    decoded = decode_access_token(tampered)
    assert decoded is None

def test_detect_text_live_pipeline():
    sample_text = (
        "Yesterday evening, I went out for a walk in the local park after a heavy rain shower. "
        "The air was cool and smelled of damp earth, which made the quiet stroll very relaxing."
    )
    response = client.post("/detect/text", json={"text": sample_text})
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "text"
    assert data["verified"] in [True, False]
    assert "details" in data
    assert "processing_time_sec" in data

def test_detect_document_txt_pipeline():
    sample_doc = (
        b"Artificial intelligence is transforming education by enabling personalized learning "
        b"experiences. Modern generative language models generate coherent academic text, "
        b"requiring robust statistical and stylometric evaluation to verify authenticity."
    )
    files = {"file": ("sample.txt", sample_doc, "text/plain")}
    response = client.post("/detect/document", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "document"
    assert "processing_time_sec" in data
    assert "details" in data

def test_detect_video_pipeline_handling():
    # Corrupt or mock bytes should be handled safely without unhandled 500 crash
    files = {"file": ("clip.mp4", b"\x00\x00\x00\x18ftypmp42", "video/mp4")}
    response = client.post("/detect/video", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "video"
    assert "processing_time_sec" in data

def test_upload_fallback_when_gdrive_unconfigured():
    files = {"file": ("test.png", b"\x89PNG\r\n\x1a\nfakeimagecontent", "image/png")}
    response = client.post("/upload", files=files, data={"type": "image"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["storage"] in ["memory", "gdrive"]
    assert "upload_id" in data

def test_upload_api_compatibility_endpoint():
    # Verifies /api/upload backward-compatibility
    files = {"file": ("test_doc.pdf", b"%PDF-1.4...", "application/pdf")}
    response = client.post("/api/upload", files=files, data={"type": "document"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_protected_routes_require_authentication():
    # /auth/me should reject request when no cookie/token provided
    res_me = client.get("/auth/me")
    assert res_me.status_code == 401

    # /history should reject request without auth
    res_history = client.get("/history")
    assert res_history.status_code == 401

    # /report/{id} should reject request without auth
    res_report = client.get("/report/64b1f2e5a1b2c3d4e5f6a7b8")
    assert res_report.status_code == 401

def test_authenticated_route_with_bearer_token():
    # Generate valid test token
    token = create_access_token({"sub": "test_user_789", "email": "bearer@example.com", "name": "Bearer Tester"})
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.get("/auth/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "bearer@example.com"
    assert data["name"] == "Bearer Tester"

def test_authenticated_route_with_cookie():
    token = create_access_token({"sub": "cookie_user_101", "email": "cookie@example.com", "name": "Cookie Tester"})
    cookies = {settings.COOKIE_NAME: token}
    
    res = client.get("/auth/me", cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "cookie@example.com"

def test_logout_clears_cookie():
    res = client.post("/auth/logout")
    assert res.status_code == 200
    # Cookie should be unset or expired
    cookie_header = res.headers.get("set-cookie", "")
    assert settings.COOKIE_NAME in cookie_header
