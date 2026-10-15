import { renderToString } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { ResultReport } from "@/components/result-report";

const base = { mode: "text" as const, busy: false, error: "", result: null, text: "Some words here", preview: "", expanded: false, onExpand() {}, onAnother() {}, onRetry() {}, onDismiss() {} };

describe("ResultReport", () => {
  it("shows the empty state", () => { expect(renderToString(<ResultReport {...base} />)).toContain("Nothing to read. Yet."); });
  it("shows no retry when the detector is not connected", () => {
    const html = renderToString(<ResultReport {...base} error="Text detection is not connected yet." />);
    expect(html).toContain("Detector unavailable"); expect(html).not.toContain("Try again");
  });
  it("renders only provided details", () => {
    const html = renderToString(<ResultReport {...base} result={{ verdict: "inconclusive" }} />);
    expect(html).toContain("Inconclusive"); expect(html).not.toContain("%"); expect(html).not.toContain("Evidence");
  });
  it("renders real score and evidence", () => {
    const html = renderToString(<ResultReport {...base} result={{ verdict: "ai", score: { value: 82, label: "AI likelihood" }, evidence: ["x"] }} />);
    expect(html).toContain("82%"); expect(html).toContain("Evidence");
  });
});
