"""
runner.py - CLI runner for isolated video prediction.
"""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from hybrid_detector import HybridVideoDetector

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing video file path"}))
        sys.exit(1)
        
    video_path = sys.argv[1]
    detector = HybridVideoDetector()
    result = detector.predict(video_path)
    print("__GAIA_RESULT__" + json.dumps(result))

if __name__ == "__main__":
    main()
