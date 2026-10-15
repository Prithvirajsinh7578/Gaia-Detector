import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { checkBackendHealth } from '../../services/api';
import {
  HiOutlineDocumentText,
  HiOutlinePhotograph,
  HiOutlineVideoCamera,
  HiOutlineDocumentSearch,
  HiOutlineShieldCheck,
  HiOutlineCheckCircle,
  HiOutlineArrowRight,
  HiOutlineChip
} from 'react-icons/hi';

export default function Dashboard() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkBackendHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }));
  }, []);

  const modalities = [
    { title: 'Text Authenticity', desc: '18-feature RF + RoBERTa Transformer', icon: HiOutlineDocumentText, tab: 'text' },
    { title: 'Image Authenticity', desc: 'Zero-shot CLIP visual classifier', icon: HiOutlinePhotograph, tab: 'image' },
    { title: 'Video Authenticity', desc: '21-feature spatio-temporal RF + HuggingFace', icon: HiOutlineVideoCamera, tab: 'video' },
    { title: 'Document Scanner', desc: 'Multi-page PDF & DOCX extraction pipeline', icon: HiOutlineDocumentSearch, tab: 'document' },
  ];

  return (
    <div className="min-h-screen pt-28 pb-16 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 font-heading">
            Authenticity <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">Dashboard</span>
          </h1>
          <p className="text-gray-400 text-sm">
            Operational status and multi-modal AI detection capabilities.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full glass border border-white/10 text-xs">
          <span className={`w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
          <span className="text-gray-300">
            Backend API: {health?.status === 'healthy' ? 'Connected & Operational' : 'Connecting...'}
          </span>
        </div>
      </div>

      {/* Grid of Modalities */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {modalities.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="glass rounded-2xl p-6 border border-white/10 hover:border-primary-cyan/40 transition-all flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-cyan/10 to-primary-purple/10 border border-white/10 flex items-center justify-center text-primary-cyan mb-4">
                  <Icon className="w-6 h-6" />
                </div>
                <h3 className="text-white font-semibold text-base mb-1">{m.title}</h3>
                <p className="text-gray-400 text-xs mb-4">{m.desc}</p>
              </div>
              <Link
                to="/upload"
                className="text-xs text-primary-cyan hover:underline inline-flex items-center gap-1 font-medium"
              >
                Launch Detector <HiOutlineArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          );
        })}
      </div>

      {/* Quick Launch Banner */}
      <div className="glass rounded-3xl p-8 md:p-10 border border-white/10 relative overflow-hidden">
        <div className="max-w-2xl relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-cyan/10 border border-primary-cyan/20 text-primary-cyan text-xs font-semibold uppercase tracking-wider mb-4">
            <HiOutlineShieldCheck className="w-4 h-4" />
            Active Multi-Modal Engine
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 font-heading">
            Detect AI-generated text, documents, images, and videos in seconds
          </h2>
          <p className="text-gray-300 text-sm mb-6 leading-relaxed">
            Gaia combines custom machine-learning models, deep transformer representations, and optional commercial verification APIs into a unified ensemble architecture.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link
              to="/upload"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-semibold hover:opacity-90 transition-all shadow-lg text-sm inline-flex items-center gap-2"
            >
              Start Analysis Now
              <HiOutlineArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/history"
              className="px-6 py-3 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold transition-all text-sm inline-flex items-center gap-2"
            >
              View Detection History
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
