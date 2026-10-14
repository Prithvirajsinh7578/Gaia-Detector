import { createFileRoute } from "@tanstack/react-router";
import { ArrowDown, ArrowUpRight, ScanLine } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DetectionWorkspace } from "@/components/detection-workspace";
import editorialPaper from "@/assets/gaia-editorial-paper.jpg";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [
    { title: "GAIA Detector — Know what you're looking at" },
    { name: "description", content: "Analyze text, images and videos with GAIA Detector. A clear, considered workspace for AI content detection." },
    { property: "og:title", content: "GAIA Detector — Content clarity" },
    { property: "og:description", content: "A simple workspace to analyze text, images and videos for AI-generated content." },
    { property: "og:type", content: "website" },
    { name: "twitter:card", content: "summary_large_image" },
  ] }),
  component: Index,
});

function Index() {
  function startAnalysis() {
    document.getElementById("analysis")?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block: "start" });
    document.getElementById("analysis-text")?.focus({ preventScroll: true });
  }

  return (
    <div className="site-shell">
      <header className="site-header grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
        <a href="/" aria-label="GAIA Detector home" className="brand flex min-w-0 items-center gap-3"><span className="brand-mark"><ScanLine className="size-5" /></span><span>GAIA<span className="brand-subtitle">DETECTOR</span></span></a>
        <Button variant="ghost" onClick={startAnalysis} className="h-11 gap-5">Workspace<ArrowUpRight className="size-4" /></Button>
      </header>
      <main>
        <section className="intro" aria-labelledby="intro-title">
          <img src={editorialPaper} width={1600} height={640} alt="" className="editorial-paper" fetchPriority="high" />
          <div className="intro-content"><p className="eyebrow mb-5 flex items-center gap-2"><span className="inline-block size-1.5 rounded-full bg-foreground" />GAIA DETECTOR</p><h1 id="intro-title">Know what you're<br /><em>looking at.</em></h1><p className="mt-5 text-base text-muted-foreground">Analyze text, images, and videos.</p><Button onClick={startAnalysis} className="mt-7 h-12 gap-6 px-5">Start Analysis<ArrowDown className="size-4" /></Button></div>
        </section>
        <div className="section-divider"><span /><span className="signal-line" /><span /></div>
        <DetectionWorkspace />
      </main>
      <footer className="site-footer grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4"><span className="text-xs text-muted-foreground">A clearer perspective.</span><span className="text-xs text-muted-foreground">GAIA DETECTOR<span className="ml-4">© 2026</span></span></footer>
    </div>
  );
}
