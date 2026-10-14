import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import api from '../../services/api';

export default function Report() {
  const [searchParams] = useSearchParams();
  const detectionId = searchParams.get('id');
  const { user, loading: authLoading } = useAuth();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchReport() {
      if (!detectionId) {
        setError('No detection report ID was specified.');
        setLoading(false);
        return;
      }
      try {
        const data = await api.getReport(detectionId);
        setReport(data);
      } catch (err) {
        setError(err.message || 'Report could not be retrieved.');
      } finally {
        setLoading(false);
      }
    }
    if (user) {
      fetchReport();
    } else if (!authLoading) {
      setLoading(false);
    }
  }, [detectionId, user, authLoading]);

  if (authLoading || loading) {
    return <div className="min-h-screen pt-36 text-center text-gray-400">Loading analysis report...</div>;
  }

  if (!user) {
    return (
      <div className="min-h-screen pt-36 px-4 max-w-md mx-auto text-center">
        <div className="glass rounded-2xl p-8 border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-2">Login Required</h2>
          <p className="text-gray-400 text-sm mb-6">
            Please log in to view protected detection reports.
          </p>
          <Link
            to={ROUTES.LOGIN}
            className="inline-block w-full py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium"
          >
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen pt-36 px-4 max-w-xl mx-auto text-center">
        <div className="glass rounded-2xl p-8 border border-white/10">
          <h2 className="text-2xl font-bold text-red-400 mb-2">Report Not Found</h2>
          <p className="text-gray-400 text-sm mb-6">{error || 'Unable to display report details.'}</p>
          <Link
            to={ROUTES.HISTORY}
            className="px-4 py-2 rounded-xl bg-white/10 text-white text-sm hover:bg-white/15"
          >
            Return to History
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 md:px-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-primary-cyan">
            Forensic Authenticity Report
          </span>
          <h1 className="text-3xl font-bold font-heading text-white mt-1">
            {report.status}
          </h1>
        </div>
        <Link
          to={ROUTES.HISTORY}
          className="px-4 py-2 rounded-xl text-sm font-medium bg-white/10 text-gray-300 hover:text-white"
        >
          ← Back to History
        </Link>
      </div>

      <div className="glass rounded-2xl p-6 md:p-10 border border-white/10 shadow-2xl">
        <div className="flex justify-between items-center pb-6 border-b border-white/10 flex-wrap gap-4">
          <div>
            <span className="text-xs text-gray-400 block">Report Reference ID</span>
            <code className="text-xs text-primary-cyan font-mono">{report.id || detectionId}</code>
          </div>
          <div className="text-right">
            <span className="text-xs text-gray-400 block">Timestamp</span>
            <span className="text-sm text-gray-300">
              {new Date(report.created_at).toLocaleString()}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 my-8">
          <div className="p-4 rounded-xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400 block">Content Type</span>
            <span className="text-white font-medium capitalize text-lg">{report.content_type}</span>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400 block">Classification</span>
            <span className="text-white font-medium text-lg">{report.prediction}</span>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400 block">Model Score</span>
            <span className="text-lg font-bold gradient-text">
              {report.verified ? `${report.confidence}%` : 'N/A'}
            </span>
          </div>
          <div className="p-4 rounded-xl bg-white/5 border border-white/5">
            <span className="text-xs text-gray-400 block">Risk Evaluation</span>
            <span className={`text-lg font-semibold ${report.risk_level === 'High' ? 'text-red-400' : report.risk_level === 'Low' ? 'text-emerald-400' : 'text-gray-300'}`}>
              {report.risk_level}
            </span>
          </div>
        </div>

        <div className="mb-8">
          <h3 className="text-base font-semibold text-white mb-2">Findings Summary</h3>
          <div className="p-5 rounded-xl bg-white/5 border border-white/10 text-gray-300 text-sm leading-relaxed">
            {report.summary}
          </div>
        </div>

        <div className="pt-6 border-t border-white/10 text-xs text-gray-400 space-y-2">
          <p>
            <strong className="text-gray-300">Pipeline Model:</strong> {report.detector_name}
          </p>
          <p>
            <strong className="text-gray-300">Processing Duration:</strong> {report.processing_time_sec}s
          </p>
          <p>
            <strong className="text-gray-300">Verification Status:</strong>{' '}
            {report.verified ? 'Verified Model Inference' : 'Unmounted Prototype / Heuristic'}
          </p>
          <p className="text-gray-500 italic mt-3">
            Notice: Gaia Detector outputs represent heuristic statistical indicators and do not constitute absolute forensic proof.
          </p>
        </div>
      </div>
    </div>
  );
}
