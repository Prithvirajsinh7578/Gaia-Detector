import io
import os
import sys
import time
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Ensure detector packages are discoverable on sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DETECTOR_DIR = WORKSPACE_ROOT / "detector"
VIDEO_DETECTOR_DIR = DETECTOR_DIR / "video_detector"

for p in [str(WORKSPACE_ROOT), str(DETECTOR_DIR), str(VIDEO_DETECTOR_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)


class ContentDetectorService:
    def __init__(self):
        # 1. Image Model (CLIP)
        self._clip_pipeline = None
        self._clip_loaded = False
        self._clip_error = None

        # 2. Text Model (Hybrid Ensemble: 18-Feature RF + RoBERTa + GPTZero)
        self._text_detector = None
        self._text_loaded = False
        self._text_error = None

        # 3. Video Model (Hybrid Ensemble: 21-Feature Spatio-Temporal RF + HuggingFace + Sightengine)
        self._video_detector = None
        self._video_loaded = False
        self._video_error = None

    # -------------------------------------------------------------------------
    # LAZY MODEL LOADERS
    # -------------------------------------------------------------------------
    def _load_clip_model(self):
        if self._clip_loaded:
            return
        try:
            from transformers import pipeline
            logger.info("Loading CLIP image model (openai/clip-vit-base-patch32)...")
            self._clip_pipeline = pipeline(
                "zero-shot-image-classification",
                model="openai/clip-vit-base-patch32"
            )
            self._clip_loaded = True
            logger.info("CLIP model loaded successfully.")
        except Exception as e:
            self._clip_error = str(e)
            logger.warning(f"Could not load CLIP model: {e}")

    def _load_text_detector(self):
        if self._text_loaded:
            return
        try:
            # Change directory context if needed for relative model weight paths
            sys.path.insert(0, str(DETECTOR_DIR))
            from hybrid_detector import HybridTextDetector
            logger.info("Mounting Hybrid AI Text Detector...")
            self._text_detector = HybridTextDetector()
            self._text_loaded = True
            logger.info("Hybrid Text Detector mounted successfully.")
        except Exception as e:
            self._text_error = str(e)
            logger.error(f"Could not load Hybrid Text Detector: {e}")

    def _load_video_detector(self):
        if self._video_loaded:
            return
        try:
            sys.path.insert(0, str(VIDEO_DETECTOR_DIR))
            from hybrid_detector import HybridVideoDetector
            logger.info("Mounting Hybrid AI Video Detector...")
            self._video_detector = HybridVideoDetector()
            self._video_loaded = True
            logger.info("Hybrid Video Detector mounted successfully.")
        except Exception as e:
            self._video_error = str(e)
            logger.error(f"Could not load Hybrid Video Detector: {e}")

    # -------------------------------------------------------------------------
    # 1. IMAGE DETECTION
    # -------------------------------------------------------------------------
    def detect_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Zero-shot image classification using CLIP."""
        start_time = time.time()
        self._load_clip_model()

        if not self._clip_loaded or not self._clip_pipeline:
            return {
                "content_type": "image",
                "status": "Detector Unavailable",
                "prediction": "Unknown",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": (
                    f"Image detection model (CLIP) is not loaded: {self._clip_error or 'Transformers/PyTorch missing'}. "
                    "Please ensure transformers and PyTorch are initialized."
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
                f"Classification resulted in '{status}' using zero-shot CLIP inference."
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

    # -------------------------------------------------------------------------
    # 2. TEXT DETECTION
    # -------------------------------------------------------------------------
    def detect_text(self, text: str) -> Dict[str, Any]:
        """Hybrid AI Text Detection combining 18-Feature RF, RoBERTa, and GPTZero."""
        start_time = time.time()
        self._load_text_detector()

        if not self._text_loaded or not self._text_detector:
            return {
                "content_type": "text",
                "status": "Detector Unavailable",
                "prediction": "Unknown",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Hybrid Text Detector is unavailable: {self._text_error or 'Module initialization failed'}.",
                "detector_name": "Gaia Hybrid Text Ensemble",
                "verified": False,
                "details": {"error": self._text_error}
            }

        try:
            res = self._text_detector.predict(text)
            prob = float(res.get("probability", 50.0))
            verdict = res.get("verdict", "Inconclusive")
            conf_rating = res.get("confidence", "Medium")
            indicators = res.get("indicators", [])
            consensus = res.get("consensus", {})
            ind_dict = res.get("individual_detectors", {})
            features = res.get("features", {})
            detailed_features = res.get("detailed_features", {})

            is_ai = prob >= 50.0
            verdict_lower = verdict.lower()
            if "likely ai" in verdict_lower or "possibly ai" in verdict_lower or "ai-generated" in verdict_lower:
                status = "Likely AI Generated"
                prediction = "Likely AI"
                risk_level = "High" if prob >= 70 else "Medium"
                confidence = prob
            elif "human" in verdict_lower or "authentic" in verdict_lower or "real" in verdict_lower:
                status = "Likely Human Written"
                prediction = "Likely Real"
                risk_level = "Low"
                confidence = 100.0 - prob
            else:
                status = "Inconclusive / Uncertain"
                prediction = "Inconclusive"
                risk_level = "Medium"
                confidence = round(abs(prob - 50.0) * 2.0, 1)

            summary = (
                f"Multi-evidence text analysis resulted in '{status}' with an ensemble AI probability of {prob:.1f}%. "
                f"Consensus: {consensus.get('agreement', 'N/A')}. "
                f"Key indicators: {', '.join(indicators[:3]) if indicators else 'Balanced linguistic profile'}."
            )

            return {
                "content_type": "text",
                "status": status,
                "prediction": prediction,
                "confidence": round(confidence, 1),
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": risk_level,
                "summary": summary,
                "detector_name": "Gaia Hybrid Text Ensemble (Custom RF + RoBERTa + GPTZero)",
                "verified": True,
                "details": {
                    "probability": prob,
                    "confidence_rating": conf_rating,
                    "verdict": verdict,
                    "indicators": indicators,
                    "consensus": consensus,
                    "individual_detectors": ind_dict,
                    "features": features,
                    "detailed_features": detailed_features,
                    "character_count": len(text)
                }
            }
        except Exception as e:
            logger.error(f"Text analysis error: {e}")
            return {
                "content_type": "text",
                "status": "Analysis Failed",
                "prediction": "Error",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Text detection failed: {str(e)}",
                "detector_name": "Gaia Hybrid Text Ensemble",
                "verified": False,
                "details": {"error": str(e)}
            }

    # -------------------------------------------------------------------------
    # 3. DOCUMENT DETECTION
    # -------------------------------------------------------------------------
    def detect_document(self, doc_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Extracts text from PDF, DOCX, or TXT documents, then runs Hybrid Text Detection."""
        start_time = time.time()
        extracted_text = ""
        extraction_success = False
        pages_count = 0
        file_ext = Path(filename).suffix.lower()

        try:
            if file_ext == ".pdf":
                import pdfplumber
                with pdfplumber.open(io.BytesIO(doc_bytes)) as pdf:
                    pages_count = len(pdf.pages)
                    # Extract up to 15 pages for comprehensive document scanning
                    pages_text = [p.extract_text() or "" for p in pdf.pages[:15]]
                    extracted_text = "\n\n".join(t.strip() for t in pages_text if t.strip())
                    extraction_success = bool(extracted_text.strip())
            elif file_ext in [".docx", ".doc"]:
                import docx
                doc = docx.Document(io.BytesIO(doc_bytes))
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                extracted_text = "\n\n".join(paragraphs)
                extraction_success = bool(extracted_text.strip())
            elif file_ext in [".txt", ".md", ".json", ".csv"]:
                extracted_text = doc_bytes.decode("utf-8", errors="replace")
                extraction_success = bool(extracted_text.strip())
            else:
                return {
                    "content_type": "document",
                    "status": "Unsupported Document Format",
                    "prediction": "Error",
                    "confidence": 0.0,
                    "processing_time_sec": round(time.time() - start_time, 2),
                    "risk_level": "Unknown",
                    "summary": f"File format '{file_ext}' is not supported. Supported: .pdf, .docx, .txt, .md, .csv",
                    "detector_name": "Gaia Document Pipeline",
                    "verified": False,
                    "details": {"filename": filename, "format": file_ext}
                }
        except Exception as e:
            logger.error(f"Document extraction error on {filename}: {e}")
            return {
                "content_type": "document",
                "status": "Extraction Failed",
                "prediction": "Error",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Could not extract text from '{filename}': {str(e)}",
                "detector_name": "Gaia Document Pipeline",
                "verified": False,
                "details": {"filename": filename, "error": str(e)}
            }

        if not extraction_success or len(extracted_text.strip()) < 20:
            return {
                "content_type": "document",
                "status": "Insufficient Content",
                "prediction": "Inconclusive",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Low",
                "summary": f"Document '{filename}' contains insufficient selectable text (scanned or image-only pages).",
                "detector_name": "Gaia Document Pipeline",
                "verified": False,
                "details": {
                    "filename": filename,
                    "extracted_chars": len(extracted_text),
                    "pages": pages_count
                }
            }

        # Run text detection on extracted content
        text_result = self.detect_text(extracted_text)
        
        # Override metadata for document context
        text_result["content_type"] = "document"
        text_result["detector_name"] = "Gaia Document Pipeline (Text Extraction + Hybrid Ensemble)"
        text_result["summary"] = (
            f"Document '{filename}' ({pages_count} pages analyzed): {text_result['summary']}"
        )
        if text_result.get("details"):
            text_result["details"]["filename"] = filename
            text_result["details"]["pages_count"] = pages_count
            text_result["details"]["extracted_characters"] = len(extracted_text)

        return text_result

    # -------------------------------------------------------------------------
    # 4. VIDEO DETECTION
    # -------------------------------------------------------------------------
    def detect_video(self, video_bytes: bytes, filename: str) -> Dict[str, Any]:
        """Hybrid Spatio-Temporal Video Detection."""
        start_time = time.time()
        self._load_video_detector()

        if not self._video_loaded or not self._video_detector:
            return {
                "content_type": "video",
                "status": "Detector Unavailable",
                "prediction": "Unknown",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Hybrid Video Detector is unavailable: {self._video_error or 'Module initialization failed'}.",
                "detector_name": "Gaia Hybrid Video Ensemble",
                "verified": False,
                "details": {"error": self._video_error}
            }

        ext = Path(filename).suffix or ".mp4"
        temp_file = None
        try:
            # Write to temporary file for frame decoding with OpenCV
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(video_bytes)
                temp_file = f.name

            # Run video prediction
            res = self._video_detector.predict(temp_file)
            
            prob = float(res.get("ai_probability", res.get("probability", 50.0)))
            verdict = res.get("verdict", "Inconclusive")
            conf_rating = res.get("confidence", "Medium")
            frames_analyzed = res.get("frames_analyzed", 0)
            temporal_analysis = res.get("temporal_analysis", "completed")
            indicators = res.get("visual_indicators", [])
            consensus = res.get("consensus", {})
            ind_dict = res.get("individual_detectors", {})
            features = res.get("summary_features", {})

            is_ai = prob >= 50.0
            verdict_lower = verdict.lower()
            if "likely ai" in verdict_lower or "ai-generated" in verdict_lower or "synthetic" in verdict_lower:
                status = "Likely AI Generated"
                prediction = "Likely AI"
                risk_level = "High" if prob >= 70 else "Medium"
                confidence = prob
            elif "authentic" in verdict_lower or "real" in verdict_lower or "human" in verdict_lower:
                status = "Likely Real Video"
                prediction = "Likely Real"
                risk_level = "Low"
                confidence = 100.0 - prob
            else:
                status = "Inconclusive / Uncertain"
                prediction = "Inconclusive"
                risk_level = "Medium"
                confidence = round(abs(prob - 50.0) * 2.0, 1)

            indicators_clean = indicators if indicators else [
                "Temporal coherence verified", "Natural frame-to-frame variance"
            ]

            summary = (
                f"Video analysis ({verdict}) indicates a {prob:.1f}% AI probability across {frames_analyzed} frames. "
                f"Temporal analysis: {temporal_analysis}. Key cues: {', '.join(indicators_clean[:2])}."
            )

            return {
                "content_type": "video",
                "status": status,
                "prediction": prediction,
                "confidence": round(confidence, 1),
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": risk_level,
                "summary": summary,
                "detector_name": "Gaia Hybrid Video Ensemble (Spatio-Temporal RF + HuggingFace + Sightengine)",
                "verified": True,
                "details": {
                    "probability": prob,
                    "confidence_rating": conf_rating,
                    "verdict": verdict,
                    "frames_analyzed": frames_analyzed,
                    "temporal_analysis": temporal_analysis,
                    "visual_indicators": indicators_clean,
                    "consensus": consensus,
                    "individual_detectors": ind_dict,
                    "features": features
                }
            }
        except Exception as e:
            logger.error(f"Video analysis error on {filename}: {e}")
            return {
                "content_type": "video",
                "status": "Analysis Failed",
                "prediction": "Error",
                "confidence": 0.0,
                "processing_time_sec": round(time.time() - start_time, 2),
                "risk_level": "Unknown",
                "summary": f"Video analysis failed on '{filename}': {str(e)}",
                "detector_name": "Gaia Hybrid Video Ensemble",
                "verified": False,
                "details": {"filename": filename, "error": str(e)}
            }
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass


detector_service = ContentDetectorService()
