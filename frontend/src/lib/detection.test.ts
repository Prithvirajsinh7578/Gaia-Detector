import { describe, expect, it, vi } from "vitest";
import { analyzeContent, parseDetectionResult, validateFile } from "./detection";

describe("Detection contract", () => {
  it("never fabricates a result when disconnected", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    for (const mode of ["text", "image", "video"] as const) {
      await expect(analyzeContent(mode, "content", new AbortController().signal)).rejects.toThrow("not connected");
    }
    expect(fetchSpy).not.toHaveBeenCalled();
    fetchSpy.mockRestore();
  });
  it("validates format, empty files and size", () => {
    expect(validateFile(new File(["image"], "photo.png", { type: "image/png" }), "image")).toBeNull();
    expect(validateFile(new File(["image"], "photo.svg", { type: "image/svg+xml" }), "image")).toContain("supported");
    expect(validateFile(new File([], "empty.mp4", { type: "video/mp4" }), "video")).toContain("empty");
    const file = new File(["image"], "photo.png", { type: "image/png" });
    Object.defineProperty(file, "size", { value: 21 * 1024 * 1024 });
    expect(validateFile(file, "image")).toContain("too large");
  });
  it("preserves real results and optional scores", () => {
    expect(parseDetectionResult({ verdict: "human" })).toEqual({ verdict: "human" });
    expect(parseDetectionResult({ verdict: "ai", score: { value: 82, label: "AI likelihood" } }).score?.value).toBe(82);
    expect(() => parseDetectionResult({ verdict: "made-up" })).toThrow();
    expect(() => parseDetectionResult({ verdict: "ai", score: { value: 150, label: "Confidence" } })).toThrow();
  });
});
describe("optional report details", () => {
  it("keeps only real, well-formed details", () => {
    const r = parseDetectionResult({ verdict: "human", model: "v2", processingMs: 840, evidence: ["a", 3, " "], summary: "" });
    expect(r).toEqual({ verdict: "human", model: "v2", processingMs: 840, evidence: ["a"] });
  });
});
