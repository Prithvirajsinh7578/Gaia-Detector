import { useState } from "react";
import { ArrowRight, ChevronDown, Maximize2, Minimize2, RotateCcw, X } from "lucide-react";
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
  fileName?: string;
  expanded: boolean;
  onExpand: () => void;
  onAnother: () => void;
  onRetry: () => void;
  onDismiss: () => void;
};

export function ResultReport({ mode, busy, error, result, text, preview, fileName, expanded, onExpand, onAnother, onRetry, onDismiss }: Props) {
  const [showEvidence, setShowEvidence] = useState(false);
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
            <div className="report-verdict">
              <span className="verdict-stamp" aria-hidden="true">{verdict.stamp}</span>
              <p className="report-label">Verdict</p>
              <h4>{verdict.label}</h4>
              {result.summary && <p className="report-summary">{result.summary}</p>}
            </div>
            {result.score && <div className="report-score" role="img" aria-label={`${result.score.label}: ${result.score.value}%`}><span style={{ width: `${result.score.value}%` }} /></div>}
            <figure className={`report-preview preview-${mode}`}>
              {mode === "text" ? <blockquote>{text.length > 420 ? `${text.slice(0, 420).trimEnd()}…` : text}</blockquote>
                : mode === "image" ? preview && <img src={preview} alt="Analyzed image" />
                : preview && <video src={preview} controls preload="metadata" aria-label="Analyzed video" />}
              <figcaption>{mode === "text" ? `${text.trim().split(/\s+/).length.toLocaleString()} words` : fileName}</figcaption>
            </figure>
            {details.length > 0 && <dl className="report-details">{details.map(item => <div key={item.term}><dt>{item.term}</dt><dd>{item.value}</dd></div>)}</dl>}
            {result.evidence && <div className="report-evidence">
              <button type="button" onClick={() => setShowEvidence(value => !value)} aria-expanded={showEvidence}>Evidence <span className="text-panel-muted">({result.evidence.length})</span><ChevronDown className={showEvidence ? "rotate-180" : ""} /></button>
              {showEvidence && <ol>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ol>}
            </div>}
            <div className="report-actions"><Button className="h-11" onClick={onAnother}>Analyze Another<ArrowRight /></Button></div>
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
