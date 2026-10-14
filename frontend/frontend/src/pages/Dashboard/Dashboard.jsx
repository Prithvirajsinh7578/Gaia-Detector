import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineDocumentSearch, HiOutlineShieldCheck, HiOutlineClock, HiOutlinePlus } from 'react-icons/hi';
import { useAuth } from '../../context/AuthContext';
import { ROUTES } from '../../constants/routes';
import api from '../../services/api';
import Badge from '../../components/Badge/Badge';

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      if (!user) {
        setLoading(false);
        return;
      }
      try {
        const items = await api.getHistory(5, 0);
        setHistory(items || []);
      } catch (err) {
        setError(err.message || 'Could not load detection history.');
      } finally {
        setLoading(false);
      }
    }
    loadDashboardData();
  }, [user]);

  if (authLoading) {
    return (
      <div className="min-h-screen pt-36 text-center text-gray-400">
        Loading session...
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen pt-36 px-4 max-w-md mx-auto text-center">
        <div className="glass rounded-2xl p-8 border border-white/10">
          <HiOutlineShieldCheck className="w-12 h-12 text-primary-cyan mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Authentication Required</h2>
          <p className="text-gray-400 text-sm mb-6">
            Please log in or register to access your personal dashboard and history.
          </p>
          <div className="flex gap-4">
            <Link
              to={ROUTES.LOGIN}
              className="flex-1 py-2.5 rounded-xl bg-white/10 text-white font-medium hover:bg-white/15"
            >
              Sign In
            </Link>
            <Link
              to={ROUTES.REGISTER}
              className="flex-1 py-2.5 rounded-xl bg-gradient-to-r from-primary-cyan to-primary-purple text-white font-medium"
            >
              Register
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 md:px-8 max-w-7xl mx-auto">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-10">
        <div>
          <h1 className="text-3xl md:text-4xl font-bold font-heading text-white">
            Welcome back, <span className="gradient-text">{user.name || user.email}</span>
          </h1>
          <p className="text-gray-400 text-sm mt-1">Here is a summary of your recent authenticity analyses.</p>
        </div>
        <Link
          to={ROUTES.UPLOAD}
          className="px-5 py-2.5 rounded-xl font-medium text-white bg-gradient-to-r from-primary-cyan to-primary-purple hover:opacity-90 transition-opacity flex items-center gap-2 shadow-lg shadow-primary-cyan/20"
        >
          <HiOutlinePlus className="w-5 h-5" />
          New Detection
        </Link>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Total Scanned</span>
            <HiOutlineDocumentSearch className="w-5 h-5 text-primary-cyan" />
          </div>
          <p className="text-3xl font-extrabold text-white">{history.length}</p>
        </div>
        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Active Pipelines</span>
            <HiOutlineShieldCheck className="w-5 h-5 text-primary-purple" />
          </div>
          <p className="text-3xl font-extrabold text-white">4 Types</p>
        </div>
        <div className="glass rounded-2xl p-6 border border-white/10">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Storage Destination</span>
            <HiOutlineClock className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">Google Drive</p>
        </div>
      </div>

      {/* Recent Detections List */}
      <div className="glass rounded-2xl p-6 md:p-8 border border-white/10">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold font-heading text-white">Recent Analyses</h2>
          <Link to={ROUTES.HISTORY} className="text-sm text-primary-cyan hover:underline">
            View all history →
          </Link>
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-400">Loading detection records...</div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-red-500/10 text-red-400 text-sm">{error}</div>
        ) : history.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-white/10 rounded-xl">
            <p className="text-gray-400 mb-3">No scans recorded yet for this account.</p>
            <Link
              to={ROUTES.UPLOAD}
              className="inline-block px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/15"
            >
              Analyze your first file
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-white/10 text-gray-400">
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium">Filename / Input</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Score</th>
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-white/5 transition-colors">
                    <td className="py-4 font-medium text-white capitalize">{item.content_type}</td>
                    <td className="py-4 text-gray-300 truncate max-w-xs">{item.filename || 'Direct upload'}</td>
                    <td className="py-4">
                      <Badge variant={item.risk_level === 'High' ? 'purple' : 'default'} size="sm">
                        {item.status}
                      </Badge>
                    </td>
                    <td className="py-4 text-white font-semibold">
                      {item.confidence > 0 ? `${item.confidence}%` : 'N/A'}
                    </td>
                    <td className="py-4 text-gray-400 text-xs">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-4 text-right">
                      <Link
                        to={`/report?id=${item.id}`}
                        className="text-primary-cyan hover:underline text-xs font-medium"
                      >
                        View Report
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
