import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Upload, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileSpreadsheet, 
  Trash2, 
  Plus, 
  Search, 
  X 
} from 'lucide-react';
import api from '../../services/api';

export default function Recipients() {
  const [recipients, setRecipients] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  // CSV Validation state
  const [csvFile, setCsvFile] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);
  const [importing, setImporting] = useState(false);
  const [groupName, setGroupName] = useState('');

  // Add Manual Recipient state
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);
  const [manualName, setManualName] = useState('');
  const [manualEmail, setManualEmail] = useState('');

  const fetchRecipients = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/recipients?search=${encodeURIComponent(search)}`);
      setRecipients(res.data.items);
      setTotalCount(res.data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecipients();
  }, [search]);

  const handleCsvSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setCsvFile(file);
    setValidating(true);
    setValidationResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post('/recipients/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setValidationResult(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || 'CSV validation failed.');
    } finally {
      setValidating(false);
    }
  };

  const handleImportValid = async () => {
    if (!validationResult || validationResult.valid_rows.length === 0) return;
    setImporting(true);
    try {
      const res = await api.post('/recipients/import', {
        valid_rows: validationResult.valid_rows,
        group_name: groupName || null
      });
      alert(res.data.message);
      setValidationResult(null);
      setCsvFile(null);
      setGroupName('');
      fetchRecipients();
    } catch (err) {
      alert('Import failed.');
    } finally {
      setImporting(false);
    }
  };

  const handleAddManual = async (e) => {
    e.preventDefault();
    try {
      await api.post('/recipients', { name: manualName, email: manualEmail });
      setIsManualModalOpen(false);
      setManualName('');
      setManualEmail('');
      fetchRecipients();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to add recipient.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this recipient?')) return;
    try {
      await api.delete(`/recipients/${id}`);
      fetchRecipients();
    } catch (err) {
      alert('Failed to delete recipient.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-950 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Recipient Management</h1>
          <p className="text-sm text-slate-400 mt-1">Upload CSV, validate contact rows, and manage email list</p>
        </div>
        <button
          onClick={() => setIsManualModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-sky-600/30"
        >
          <Plus className="w-4 h-4" />
          Add Recipient
        </button>
      </div>

      {/* CSV Upload & Validation Area */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-sky-400" />
          Upload & Validate CSV Recipient File
        </h2>

        <div className="border-2 border-dashed border-slate-800 hover:border-sky-500/50 rounded-2xl p-8 text-center bg-slate-950/50 transition-colors">
          <input
            type="file"
            accept=".csv"
            onChange={handleCsvSelect}
            className="hidden"
            id="csv-upload-input"
          />
          <label htmlFor="csv-upload-input" className="cursor-pointer flex flex-col items-center">
            <Upload className="w-10 h-10 text-sky-400 mb-3 animate-bounce" />
            <span className="text-sm font-semibold text-slate-200">
              {csvFile ? csvFile.name : 'Click to select CSV file'}
            </span>
            <span className="text-xs text-slate-500 mt-1">Supports columns: name, email, subject, custom attributes</span>
          </label>
        </div>

        {validating && (
          <div className="text-center py-6 text-sky-400 flex items-center justify-center gap-2 text-sm">
            <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
            Analyzing and validating CSV rows...
          </div>
        )}

        {/* Validation Result Stats Summary */}
        {validationResult && (
          <div className="space-y-6 border-t border-slate-800 pt-6">
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <span className="text-xs text-slate-400 font-semibold uppercase">Total Rows</span>
                <p className="text-2xl font-bold text-slate-100 mt-1">{validationResult.total_rows}</p>
              </div>
              <div className="bg-emerald-500/10 p-4 rounded-xl border border-emerald-500/20">
                <span className="text-xs text-emerald-400 font-semibold uppercase">Valid Emails</span>
                <p className="text-2xl font-bold text-emerald-400 mt-1">{validationResult.valid_count}</p>
              </div>
              <div className="bg-rose-500/10 p-4 rounded-xl border border-rose-500/20">
                <span className="text-xs text-rose-400 font-semibold uppercase">Invalid Rows</span>
                <p className="text-2xl font-bold text-rose-400 mt-1">{validationResult.invalid_count}</p>
              </div>
              <div className="bg-amber-500/10 p-4 rounded-xl border border-amber-500/20">
                <span className="text-xs text-amber-400 font-semibold uppercase">Duplicates</span>
                <p className="text-2xl font-bold text-amber-400 mt-1">{validationResult.duplicate_count}</p>
              </div>
            </div>

            {/* Invalid Row Details Table */}
            {validationResult.invalid_rows.length > 0 && (
              <div className="bg-slate-950 p-4 rounded-xl border border-rose-500/30">
                <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Invalid Rows Detail Log ({validationResult.invalid_rows.length})
                </h3>
                <div className="max-h-40 overflow-y-auto space-y-1 text-xs">
                  {validationResult.invalid_rows.map((inv, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 bg-slate-900 rounded border border-slate-800">
                      <span className="font-mono text-slate-400">Row #{inv.row}</span>
                      <span className="text-rose-400 font-medium">{inv.reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Import Controls */}
            {validationResult.valid_count > 0 && (
              <div className="flex flex-col sm:flex-row items-center gap-4 bg-slate-950 p-4 rounded-xl border border-slate-800 justify-between">
                <input
                  type="text"
                  placeholder="Optional Group Name (e.g. Q3 Leads)"
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500 w-full sm:w-80"
                />
                <button
                  onClick={handleImportValid}
                  disabled={importing}
                  className="w-full sm:w-auto px-6 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Import {validationResult.valid_count} Valid Recipients
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Recipient Database List */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-slate-100">Saved Database Recipients ({totalCount})</h2>
            <p className="text-xs text-slate-400">Stored contacts ready for email campaigns</p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search name or email..."
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-sky-500"
            />
          </div>
        </div>

        {loading ? (
          <div className="h-48 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : recipients.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
            <Users className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No recipients stored yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="pb-3 font-semibold">Name</th>
                  <th className="pb-3 font-semibold">Email</th>
                  <th className="pb-3 font-semibold">Custom Attributes</th>
                  <th className="pb-3 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recipients.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 font-medium text-slate-200">{r.name}</td>
                    <td className="py-3.5 font-mono text-xs text-sky-400">{r.email}</td>
                    <td className="py-3.5 text-xs text-slate-400">
                      {r.custom_fields && Object.keys(r.custom_fields).length > 0 ? (
                        <div className="flex gap-1.5 flex-wrap">
                          {Object.entries(r.custom_fields).map(([k, v]) => (
                            <span key={k} className="bg-slate-950 px-2 py-0.5 rounded border border-slate-800 font-mono">
                              {k}: {String(v)}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-600 italic">None</span>
                      )}
                    </td>
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() => handleDelete(r.id)}
                        className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                        title="Delete"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Manual Recipient Modal */}
      {isManualModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-slate-100">Add Single Recipient</h3>
              <button onClick={() => setIsManualModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddManual} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={manualName}
                  onChange={(e) => setManualName(e.target.value)}
                  placeholder="Jane Smith"
                  className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  required
                  value={manualEmail}
                  onChange={(e) => setManualEmail(e.target.value)}
                  placeholder="jane@company.com"
                  className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsManualModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow-lg shadow-sky-600/30"
                >
                  Save Recipient
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

