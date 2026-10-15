import requests
import io
from PIL import Image

def test_full_pipeline():
    print("=================================================================")
    print("GAIA DETECTOR END-TO-END VERIFICATION SUITE")
    print("=================================================================\n")

    # 1. Health via Vite Proxy (port 5173 -> 8000)
    print("1. [Proxy Health Check] Testing http://localhost:5173/health...")
    r_health = requests.get("http://localhost:5173/health", timeout=10)
    print("   -> Status:", r_health.status_code, "| Body:", r_health.json())
    assert r_health.status_code == 200, "Health check failed"

    # 2. Text Detection via Vite Proxy
    print("\n2. [Text Detection] Testing http://localhost:5173/detect/text...")
    text_payload = {
        "text": (
            "The implementation of artificial neural networks has demonstrated substantial performance gains "
            "across multidimensional classification domains, offering probabilistic bounds and feature representations."
        )
    }
    r_text = requests.post("http://localhost:5173/detect/text", json=text_payload, timeout=60)
    print("   -> Status:", r_text.status_code)
    data_text = r_text.json()
    print("   -> Verdict:", data_text.get("prediction"), "| Status:", data_text.get("status"))
    print("   -> Confidence:", data_text.get("confidence"), "% | Risk:", data_text.get("risk_level"))
    print("   -> Engine:", data_text.get("detector_name"))
    print("   -> Diagnostics:", data_text.get("summary"))
    assert r_text.status_code == 200, "Text detection failed"

    # 3. Image Detection via Direct Backend
    print("\n3. [Image Detection] Testing http://127.0.0.1:8000/detect/image...")
    img = Image.new("RGB", (128, 128), color=(73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_bytes = img_byte_arr.getvalue()

    files = {"file": ("test_sample.png", img_bytes, "image/png")}
    r_image = requests.post("http://127.0.0.1:8000/detect/image", files=files, timeout=60)
    print("   -> Status:", r_image.status_code)
    data_image = r_image.json()
    print("   -> Verdict:", data_image.get("prediction"), "| Status:", data_image.get("status"))
    print("   -> Confidence:", data_image.get("confidence"), "% | Risk:", data_image.get("risk_level"))
    print("   -> Engine:", data_image.get("detector_name"))
    assert r_image.status_code == 200, "Image detection failed"

    # 4. Document Detection via Direct Backend
    print("\n4. [Document Detection] Testing http://127.0.0.1:8000/detect/document...")
    doc_content = (
        "Project Architecture Document for Gaia Content Authenticity Detector.\n\n"
        "This multi-modal system integrates custom Random Forest classifiers with deep pretrained transformers "
        "and external validation APIs to verify text, document, image, and video content."
    ).encode("utf-8")
    files_doc = {"file": ("architecture_overview.txt", doc_content, "text/plain")}
    r_doc = requests.post("http://127.0.0.1:8000/detect/document", files=files_doc, timeout=60)
    print("   -> Status:", r_doc.status_code)
    data_doc = r_doc.json()
    print("   -> Verdict:", data_doc.get("prediction"), "| Status:", data_doc.get("status"))
    print("   -> Confidence:", data_doc.get("confidence"), "% | Risk:", data_doc.get("risk_level"))
    print("   -> Modality:", data_doc.get("content_type"))
    print("   -> Engine:", data_doc.get("detector_name"))
    assert r_doc.status_code == 200, "Document detection failed"

    print("\n=================================================================")
    print("ALL LIVE END-TO-END WORKFLOWS VERIFIED SUCCESSFULLY!")
    print("=================================================================")

if __name__ == "__main__":
    test_full_pipeline()
