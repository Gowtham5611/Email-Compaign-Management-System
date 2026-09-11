import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  FileText, 
  Users, 
  Paperclip, 
  CheckCircle2, 
  XCircle, 
  StopCircle, 
  Play, 
  Eye, 
  AlertCircle, 
  FileSpreadsheet, 
  Sparkles 
} from 'lucide-react';
import api from '../../services/api';

export default function Campaigns() {
  const [templates, setTemplates] = useState([]);
  const [recipients, setRecipients] = useState([]);
  const [groups, setGroups] = useState([]);

  // Creation Form state
  const [campaignName, setCampaignName] = useState('');
  const [selectedTemplateId, setSelectedTemplateId] = useState('');
  const [recipientSource, setRecipientSource] = useState('database'); // 'database', 'group', 'csv'
  const [selectedRecipientIds, setSelectedRecipientIds] = useState([]);
  const [selectedGroupId, setSelectedGroupId] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [csvValidatedRows, setCsvValidatedRows] = useState([]);
  const [attachmentFile, setAttachmentFile] = useState(null);

  // Active Campaign / Progress state
  const [activeCampaign, setActiveCampaign] = useState(null);
  const [progress, setProgress] = useState(null);
  const [logs, setLogs] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const pollingRef = useRef(null);

  useEffect(() => {
    // Load prerequisites
    api.get('/templates').then((res) => setTemplates(res.data)).catch(console.error);
    api.get('/recipients?limit=200').then((res) => setRecipients(res.data.items)).catch(console.error);
    api.get('/recipients/groups/list').then((res) => setGroups(res.data)).catch(console.error);
  }, []);

  // Poll progress when active campaign is sending
  useEffect(() => {
    if (activeCampaign && (activeCampaign.status === 'SENDING' || activeCampaign.status === 'QUEUED')) {
      pollingRef.current = setInterval(async () => {
        try {
          const res = await api.get(`/campaigns/${activeCampaign.id}/progress`);
          setProgress(res.data);
          if (res.data.status !== 'SENDING' && res.data.status !== 'QUEUED') {
            clearInterval(pollingRef.current);
            setActiveCampaign((prev) => ({ ...prev, status: res.data.status }));
          }
        } catch (err) {
          console.error(err);
        }
      }, 1500);
    } else {
      if (pollingRef.current) clearInterval(pollingRef.current);
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [activeCampaign]);

  const handleCsvSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setCsvFile(file);

    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await api.post('/recipients/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setCsvValidatedRows(res.data.valid_rows);
    } catch (err) {
      alert('CSV upload validation failed.');
    }
  };

  const handleCreateAndSend = async (e) => {
    e.preventDefault();
    if (!campaignName || !selectedTemplateId) {
      alert('Please enter campaign name and select a template.');
      return;
    }

    setIsSubmitting(true);
    const formData = new FormData();
    formData.append('name', campaignName);
    formData.append('template_id', selectedTemplateId);

    if (recipientSource === 'database') {
      if (selectedRecipientIds.length === 0) {
        alert('Please select at least one recipient.');
        setIsSubmitting(false);
        return;
      }
      formData.append('recipient_ids', JSON.stringify(selectedRecipientIds));
    } else if (recipientSource === 'group') {
      if (!selectedGroupId) {
        alert('Please select a recipient group.');
        setIsSubmitting(false);
        return;
      }
      formData.append('recipient_group_ids', JSON.stringify([parseInt(selectedGroupId)]));
    } else if (recipientSource === 'csv') {
      if (csvValidatedRows.length === 0) {
        alert('Please upload a valid CSV file.');
        setIsSubmitting(false);
        return;
      }
      formData.append('raw_recipients', JSON.stringify(csvValidatedRows));
    }

    if (attachmentFile) {
      formData.append('attachment', attachmentFile);
    }

    try {
      // 1. Create Campaign
      const createRes = await api.post('/campaigns', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const created = createRes.data;

      // 2. Trigger Send
      const sendRes = await api.post(`/campaigns/${created.id}/send`);
      setActiveCampaign(sendRes.data);
      alert(`Campaign #${created.id} launched successfully!`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to launch campaign.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCancelCampaign = async () => {
    if (!activeCampaign) return;
    if (!window.confirm('Stop sending remaining emails for this campaign?')) return;
    try {
      const res = await api.post(`/campaigns/${activeCampaign.id}/cancel`);
      setActiveCampaign(res.data);
      alert('Campaign sending halted.');
    } catch (err) {
      alert('Failed to cancel campaign.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-950 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Email Campaigns</h1>
          <p className="text-sm text-slate-400 mt-1">Configure, preview, launch, and monitor bulk email dispatches</p>
        </div>
      </div>

      {/* Real-time Progress Monitor if Active Campaign exists */}
      {activeCampaign && (
        <div className="bg-slate-900 border border-sky-500/40 rounded-2xl p-6 space-y-6 shadow-2xl">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs text-sky-400 font-semibold uppercase tracking-wider">Active Campaign Monitor</span>
              <h2 className="text-xl font-bold text-slate-100">{activeCampaign.name} (ID #{activeCampaign.id})</h2>
            </div>
            <div className="flex items-center gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                activeCampaign.status === 'SENDING' ? 'bg-sky-500/20 text-sky-300 animate-pulse border border-sky-500/30' :
                activeCampaign.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                activeCampaign.status === 'CANCELLED' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                'bg-slate-800 text-slate-400'
              }`}>
                STATUS: {activeCampaign.status}
              </span>
              {(activeCampaign.status === 'SENDING' || activeCampaign.status === 'QUEUED') && (
                <button
                  onClick={handleCancelCampaign}
                  className="flex items-center gap-1.5 px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-bold rounded-xl transition-all"
                >
                  <StopCircle className="w-4 h-4 text-rose-400" />
                  Cancel Campaign
                </button>
              )}
            </div>
          </div>

          {/* Progress Bar & Stats */}
          {progress && (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-sm text-slate-300 font-medium">
                <span>Sending Progress: {progress.percentage}%</span>
                <span>{progress.sent + progress.failed} / {progress.total} Processed</span>
              </div>
              <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="bg-gradient-to-r from-sky-500 to-emerald-500 h-full transition-all duration-500"
                  style={{ width: `${progress.percentage}%` }}
                ></div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 text-xs">
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-500 font-semibold">Total</span>
                  <p className="text-lg font-bold text-slate-200">{progress.total}</p>
                </div>
                <div className="bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
                  <span className="text-emerald-400 font-semibold">Successful</span>
                  <p className="text-lg font-bold text-emerald-400">{progress.sent}</p>
                </div>
                <div className="bg-rose-500/10 p-3 rounded-xl border border-rose-500/20">
                  <span className="text-rose-400 font-semibold">Failed</span>
                  <p className="text-lg font-bold text-rose-400">{progress.failed}</p>
                </div>
                <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="text-slate-400 font-semibold">Pending</span>
                  <p className="text-lg font-bold text-slate-300">{progress.pending}</p>
                </div>
                <div className="bg-amber-500/10 p-3 rounded-xl border border-amber-500/20">
                  <span className="text-amber-400 font-semibold">Cancelled</span>
                  <p className="text-lg font-bold text-amber-400">{progress.cancelled}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Campaign Creation Wizard */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <Send className="w-5 h-5 text-sky-400" />
          Launch New Campaign
        </h2>

        <form onSubmit={handleCreateAndSend} className="space-y-6">
          {/* 1. Campaign Name */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              1. Campaign Name
            </label>
            <input
              type="text"
              required
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              placeholder="e.g. Q3 Product Update & Announcement"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* 2. Select Template */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              2. Select Email Template
            </label>
            <select
              required
              value={selectedTemplateId}
              onChange={(e) => setSelectedTemplateId(e.target.value)}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            >
              <option value="">-- Choose a Saved Template --</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name} (Subject: {t.subject})
                </option>
              ))}
            </select>
          </div>

          {/* 3. Recipient Selection */}
          <div className="space-y-3">
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
              3. Recipient Selection Method
            </label>

            <div className="flex gap-4 border-b border-slate-800 pb-3">
              <button
                type="button"
                onClick={() => setRecipientSource('database')}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  recipientSource === 'database' ? 'bg-sky-600 text-white' : 'bg-slate-950 text-slate-400 hover:text-slate-200'
                }`}
              >
                Select from Saved Database ({recipients.length})
              </button>
              <button
                type="button"
                onClick={() => setRecipientSource('csv')}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  recipientSource === 'csv' ? 'bg-sky-600 text-white' : 'bg-slate-950 text-slate-400 hover:text-slate-200'
                }`}
              >
                Direct CSV Upload
              </button>
            </div>

            {recipientSource === 'database' && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 max-h-48 overflow-y-auto space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                  <span>Check recipients to include:</span>
                  <button
                    type="button"
                    onClick={() => setSelectedRecipientIds(recipients.map(r => r.id))}
                    className="text-sky-400 hover:underline font-semibold"
                  >
                    Select All ({recipients.length})
                  </button>
                </div>
                {recipients.map((r) => (
                  <label key={r.id} className="flex items-center gap-3 text-xs text-slate-300 hover:bg-slate-900 p-1.5 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedRecipientIds.includes(r.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedRecipientIds([...selectedRecipientIds, r.id]);
                        } else {
                          setSelectedRecipientIds(selectedRecipientIds.filter(id => id !== r.id));
                        }
                      }}
                      className="rounded border-slate-700 bg-slate-900 text-sky-500 focus:ring-0"
                    />
                    <span className="font-semibold text-slate-200">{r.name}</span>
                    <span className="text-slate-500 font-mono">({r.email})</span>
                  </label>
                ))}
              </div>
            )}

            {recipientSource === 'csv' && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleCsvSelect}
                  className="text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-sky-600 file:text-white hover:file:bg-sky-500 cursor-pointer"
                />
                {csvValidatedRows.length > 0 && (
                  <p className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    Validated {csvValidatedRows.length} valid recipient rows ready for campaign
                  </p>
                )}
              </div>
            )}
          </div>

          {/* 4. Optional Attachment */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-2">
              <Paperclip className="w-4 h-4 text-sky-400" />
              4. Optional File Attachment
            </label>
            <input
              type="file"
              onChange={(e) => setAttachmentFile(e.target.files[0] || null)}
              className="text-xs text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-800 file:text-slate-200 hover:file:bg-slate-700 cursor-pointer"
            />
          </div>

          {/* Launch Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3.5 bg-sky-600 hover:bg-sky-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-sky-600/30 flex items-center justify-center gap-2 disabled:opacity-50 text-base"
          >
            {isSubmitting ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Confirm & Start Campaign
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

