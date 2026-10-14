import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import api from '../../services/api';
import Badge from '../../components/Badge/Badge';

export default function History() {
  const { user, loading: authLoading } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadHistory() {
      if (!user) {
        setLoading(false);
        return;
      }
      try {
        const items = await api.getHistory(50, 0);
        setHistory(items || []);
      } catch (err) {
        setError(err.message || 'Could not fetch detection history.');
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [user]);

  if (authLoading) {
    return <div className="min-h-screen pt-36 text-center text-gray-400">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="min-h-screen pt-36 px-4 max-w-md mx-auto text-center">
        <div className="glass rounded-2xl p-8 border border-white/10">
          <h2 className="text-2xl font-bold text-white mb-2">Login Required</h2>
          <p className="text-gray-400 text-sm mb-6">
            Log in to see all your past scan logs and detection reports.
          </p>
          <Link
            to={ROUTES.LOGIN}
            className="inline-block w-full py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 md:px-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold font-heading text-white">Detection History</h1>
          <p className="text-gray-400 text-sm mt-1">Audit log of all content authenticity checks performed</p>
        </div>
        <Link
          to={ROUTES.UPLOAD}
          className="px-4 py-2 rounded-xl text-sm font-medium text-white bg-white/10 hover:bg-white/15 transition-colors"
        >
          + New Detection
        </Link>
      </div>

      <div className="glass rounded-2xl p-6 md:p-8 border border-white/10">
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading audit history...</div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-white/10 rounded-xl">
            <p className="text-gray-400 mb-4">No detection scans recorded yet.</p>
            <Link
              to={ROUTES.UPLOAD}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium text-sm inline-block"
            >
              Start First Scan
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 text-gray-400">
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium">Source / Filename</th>
                  <th className="pb-3 font-medium">Classification</th>
                  <th className="pb-3 font-medium">Confidence Score</th>
                  <th className="pb-3 font-medium">Risk Level</th>
                  <th className="pb-3 font-medium">Date & Time</th>
                  <th className="pb-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {history.map((row) => (
                  <tr key={row.id} className="hover:bg-white/5 transition-colors">
                    <td className="py-4 font-medium text-white capitalize">{row.content_type}</td>
                    <td className="py-4 text-gray-300 max-w-xs truncate">{row.filename || 'Direct Input'}</td>
                    <td className="py-4">
                      <Badge variant={row.prediction === 'Likely AI' ? 'purple' : 'default'} size="sm">
                        {row.prediction}
                      </Badge>
                    </td>
                    <td className="py-4 text-white font-medium">
                      {row.confidence > 0 ? `${row.confidence}%` : 'N/A'}
                    </td>
                    <td className="py-4">
                      <span className={`text-xs font-semibold ${row.risk_level === 'High' ? 'text-red-400' : row.risk_level === 'Low' ? 'text-emerald-400' : 'text-gray-400'}`}>
                        {row.risk_level}
                      </span>
                    </td>
                    <td className="py-4 text-gray-400 text-xs">
                      {new Date(row.created_at).toLocaleString()}
                    </td>
                    <td className="py-4 text-right">
                      <Link
                        to={`/report?id=${row.id}`}
                        className="text-primary-cyan hover:underline text-xs font-medium"
                      >
                        Inspect Report
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
