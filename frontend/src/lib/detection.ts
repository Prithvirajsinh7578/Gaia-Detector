export type DetectionMode = "text" | "image" | "video";

export type ModelResult = {
  id: string;
  name: string;
  category?: string;
  verdict?: string;
  aiProbability?: number;
  confidence?: string;
  latencyMs?: number;
  status?: string;
  details?: Record<string, any>;
};

export type ConsensusInfo = {
  agreement?: string;
  agreementScore?: number;
  activeDetectors?: number;
  totalDetectors?: number;
  discrepancy?: number;
  inconclusiveReason?: string;
};

export type DetectionResult = {
  verdict: "ai" | "human" | "inconclusive";
  score?: { value: number; label: string };
  summary?: string;
  model?: string;
  processingMs?: number;
  evidence?: string[];
  models?: ModelResult[];
  consensus?: ConsensusInfo;
  features?: Record<string, number | string>;
  details?: Record<string, any>;
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
    label: "JPG, PNG, WEBP · No size limit",
  },
  video: {
    types: ["video/mp4", "video/webm", "video/quicktime"],
    extensions: ["mp4", "webm", "mov"],
    label: "MP4, WEBM, MOV · No size limit",
  },
};

export function validateFile(file: File, mode: "image" | "video"): string | null {
  const rules = fileRules[mode];
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  const typeMatches = file.type ? rules.types.includes(file.type) : false;
  const extMatches = rules.extensions.includes(extension);
  if (!typeMatches && !extMatches) return `Choose a supported ${mode} file.`;
  if (file.size === 0) return "This file is empty.";
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
    } else if (typeof raw.details?.ai_probability === "number") {
      scoreVal = raw.details.ai_probability;
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

  // 7. Ensemble Models Breakdown
  const models: ModelResult[] = [];
  const indDetectors = raw.details?.individual_detectors;
  if (indDetectors && typeof indDetectors === "object") {
    for (const [key, val] of Object.entries(indDetectors)) {
      if (val && typeof val === "object") {
        const m = val as Record<string, any>;
        const prob = typeof m.ai_probability === "number" ? Math.round(m.ai_probability * 10) / 10 : undefined;
        models.push({
          id: key,
          name: m.name || key,
          category: m.category,
          verdict: m.verdict,
          aiProbability: prob,
          confidence: m.confidence,
          latencyMs: typeof m.latency_ms === "number" ? Math.round(m.latency_ms) : undefined,
          status: m.status,
          details: m.details || m.metadata,
        });
      }
    }
  } else if (Array.isArray(raw.details?.raw_scores)) {
    for (const item of raw.details.raw_scores) {
      if (item && typeof item === "object") {
        const isAI = String(item.label || "").toLowerCase().includes("ai");
        models.push({
          id: isAI ? "clip_ai" : "clip_real",
          name: item.label,
          verdict: isAI ? "AI Generated" : "Real Photo",
          aiProbability: Math.round((Number(item.score) || 0) * 1000) / 10,
          status: "success",
        });
      }
    }
  }

  if (models.length > 0) {
    parsed.models = models;
  }

  // 8. Consensus Information
  if (raw.details?.consensus && typeof raw.details.consensus === "object") {
    const c = raw.details.consensus as Record<string, any>;
    parsed.consensus = {
      agreement: c.agreement,
      agreementScore: typeof c.agreement_score === "number" ? c.agreement_score : undefined,
      activeDetectors: c.active_detectors,
      totalDetectors: c.total_detectors,
      discrepancy: typeof c.discrepancy === "number" ? Math.round(c.discrepancy * 10) / 10 : undefined,
      inconclusiveReason: c.inconclusive_reason || undefined,
    };
  }

  // 9. Quantitative Feature Metrics
  const rawFeatures = raw.details?.features || raw.details?.summary_features || raw.details?.detailed_features;
  if (rawFeatures && typeof rawFeatures === "object") {
    const featMap: Record<string, number | string> = {};
    for (const [k, v] of Object.entries(rawFeatures)) {
      if (typeof v === "number") {
        featMap[k] = Math.round(v * 100) / 100;
      } else if (typeof v === "string" || typeof v === "boolean") {
        featMap[k] = String(v);
      }
    }
    parsed.features = featMap;
  }

  // 10. Raw Details
  if (raw.details && typeof raw.details === "object") {
    parsed.details = raw.details;
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