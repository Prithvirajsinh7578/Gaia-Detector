export type DetectionMode = "text" | "image" | "video";
export type DetectionResult = {
  verdict: "ai" | "human" | "inconclusive";
  score?: { value: number; label: string };
  summary?: string;
  model?: string;
  processingMs?: number;
  evidence?: string[];
};

// Configure only verified, same-origin server endpoints. Never put provider keys here.
export const detectionEndpoints: Partial<Record<DetectionMode, string>> = { text: "/__qa/detect" };
export const fileRules = {
  image: { types: ["image/jpeg", "image/png", "image/webp"], extensions: ["jpg", "jpeg", "png", "webp"], maxBytes: 20 * 1024 * 1024, label: "JPG, PNG, WEBP · Up to 20 MB" },
  video: { types: ["video/mp4", "video/webm", "video/quicktime"], extensions: ["mp4", "webm", "mov"], maxBytes: 100 * 1024 * 1024, label: "MP4, WEBM, MOV · Up to 100 MB" },
};

export function validateFile(file: File, mode: "image" | "video"): string | null {
  const rules = fileRules[mode];
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";
  if (!rules.types.includes(file.type) || !rules.extensions.includes(extension)) return `Choose a supported ${mode} file.`;
  if (file.size === 0) return "This file is empty.";
  if (file.size > rules.maxBytes) return `File too large. Maximum ${mode === "image" ? "20" : "100"} MB.`;
  return null;
}

export function parseDetectionResult(data: unknown): DetectionResult {
  if (!data || typeof data !== "object") throw new Error("The detector returned an invalid result.");
  const result = data as Record<string, unknown>;
  if (result.verdict !== "ai" && result.verdict !== "human" && result.verdict !== "inconclusive") throw new Error("The detector returned an invalid result.");
  const parsed: DetectionResult = { verdict: result.verdict };
  if (result.score !== undefined) {
    if (!result.score || typeof result.score !== "object") throw new Error("The detector returned an invalid score.");
    const score = result.score as { value?: unknown; label?: unknown };
    if (typeof score.value !== "number" || !Number.isFinite(score.value) || score.value < 0 || score.value > 100 || typeof score.label !== "string" || !score.label.trim()) throw new Error("The detector returned an invalid score.");
    parsed.score = { value: score.value, label: score.label };
  }
  // Optional details: shown only when the detector actually returns them.
  if (typeof result.summary === "string" && result.summary.trim()) parsed.summary = result.summary.trim();
  if (typeof result.model === "string" && result.model.trim()) parsed.model = result.model.trim();
  if (typeof result.processingMs === "number" && Number.isFinite(result.processingMs) && result.processingMs >= 0) parsed.processingMs = result.processingMs;
  if (Array.isArray(result.evidence)) {
    const evidence = result.evidence.filter((item): item is string => typeof item === "string" && !!item.trim()).map(item => item.trim());
    if (evidence.length) parsed.evidence = evidence;
  }
  return parsed;
}

export async function analyzeContent(mode: DetectionMode, input: string | File, signal: AbortSignal): Promise<DetectionResult> {
  const endpoint = detectionEndpoints[mode];
  if (!endpoint) throw new Error(`${mode.charAt(0).toUpperCase() + mode.slice(1)} detection is not connected yet.`);
  const body = new FormData();
  body.set("mode", mode);
  body.set(typeof input === "string" ? "text" : "file", input);
  const response = await fetch(endpoint, { method: "POST", body, signal });
  if (!response.ok) throw new Error(response.status === 429 ? "Too many requests. Please try again later." : "Analysis failed. Please try again.");
  return parseDetectionResult(await response.json());
}