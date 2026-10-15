import { useEffect, useRef, useState } from "react";
import { ArrowRight, ArrowUpRight, Check, CircleAlert, FileText, Image, LoaderCircle, ScanLine, Upload, Video, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ResultReport } from "@/components/result-report";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { analyzeContent, fileRules, validateFile, type DetectionMode, type DetectionResult } from "@/lib/detection";


export function DetectionWorkspace() {
  const [mode, setMode] = useState<DetectionMode>("text");
  const [text, setText] = useState("");
  const [files, setFiles] = useState<Partial<Record<"image" | "video", File>>>({});
  const [preview, setPreview] = useState("");
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [detectorStatus, setDetectorStatus] = useState<"connected" | "connecting" | "offline">("connecting");
  const inputRef = useRef<HTMLInputElement>(null);
  const controller = useRef<AbortController | null>(null);
  const file = mode === "text" ? undefined : files[mode];
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;

  useEffect(() => {
    let isMounted = true;
    async function checkHealth() {
      try {
        const res = await fetch("/health");
        if (res.ok && isMounted) {
          setDetectorStatus("connected");
          return;
        }
      } catch {
        // ignore
      }
      if (isMounted) setDetectorStatus("offline");
    }
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    if (!file) { setPreview(""); return; }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  useEffect(() => () => controller.current?.abort(), []);
  useEffect(() => {
    function select(event: Event) {
      const next = (event as CustomEvent<DetectionMode>).detail;
      if (next !== "text" && next !== "image" && next !== "video") return;
      setMode(current => { if (current !== next) { invalidate(); setDragging(false); } return next; });
    }
    window.addEventListener("gaia:select-mode", select);
    return () => window.removeEventListener("gaia:select-mode", select);
  }, []);

  function invalidate() {
    controller.current?.abort();
    controller.current = null;
    setBusy(false);
    setResult(null);
    setExpanded(false);
    setError("");
  }

  function chooseFile(next: File | undefined) {
    if (!next || mode === "text") return;
    invalidate();
    const issue = validateFile(next, mode);
    if (issue) { setError(issue); return; }
    setFiles(current => ({ ...current, [mode]: next }));
  }

  function clear() {
    invalidate();
    if (mode === "text") setText("");
    else setFiles(current => ({ ...current, [mode]: undefined }));
    if (inputRef.current) inputRef.current.value = "";
  }

  async function analyze() {
    if (controller.current) return;
    setError(""); setResult(null);
    const value = mode === "text" ? text.trim() : file;
    if (!value) { setError(mode === "text" ? "Add some text to analyze." : `Choose a ${mode} first.`); return; }
    const active = new AbortController();
    controller.current = active; setBusy(true);
    try {
      const next = await analyzeContent(mode, value, active.signal);
      if (!active.signal.aborted && controller.current === active) setResult(next);
    } catch (issue) {
      if (!active.signal.aborted && controller.current === active) setError(issue instanceof Error ? issue.message : "Analysis failed. Please try again.");
    } finally {
      if (controller.current === active) { controller.current = null; setBusy(false); }
    }
  }

  return (
    <section id="analysis" aria-labelledby="workspace-title" className="workspace scroll-mt-6">
      <div className="mb-6 grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
        <div className="min-w-0"><p className="eyebrow mb-2">THE WORKSPACE</p><h2 id="workspace-title" className="text-2xl font-medium">A little more clarity.</h2></div>
        {detectorStatus === "connected" ? (
          <span className="hidden items-center gap-2 text-xs text-emerald-400 font-medium sm:flex">
            <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
            All AI Detectors Connected
          </span>
        ) : detectorStatus === "connecting" ? (
          <span className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex">
            <span className="size-1.5 rounded-full bg-muted-foreground animate-pulse" />
            Connecting to detectors…
          </span>
        ) : (
          <span className="hidden items-center gap-2 text-xs text-amber-400 font-medium sm:flex">
            <span className="size-1.5 rounded-full bg-amber-500" />
            Detectors offline
          </span>
        )}
      </div>
      <div className={`analysis-grid ${expanded && result ? "is-expanded" : ""}`}>
        <div className="min-w-0">
          <Tabs value={mode} onValueChange={value => { invalidate(); setDragging(false); setMode(value as DetectionMode); }}>
            <TabsList aria-label="Content type" className="mode-tabs grid w-full grid-cols-3 rounded-none bg-transparent p-0">
              <TabsTrigger value="text"><FileText />TEXT</TabsTrigger>
              <TabsTrigger value="image"><Image />IMAGE</TabsTrigger>
              <TabsTrigger value="video"><Video />VIDEO</TabsTrigger>
            </TabsList>
            <TabsContent value="text" className="mt-0">
              <div className="input-area">
                <div className="flex items-center justify-between gap-4"><label htmlFor="analysis-text" className="text-sm font-medium">Your text</label><Button variant="ghost" size="sm" onClick={clear} disabled={!text} className="h-11 text-muted-foreground">Clear <X className="size-3" /></Button></div>
                <textarea id="analysis-text" value={text} onChange={event => { invalidate(); setText(event.target.value); }} placeholder="Paste your text here…" className="text-editor" spellCheck={false} />
                <div className="flex justify-between gap-4 text-xs text-muted-foreground"><span>{words.toLocaleString()} {words === 1 ? "word" : "words"}</span><span>{text.length.toLocaleString()} characters</span></div>
              </div>
            </TabsContent>
            {(["image", "video"] as const).map(kind => (
              <TabsContent key={kind} value={kind} className="mt-0">
                <div className={`input-area upload-area ${dragging ? "is-dragging" : ""}`} onDragOver={event => { event.preventDefault(); setDragging(true); }} onDragLeave={event => { if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setDragging(false); }} onDrop={event => { event.preventDefault(); setDragging(false); if (event.dataTransfer.files.length > 1) { invalidate(); setError("Choose one file at a time."); return; } chooseFile(event.dataTransfer.files[0]); }}>
                  <input ref={mode === kind ? inputRef : undefined} type="file" aria-label={`Upload ${kind}`} className="sr-only" accept={fileRules[kind].types.join(",")} onChange={event => { chooseFile(event.target.files?.[0]); event.target.value = ""; }} />
                  {file ? <><div className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3"><span className="truncate text-sm font-medium">{file.name}</span><Button variant="ghost" size="icon" className="size-11" aria-label={`Remove ${kind}`} title={`Remove ${kind}`} onClick={clear}><X /></Button></div><div className="media-preview">{preview && (kind === "image" ? <img src={preview} alt="Selected image" /> : <video key={preview} src={preview} controls preload="metadata" onError={() => setError("Preview unavailable in this browser. You can still select this file.")} />)}</div><p className="text-xs text-muted-foreground">{(file.size / (1024 * 1024)).toFixed(2)} MB</p></> : <div className="flex flex-1 flex-col items-center justify-center text-center"><div className="mb-5 grid size-12 place-items-center rounded-full bg-secondary"><Upload className="size-5" /></div><p className="mb-2 text-base">Drop your {kind} here</p><p className="mb-5 text-xs text-muted-foreground">{fileRules[kind].label}</p><Button variant="outline" className="h-11" onClick={() => inputRef.current?.click()}>Choose {kind}<ArrowUpRight /></Button></div>}
                </div>
              </TabsContent>
            ))}
          </Tabs>
          <div className="analysis-actions grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3"><span className="text-xs text-muted-foreground">{mode === "text" ? "Text stays here until you analyze." : "Local preview only. No file uploaded."}</span><Button onClick={analyze} disabled={busy || (mode === "text" ? !text.trim() : !file)} className="h-12 px-6">{busy ? <><LoaderCircle />Analyzing…</> : <>Analyze {mode}<ArrowRight /></>}</Button></div>
        </div>
        <ResultReport mode={mode} busy={busy} error={error} result={result} text={text} preview={preview} fileName={file?.name} expanded={expanded} onExpand={() => setExpanded(value => !value)} onAnother={clear} onRetry={analyze} onDismiss={() => setError("")} />
      </div>
      <div className="bento-strip" role="group" aria-label="Formats">
        {(["text", "image", "video"] as const).map((kind, index) => (
          <button key={kind} type="button" className={`bento-tile ${mode === kind ? "is-active" : ""}`} aria-pressed={mode === kind} onClick={() => { if (mode !== kind) { invalidate(); setDragging(false); setMode(kind); } }}>
            <span className="bento-index">0{index + 1}</span>
            <span className="bento-name">{kind.charAt(0).toUpperCase() + kind.slice(1)}</span>
            <span className="text-xs text-muted-foreground">{kind === "text" ? "No length limit" : fileRules[kind].label}</span>
          </button>
        ))}
      </div>
      <p className="mt-4 text-xs sm:hidden">
        {detectorStatus === "connected" ? (
          <span className="text-emerald-400 font-medium">All AI detectors connected and active.</span>
        ) : detectorStatus === "connecting" ? (
          <span className="text-muted-foreground">Connecting to detectors…</span>
        ) : (
          <span className="text-amber-400 font-medium">Detectors offline.</span>
        )}
      </p>
    </section>
  );
}