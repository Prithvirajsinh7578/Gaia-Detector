import { useState } from "react";
import { ArrowRight, ChevronDown, Maximize2, Minimize2, RotateCcw, SlidersHorizontal, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { DetectionMode, DetectionResult } from "@/lib/detection";

const verdicts = {
  ai: { label: "Likely AI-generated", stamp: "AI", tone: "is-ai" },
  human: { label: "Likely human-created", stamp: "Human", tone: "is-human" },
  inconclusive: { label: "Inconclusive", stamp: "Unclear", tone: "is-unclear" },
} as const;

type Props = {
  mode: DetectionMode;
  busy: boolean;
  error: string;
  result: DetectionResult | null;
  text: string;
  preview: string;
  fileName?: string | undefined;
  expanded: boolean;
  onExpand: () => void;
  onAnother: () => void;
  onRetry: () => void;
  onDismiss: () => void;
};

function formatFeatureName(key: string): string {
  const spaced = key.replace(/([A-Z])/g, " $1").replace(/_/g, " ");
  return spaced.charAt(0).toUpperCase() + spaced.slice(1).trim();
}

export function ResultReport({ mode, busy, error, result, text, preview, fileName, expanded, onExpand, onAnother, onRetry, onDismiss }: Props) {
  const [showEvidence, setShowEvidence] = useState(false);
  const [showDetailedReport, setShowDetailedReport] = useState(false);
  const status = busy ? "Analyzing" : result ? "Complete" : error ? "Failed" : "Ready";
  const unavailable = error.includes("not connected");
  const verdict = result ? verdicts[result.verdict] : null;
  const details = result ? [
    result.score && { term: result.score.label, value: `${result.score.value}%` },
    result.processingMs !== undefined && { term: "Processing", value: result.processingMs < 1000 ? `${Math.round(result.processingMs)} ms` : `${(result.processingMs / 1000).toFixed(1)} s` },
    result.model && { term: "Detector", value: result.model },
  ].filter(Boolean) as { term: string; value: string }[] : [];

  return (
    <aside className={`result-panel report ${result ? "has-result" : ""} ${verdict?.tone ?? ""}`} aria-labelledby="result-title" aria-busy={busy}>
      <header className="report-head">
        <h3 id="result-title" className="report-kicker">GAIA <span aria-hidden="true">/</span> Analysis report</h3>
        <div className="flex items-center gap-3">
          <span className="report-meta">{mode}</span>
          <span className={`report-status status-${status.toLowerCase()}`}><span aria-hidden="true" />{status}</span>
          {result && <button type="button" className="report-icon" onClick={onExpand} aria-expanded={expanded} aria-label={expanded ? "Collapse report" : "Expand report"}>{expanded ? <Minimize2 /> : <Maximize2 />}</button>}
        </div>
      </header>

      <div className="report-body" aria-live="polite" aria-atomic="true">
        {result && verdict ? (
          <div className="report-result">
            {/* Verdict, Stamp, and Short Summary */}
            <div className="report-verdict">
              <span className="verdict-stamp" aria-hidden="true">{verdict.stamp}</span>
              <p className="report-label">Verdict</p>
              <h4>{verdict.label}</h4>
              {result.summary && <p className="report-summary">{result.summary}</p>}
            </div>

            {/* Overall Score Bar */}
            {result.score && (
              <div className="report-score" role="img" aria-label={`${result.score.label}: ${result.score.value}%`}>
                <span style={{ width: `${result.score.value}%` }} />
              </div>
            )}

            {/* Shorter Version: All Models' Results */}
            {result.models && result.models.length > 0 && (
              <div className="space-y-2 pt-1">
                <p className="report-label">Ensemble Models Breakdown</p>
                <div className="grid gap-2">
                  {result.models.map((m) => {
                    const prob = m.aiProbability;
                    const isStandby = m.status === "unconfigured" || m.status === "failed";
                    return (
                      <div
                        key={m.id}
                        className="p-2.5 rounded-sm border border-border bg-secondary/50 flex items-center justify-between gap-3 text-xs"
                      >
                        <div className="min-w-0 flex-1">
                          <div className="font-medium truncate text-foreground">{m.name}</div>
                          <div className="text-[11px] text-muted-foreground truncate">
                            {isStandby
                              ? "Commercial API (Standby)"
                              : m.verdict || (prob !== undefined ? (prob >= 60 ? "Likely AI" : prob <= 40 ? "Likely Real" : "Inconclusive") : "Active")}
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          {prob !== undefined && !isStandby ? (
                            <span
                              className={`inline-block font-mono font-bold text-xs px-2 py-0.5 rounded-sm ${
                                prob >= 60
                                  ? "text-amber-400 bg-amber-950/40 border border-amber-800/40"
                                  : prob <= 40
                                  ? "text-emerald-400 bg-emerald-950/40 border border-emerald-800/40"
                                  : "text-muted-foreground bg-muted border border-border"
                              }`}
                            >
                              {prob}% AI
                            </span>
                          ) : (
                            <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                              {m.status || "Standby"}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Media Preview */}
            <figure className={`report-preview preview-${mode}`}>
              {mode === "text" ? <blockquote>{text.length > 420 ? `${text.slice(0, 420).trimEnd()}…` : text}</blockquote>
                : mode === "image" ? preview && <img src={preview} alt="Analyzed image" />
                : preview && <video src={preview} controls preload="metadata" aria-label="Analyzed video" />}
              <figcaption>{mode === "text" ? `${text.trim().split(/\s+/).length.toLocaleString()} words` : fileName}</figcaption>
            </figure>

            {/* Overview Details (Score, Processing time, Primary detector) */}
            {details.length > 0 && <dl className="report-details">{details.map(item => <div key={item.term}><dt>{item.term}</dt><dd>{item.value}</dd></div>)}</dl>}

            {/* Option to See Detailed Report in the Same UI */}
            <div className="pt-2 border-t border-border flex items-center justify-between gap-3">
              <Button
                type="button"
                variant={showDetailedReport ? "secondary" : "outline"}
                size="sm"
                className="h-10 gap-2 text-xs font-medium"
                onClick={() => setShowDetailedReport(prev => !prev)}
              >
                <SlidersHorizontal className="size-3.5" />
                {showDetailedReport ? "Hide Detailed Report" : "View Detailed Report"}
                <ChevronDown className={`size-3.5 transition-transform ${showDetailedReport ? "rotate-180" : ""}`} />
              </Button>
              <span className="text-[11px] text-muted-foreground">
                {showDetailedReport ? "Deep Diagnostics Active" : "Click for deep metrics"}
              </span>
            </div>

            {/* Detailed Report Section (Rendered in the Same UI) */}
            {showDetailedReport && (
              <div className="space-y-4 pt-2 border-t border-dashed border-border">
                {/* Ensemble Consensus Card */}
                {result.consensus && (
                  <div className="p-3 rounded-sm border border-border bg-secondary/40 space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[10px] uppercase font-semibold tracking-wider text-muted-foreground">
                        Ensemble Consensus
                      </span>
                      <span className="text-xs font-mono font-medium text-primary">
                        {result.consensus.agreement || "Synthesized"}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <span className="text-muted-foreground text-[11px]">Active Models:</span>{" "}
                        <span className="font-medium">
                          {result.consensus.activeDetectors ?? "Multi"} / {result.consensus.totalDetectors ?? "3"}
                        </span>
                      </div>
                      {result.consensus.discrepancy !== undefined && (
                        <div>
                          <span className="text-muted-foreground text-[11px]">Discrepancy:</span>{" "}
                          <span className="font-medium font-mono">{result.consensus.discrepancy}%</span>
                        </div>
                      )}
                    </div>
                    {result.consensus.inconclusiveReason && (
                      <p className="text-[11px] text-muted-foreground italic border-t border-border/50 pt-1.5">
                        {result.consensus.inconclusiveReason}
                      </p>
                    )}
                  </div>
                )}

                {/* Extracted Quantitative Features */}
                {result.features && Object.keys(result.features).length > 0 && (
                  <div className="space-y-2">
                    <p className="report-label">Extracted Feature Telemetry</p>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {Object.entries(result.features).map(([key, val]) => (
                        <div key={key} className="p-2 rounded-sm border border-border bg-secondary/30 text-xs">
                          <div className="text-[10px] text-muted-foreground truncate" title={key}>
                            {formatFeatureName(key)}
                          </div>
                          <div className="font-mono font-medium text-foreground mt-0.5 truncate">
                            {String(val)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Full Forensic Evidence List */}
                {result.evidence && result.evidence.length > 0 && (
                  <div className="space-y-2">
                    <p className="report-label">Forensic Indicators ({result.evidence.length})</p>
                    <ol className="list-decimal pl-5 text-xs text-muted-foreground space-y-1.5 leading-relaxed">
                      {result.evidence.map((item, index) => (
                        <li key={index} className="text-foreground/90">
                          {item}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            )}

            {/* Quick Evidence Drawer (shown when detailed report is collapsed) */}
            {!showDetailedReport && result.evidence && (
              <div className="report-evidence">
                <button type="button" onClick={() => setShowEvidence(value => !value)} aria-expanded={showEvidence}>
                  Evidence <span className="text-panel-muted">({result.evidence.length})</span>
                  <ChevronDown className={showEvidence ? "rotate-180" : ""} />
                </button>
                {showEvidence && <ol>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ol>}
              </div>
            )}

            <div className="report-actions">
              <Button className="h-11" onClick={onAnother}>Analyze Another<ArrowRight /></Button>
            </div>
          </div>
        ) : error ? (
          <div className="report-state">
            <span className="verdict-stamp is-error" aria-hidden="true">{unavailable ? "Offline" : "Error"}</span>
            <h4>{unavailable ? "Detector unavailable" : "Unable to analyze"}</h4>
            <p role="alert">{error}</p>
            <div className="mt-6 flex flex-wrap gap-2">
              {!unavailable && <Button className="h-11" onClick={onRetry}><RotateCcw />Try again</Button>}
              <Button variant="ghost" className="h-11" onClick={onDismiss}>Dismiss<X /></Button>
            </div>
          </div>
        ) : (
          <div className="report-state">
            <svg className={`report-sheet ${busy ? "is-reading" : ""}`} viewBox="0 0 120 92" aria-hidden="true">
              <rect x="22" y="8" width="70" height="80" rx="1" className="sheet-back" />
              <rect x="14" y="4" width="70" height="80" rx="1" className="sheet-front" />
              <path d="M26 22h38M26 32h46M26 42h30M26 52h42M26 62h24" className="sheet-lines" />
              <circle cx="96" cy="70" r="13" className="sheet-seal" />
            </svg>
            <h4>{busy ? `Reading your ${mode}` : "Nothing to read. Yet."}</h4>
            <p>{busy ? "Waiting for the detector…" : "Your analysis will appear here."}</p>
            {busy && <div className="report-progress" role="progressbar" aria-label="Analysis in progress"><span /></div>}
          </div>
        )}
      </div>

      <footer className="report-foot">{result ? "An estimate, not proof of origin." : busy ? "Don't close this page." : "Ready when you are"}</footer>
    </aside>
  );
}
