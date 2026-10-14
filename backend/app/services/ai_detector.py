import io
import time
import logging
from typing import Dict, Any, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

class ContentDetectorService:
    def __init__(self):
        self._clip_pipeline = None
        self._clip_loaded = False
        self._clip_error = None

    def _load_clip_model(self):
        if self._clip_loaded:
            return
        try:
            from transformers import pipeline
            logger.info("Attempting to load CLIP model (openai/clip-vit-base-patch32)...")
            self._clip_pipeline = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32"
            )
            self._clip_loaded = True
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            self._clip_error = str(e)
            logger.warning(f"Could not load Hugging Face CLIP model: {e}")

    def detect_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Replicates the exact AI prototype logic from the ai branch (Detector.html):
        Zero-shot classification with CLIP against:
        'a real photograph taken by a camera' vs 'an AI generated image'
        Threshold: >= 60% AI -> Likely AI Generated, else -> Likely Real Image
        
        Important note: Heuristic classification; not a forensic guarantee.
        """
        start_time = time.time()
        self._load_clip_model()

        if not self._clip_loaded or not self._clip_pipeline:
            # Report honestly that model is unavailable/not loaded in current environment
            return {
                "content_type": "image",
                "status": "Detector Unavailable",
                "prediction": "Unknown",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": (
                    f"Image detection model (CLIP) is not loaded: {self._clip_error or 'Transformers/PyTorch missing or model download pending'}. "
                    "In local or offline environments, please download 'openai/clip-vit-base-patch32' or install PyTorch + transformers."
                ),
                "detector_name": "openai/clip-vit-base-patch32",
                "verified": False,
                "details": {"error": self._clip_error}
            }

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            candidate_labels = [
                "a real photograph taken by a camera",
                "an AI generated image"
            ]

            results = self._clip_pipeline(image, candidate_labels=candidate_labels)
            
            ai_score = 0.0
            for item in results:
                if item["label"] == "an AI generated image":
                    ai_score = float(item["score"]) * 100.0
                    break

            ai_percentage = max(0.0, min(100.0, ai_score))
            is_ai = ai_percentage >= 60.0

            prediction = "Likely AI" if is_ai else "Likely Real"
            status = "Likely AI Generated" if is_ai else "Likely Real Image"
            risk_level = "High" if is_ai else "Low"

            summary = (
                f"Image analysis indicates a {ai_percentage:.1f}% probability of being AI-generated. "
                f"Classification resulted in '{status}' using zero-shot CLIP inference. "
                "Note: Heuristic model output; should be verified against forensic metadata."
            )

            return {
                "content_type": "image",
                "status": status,
                "prediction": prediction,
                "confidence": round(ai_percentage if is_ai else (100.0 - ai_percentage), 1),
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": risk_level,
                "summary": summary,
                "detector_name": "openai/clip-vit-base-patch32",
                "verified": True,
                "details": {
                    "raw_scores": results,
                    "ai_score_percent": round(ai_percentage, 2)
                }
            }
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                "content_type": "image",
                "status": "Analysis Failed",
                "prediction": "Error",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Failed to analyze image file: {str(e)}",
                "detector_name": "openai/clip-vit-base-patch32",
                "verified": False,
                "details": {"error": str(e)}
            }

    def detect_text(self, text: str) -> Dict[str, Any]:
        """
        Text detection status: Reports honestly that no verified model is loaded.
        Does not fabricate random or fake scores.
        """
        start_time = time.time()
        return {
            "content_type": "text",
            "status": "Detector Not Implemented",
            "prediction": "Unverified",
            "confidence": 0.0,
            "processing_time_sec": round(time.time() - start_time, 2),
            "risk_level": "Unknown",
            "summary": "Text authenticity detection backend is architected, but no validated model pipeline (e.g. fine-tuned RoBERTa OpenAI detector) is currently mounted. No synthetic scores are returned.",
            "detector_name": "unmounted_text_detector",
            "verified": False,
            "details": {"character_count": len(text)}
        }

    def detect_document(self, doc_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Document detection status: Extracts text safely if PDF or TXT,
        but reports honest unverified status without synthetic detection score.
        """
        start_time = time.time()
        extracted_text = ""
        extraction_success = False

        if filename.lower().endswith(".pdf"):
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(doc_bytes)) as pdf:
                    pages = [p.extract_text() or "" for p in pdf.pages[:5]]
                    extracted_text = "\n".join(pages)
                    extraction_success = True
            except Exception as e:
                extracted_text = f"Extraction failed: {e}"
        elif filename.lower().endswith(".txt"):
            try:
                extracted_text = doc_bytes.decode("utf-8", errors="ignore")[:5000]
                extraction_success = True
            except Exception as e:
                extracted_text = f"Extraction failed: {e}"

        return {
            "content_type": "document",
            "status": "Detector Not Implemented",
            "prediction": "Unverified",
            "confidence": 0.0,
            "processing_time_sec": round(time.time() - start_time, 2),
            "risk_level": "Unknown",
            "summary": "Document text extraction pipeline is functional, but downstream multi-modal AI detector is not yet mounted. No synthetic scores are returned.",
            "detector_name": "document_pipeline",
            "verified": False,
            "details": {
                "extracted_length": len(extracted_text),
                "text_extracted": extraction_success
            }
        }

    def detect_video(self, video_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Video detection status: Honestly reports not implemented.
        Does not fabricate random scores.
        """
        start_time = time.time()
        return {
            "content_type": "video",
            "status": "Detector Not Implemented",
            "prediction": "Unverified",
            "confidence": 0.0,
            "processing_time_sec": round(time.time() - start_time, 2),
            "risk_level": "Unknown",
            "summary": "Frame extraction and temporal video authenticity analysis pipeline is not yet mounted. No synthetic scores are returned.",
            "detector_name": "video_pipeline",
            "verified": False,
            "details": {"size_bytes": len(video_bytes)}
        }

detector_service = ContentDetectorService()
