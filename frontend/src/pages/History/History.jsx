import React, { useState, useEffect } from 'react';
import { History as HistoryIcon, Eye, CheckCircle2, XCircle, Clock, AlertTriangle, X } from 'lucide-react';
import api from '../../services/api';

export default function History() {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [recipientResults, setRecipientResults] = useState([]);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const fetchCampaigns = async () => {
    setLoading(true);
    try {
      const res = await api.get('/campaigns');
      setCampaigns(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleOpenDetails = async (c) => {
    setSelectedCampaign(c);
    setLoadingDetails(true);
    try {
      const res = await api.get(`/campaigns/${c.id}/recipients`);
      setRecipientResults(res.data);
    } catch (err) {
      alert('Failed to load campaign recipient details.');
    } finally {
      setLoadingDetails(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-950 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Campaign History</h1>
          <p className="text-sm text-slate-400 mt-1">Audit historical execution results and individual recipient delivery logs</p>
        </div>
      </div>

      {/* History Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        {loading ? (
          <div className="h-48 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-16">
            <HistoryIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No historical campaign logs found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Campaign Name</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Total Recipients</th>
                  <th className="pb-3 font-semibold">Sent / Failed</th>
                  <th className="pb-3 font-semibold">Created Date</th>
                  <th className="pb-3 font-semibold text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {campaigns.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 font-bold text-slate-100">{c.name}</td>
                    <td className="py-3.5">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        c.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        c.status === 'SENDING' ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' :
                        c.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        c.status === 'CANCELLED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {c.status}
                      </span>
                    </td>
                    <td className="py-3.5 text-slate-300 font-semibold">{c.total_recipients}</td>
                    <td className="py-3.5 text-xs">
                      <span className="text-emerald-400 font-bold">{c.successful_count}</span> / <span className="text-rose-400 font-bold">{c.failed_count}</span>
                    </td>
                    <td className="py-3.5 text-xs text-slate-400">
                      {new Date(c.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() => handleOpenDetails(c)}
                        className="px-3 py-1.5 bg-sky-600/10 hover:bg-sky-600/20 text-sky-400 border border-sky-600/30 text-xs font-semibold rounded-lg transition-colors flex items-center gap-1.5 ml-auto"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        View Results
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Recipient Results Detail Modal */}
      {selectedCampaign && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <h3 className="text-lg font-bold text-slate-100">{selectedCampaign.name}</h3>
                <p className="text-xs text-slate-400">Recipient Delivery Breakdown Log</p>
              </div>
              <button onClick={() => setSelectedCampaign(null)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            {loadingDetails ? (
              <div className="h-48 flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : (
              <div className="max-h-96 overflow-y-auto space-y-2 pr-1">
                {recipientResults.map((r) => (
                  <div key={r.id} className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <span className="font-semibold text-slate-200 text-sm">{r.recipient_name}</span>
                      <span className="text-xs text-sky-400 font-mono ml-2">({r.recipient_email})</span>
                      {r.error_message && (
                        <p className="text-xs text-rose-400 mt-1 font-mono bg-rose-500/10 p-2 rounded border border-rose-500/20">
                          Failure Reason: {r.error_message}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-xs text-slate-500 font-mono">Retries: {r.retry_count}</span>
                      <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                        r.status === 'SENT' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                        r.status === 'FAILED' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' :
                        r.status === 'CANCELLED' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {r.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedCampaign(null)}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

