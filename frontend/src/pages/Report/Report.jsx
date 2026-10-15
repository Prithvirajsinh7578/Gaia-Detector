import { Link } from 'react-router-dom';
import DetectionPreview from '../../components/DetectionPreview/DetectionPreview';
import { HiOutlineArrowLeft, HiOutlineDownload, HiOutlineShare } from 'react-icons/hi';

export default function Report() {
  return (
    <div className="min-h-screen pt-28 pb-16 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <Link
            to="/upload"
            className="inline-flex items-center gap-1.5 text-xs text-primary-cyan hover:underline mb-2 font-medium"
          >
            <HiOutlineArrowLeft className="w-4 h-4" /> Back to Workbench
          </Link>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 font-heading">
            Authenticity <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">Inspection Report</span>
          </h1>
          <p className="text-gray-400 text-sm">
            Comprehensive diagnostic summary of artifact features and multi-modal ensemble metrics.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white text-xs font-semibold transition-all inline-flex items-center gap-2"
          >
            <HiOutlineDownload className="w-4 h-4" /> Export Report
          </button>
        </div>
      </div>

      <DetectionPreview />
    </div>
  );
}
