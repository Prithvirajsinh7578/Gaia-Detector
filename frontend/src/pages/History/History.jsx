import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDetectionHistory } from '../../services/api';
import { HiOutlineClock, HiOutlineDocumentSearch, HiOutlineShieldCheck, HiOutlineArrowRight } from 'react-icons/hi';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        const data = await getDetectionHistory();
        setHistory(Array.isArray(data) ? data : (data.items || []));
      } catch (err) {
        // If MongoDB is not configured or user is anonymous, history returns empty
        setError(null);
        setHistory([]);
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, []);

  return (
    <div className="min-h-screen pt-28 pb-16 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 font-heading">
            Detection <span className="bg-gradient-to-r from-primary-cyan to-primary-purple bg-clip-text text-transparent">History</span>
          </h1>
          <p className="text-gray-400 text-sm">
            Review your previously analyzed text, documents, images, and videos.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white text-sm font-semibold hover:opacity-90 transition-all shadow-lg w-fit"
        >
          New Analysis
          <HiOutlineArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {loading ? (
        <div className="glass rounded-2xl p-12 text-center">
          <div className="w-8 h-8 border-2 border-primary-cyan/30 border-t-primary-cyan rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Loading detection records...</p>
        </div>
      ) : history.length > 0 ? (
        <div className="glass rounded-2xl overflow-hidden border border-white/10">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400 uppercase text-xs tracking-wider border-b border-white/10">
                <tr>
                  <th className="px-6 py-4">File / Content</th>
                  <th className="px-6 py-4">Modality</th>
                  <th className="px-6 py-4">Verdict</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {history.map((item, idx) => (
                  <tr key={item.id || idx} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-medium text-white">{item.filename || 'Raw Content'}</td>
                    <td className="px-6 py-4 capitalize">{item.content_type}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        (item.prediction || item.status || '').toLowerCase().includes('ai')
                          ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}>
                        {item.prediction || item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-semibold text-white">{Math.round(item.confidence || 0)}%</td>
                    <td className="px-6 py-4 text-gray-500 text-xs">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'Recent'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="glass rounded-2xl p-12 text-center border border-white/10">
          <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4 text-gray-500">
            <HiOutlineDocumentSearch className="w-8 h-8" />
          </div>
          <h3 className="text-white text-lg font-semibold mb-2">No Detection History Yet</h3>
          <p className="text-gray-400 text-sm max-w-md mx-auto mb-6">
            Run your first content authenticity scan using Gaia's multi-modal engine.
          </p>
          <Link
            to="/upload"
            className="px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/15 text-white text-sm font-semibold transition-all inline-flex items-center gap-2"
          >
            Start Analyzing Now
          </Link>
        </div>
      )}
    </div>
  );
}
