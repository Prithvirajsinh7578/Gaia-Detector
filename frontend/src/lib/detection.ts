export type DetectionMode = "text" | "image" | "video";
export type DetectionResult = {
  verdict: "ai" | "human" | "inconclusive";
  score?: { value: number; label: string };
  summary?: string;
  model?: string;
  processingMs?: number;
  evidence?: string[];
};

// Verified backend proxy routes
export const detectionEndpoints: Record<DetectionMode, string> = {
  text: "/detect/text",
  image: "/detect/image",
  video: "/detect/video",
};

export const fileRules = {
  image: {
    types: ["image/jpeg", "image/png", "image/webp"],
    extensions: ["jpg", "jpeg", "png", "webp"],
    maxBytes: 20 * 1024 * 1024,
    label: "JPG, PNG, WEBP · Up to 20 MB",
  },
  video: {
    types: ["video/mp4", "video/webm", "video/quicktime"],
    extensions: ["mp4", "webm", "mov"],
    maxBytes: 100 * 1024 * 1024,
    label: "MP4, WEBM, MOV · Up to 100 MB",
  },
};

export function validateFile(file: File, mode: "image" | "video"): string | null {
  const rules = fileRules[mode];
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const typeMatches = file.type ? rules.types.includes(file.type) : false;
  const extMatches = rules.extensions.includes(extension);
  if (!typeMatches && !extMatches) return `Choose a supported ${mode} file.`;
  if (file.size === 0) return "This file is empty.";
  if (file.size > rules.maxBytes) return `File too large. Maximum ${mode === "image" ? "20" : "100"} MB.`;
  return null;
}

export function parseDetectionResult(data: unknown): DetectionResult {
  if (!data || typeof data !== "object") throw new Error("The detector returned an invalid result.");

  const raw = data as Record<string, any>;

  // 1. Determine Verdict
  let verdict: "ai" | "human" | "inconclusive" = "inconclusive";

  if (raw.verdict === "ai" || raw.verdict === "human" || raw.verdict === "inconclusive") {
    verdict = raw.verdict;
  } else {
    // Map from Gaia Backend prediction/status/details
    const pred = String(raw.prediction || raw.status || raw.details?.verdict || "").toLowerCase();
    if (pred.includes("ai") || pred.includes("synthetic") || pred.includes("fake")) {
      verdict = "ai";
    } else if (pred.includes("real") || pred.includes("human") || pred.includes("authentic")) {
      verdict = "human";
    } else {
      verdict = "inconclusive";
    }
  }

  const parsed: DetectionResult = { verdict };

  // 2. Score Calculation
  if (raw.score && typeof raw.score === "object" && typeof raw.score.value === "number") {
    const val = Math.max(0, Math.min(100, Math.round(raw.score.value)));
    const lbl = typeof raw.score.label === "string" && raw.score.label.trim() ? raw.score.label.trim() : "AI Probability";
    parsed.score = { value: val, label: lbl };
  } else {
    // Map from backend probability or confidence
    let scoreVal: number | undefined;
    if (typeof raw.details?.probability === "number") {
      scoreVal = raw.details.probability;
    } else if (typeof raw.details?.ai_score_percent === "number") {
      scoreVal = raw.details.ai_score_percent;
    } else if (typeof raw.confidence === "number") {
      scoreVal = verdict === "human" ? Math.max(0, 100 - raw.confidence) : raw.confidence;
    }

    if (typeof scoreVal === "number" && Number.isFinite(scoreVal)) {
      parsed.score = {
        value: Math.max(0, Math.min(100, Math.round(scoreVal))),
        label: "AI Probability",
      };
    }
  }

  // 3. Summary
  if (typeof raw.summary === "string" && raw.summary.trim()) {
    parsed.summary = raw.summary.trim();
  }

  // 4. Model / Detector Name
  const modelName = raw.detector_name || raw.model;
  if (typeof modelName === "string" && modelName.trim()) {
    parsed.model = modelName.trim();
  }

  // 5. Processing Time
  if (typeof raw.processingMs === "number" && Number.isFinite(raw.processingMs) && raw.processingMs >= 0) {
    parsed.processingMs = raw.processingMs;
  } else if (typeof raw.processing_time_sec === "number" && Number.isFinite(raw.processing_time_sec)) {
    parsed.processingMs = Math.round(raw.processing_time_sec * 1000);
  }

  // 6. Evidence Extraction
  let evidenceList: string[] = [];
  if (Array.isArray(raw.evidence)) {
    evidenceList = raw.evidence;
  } else if (Array.isArray(raw.details?.indicators)) {
    evidenceList = raw.details.indicators;
  } else if (Array.isArray(raw.details?.visual_indicators)) {
    evidenceList = raw.details.visual_indicators;
  }

  const cleanEvidence = evidenceList
    .filter((item): item is string => typeof item === "string" && !!item.trim())
    .map((item) => item.trim());

  if (cleanEvidence.length > 0) {
    parsed.evidence = cleanEvidence;
  }

  return parsed;
}

export async function analyzeContent(
  mode: DetectionMode,
  input: string | File,
  signal: AbortSignal
): Promise<DetectionResult> {
  const endpoint = detectionEndpoints[mode];
  if (!endpoint) throw new Error(`${mode.charAt(0).toUpperCase() + mode.slice(1)} detection is not connected yet.`);

  let response: Response;
  if (mode === "text") {
    if (typeof input === "string") {
      response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: input }),
        signal,
      });
    } else {
      // Document file upload fallback to /detect/document
      const body = new FormData();
      body.append("file", input);
      response = await fetch("/detect/document", {
        method: "POST",
        body,
        signal,
      });
    }
  } else {
    const body = new FormData();
    body.append("file", input);
    response = await fetch(endpoint, {
      method: "POST",
      body,
      signal,
    });
  }

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errJson = await response.json();
      if (errJson && typeof errJson.detail === "string") {
        errorDetail = errJson.detail;
      }
    } catch {
      // Ignore JSON parse errors on failure
    }
    if (errorDetail) {
      throw new Error(errorDetail);
    }
    throw new Error(
      response.status === 429
        ? "Too many requests. Please try again later."
        : "Analysis failed. Please try again."
    );
  }

  const rawData = await response.json();
  return parseDetectionResult(rawData);
}