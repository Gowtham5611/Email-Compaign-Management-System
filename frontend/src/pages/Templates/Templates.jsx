import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Plus, 
  Copy, 
  Trash2, 
  Eye, 
  Edit, 
  Sparkles, 
  X, 
  Check, 
  AlertCircle 
} from 'lucide-react';
import api from '../../services/api';

export default function Templates() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Modal States
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);

  // Form State
  const [name, setName] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [description, setDescription] = useState('');

  // Preview State
  const [previewData, setPreviewData] = useState(null);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const res = await api.get('/templates');
      setTemplates(res.data);
    } catch (err) {
      setError('Failed to load email templates.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleOpenCreate = () => {
    setEditingTemplate(null);
    setName('');
    setSubject('Project Update - {subject}');
    setBody('Hello {name},\n\nThis is an automated notification regarding {subject}.\n\nRegards,\nEmail Campaign Management System');
    setDescription('');
    setIsEditModalOpen(true);
  };

  const handleOpenEdit = (t) => {
    setEditingTemplate(t);
    setName(t.name);
    setSubject(t.subject);
    setBody(t.body);
    setDescription(t.description || '');
    setIsEditModalOpen(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingTemplate) {
        await api.put(`/templates/${editingTemplate.id}`, { name, subject, body, description });
      } else {
        await api.post('/templates', { name, subject, body, description });
      }
      setIsEditModalOpen(false);
      fetchTemplates();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to save template.');
    }
  };

  const handleDuplicate = async (id) => {
    try {
      await api.post(`/templates/${id}/duplicate`);
      fetchTemplates();
    } catch (err) {
      alert('Failed to duplicate template.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this template?')) return;
    try {
      await api.delete(`/templates/${id}`);
      fetchTemplates();
    } catch (err) {
      alert('Failed to delete template.');
    }
  };

  const handlePreview = async (t) => {
    try {
      const res = await api.post('/templates/preview', {
        subject: t.subject,
        body: t.body,
        sample_data: {
          name: 'John Doe',
          email: 'john.doe@example.com',
          subject: 'Quarterly Project Milestone',
          position: 'Senior Developer',
          company: 'TechCorp'
        }
      });
      setPreviewData(res.data);
      setIsPreviewModalOpen(true);
    } catch (err) {
      alert('Failed to generate preview.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-950 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Email Templates</h1>
          <p className="text-sm text-slate-400 mt-1">Manage, edit, duplicate and preview dynamic email templates</p>
        </div>
        <button
          onClick={handleOpenCreate}
          className="flex items-center gap-2 px-4 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-xl transition-all shadow-lg shadow-sky-600/30"
        >
          <Plus className="w-4 h-4" />
          Create Template
        </button>
      </div>

      {/* Available Placeholders Tip Banner */}
      <div className="p-4 rounded-xl bg-sky-600/10 border border-sky-600/20 flex items-start gap-3">
        <Sparkles className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
        <div className="text-xs text-sky-300 space-y-1">
          <p className="font-semibold">Supported Template Variable Variables:</p>

          <p>
            Use <code className="bg-sky-950 px-1.5 py-0.5 rounded text-sky-200">{'{name}'}</code>, <code className="bg-sky-950 px-1.5 py-0.5 rounded text-sky-200">{'{subject}'}</code>, <code className="bg-sky-950 px-1.5 py-0.5 rounded text-sky-200">{'{email}'}</code> or any dynamic custom column from your CSV (e.g. <code className="bg-sky-950 px-1.5 py-0.5 rounded text-sky-200">{'{company}'}</code>, <code className="bg-sky-950 px-1.5 py-0.5 rounded text-sky-200">{'{position}'}</code>).
          </p>
        </div>
      </div>

      {/* Templates Grid */}
      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-16 bg-slate-900 border border-slate-800 rounded-2xl">
          <FileText className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-slate-200 font-semibold">No Templates Created</h3>
          <p className="text-slate-400 text-sm mt-1 mb-4">Create your first reusable email body template.</p>
          <button
            onClick={handleOpenCreate}
            className="px-4 py-2 bg-sky-600 text-white text-sm font-medium rounded-xl hover:bg-sky-500 transition-colors"
          >
            + Create Template
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {templates.map((t) => (
            <div key={t.id} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-md">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-bold text-slate-100 text-base">{t.name}</h3>
                  <span className="text-[11px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
                    ID #{t.id}
                  </span>
                </div>
                <p className="text-xs font-medium text-sky-400 mb-3 truncate">
                  Subject: {t.subject}
                </p>
                <p className="text-xs text-slate-400 line-clamp-3 bg-slate-950 p-3 rounded-xl border border-slate-800 font-mono whitespace-pre-wrap">
                  {t.body}
                </p>
              </div>

              <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-800 text-xs">
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => handlePreview(t)}
                    className="p-2 text-slate-400 hover:text-sky-400 hover:bg-sky-500/10 rounded-lg transition-colors"
                    title="Preview Email"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleOpenEdit(t)}
                    className="p-2 text-slate-400 hover:text-amber-400 hover:bg-amber-500/10 rounded-lg transition-colors"
                    title="Edit Template"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDuplicate(t.id)}
                    className="p-2 text-slate-400 hover:text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors"
                    title="Duplicate Template"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                </div>
                <button
                  onClick={() => handleDelete(t.id)}
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                  title="Delete Template"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Edit / Create Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-slate-100">
                {editingTemplate ? 'Edit Template' : 'New Template'}
              </h3>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Template Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Project Update Template"
                  className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Email Subject (Supports Variables)
                </label>
                <input
                  type="text"
                  required
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Notification: {subject}"
                  className="w-full px-4 py-2 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                  Email Body Template
                </label>
                <textarea
                  required
                  rows={8}
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                  className="w-full p-4 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm font-mono focus:outline-none focus:border-sky-500"
                ></textarea>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-sky-600 hover:bg-sky-500 text-white text-sm font-medium rounded-xl shadow-lg shadow-sky-600/30"
                >
                  Save Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {isPreviewModalOpen && previewData && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-xl bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Eye className="w-5 h-5 text-sky-400" />
                Template Render Preview
              </h3>
              <button
                onClick={() => setIsPreviewModalOpen(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-sm">
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <span className="text-xs text-slate-500 font-semibold uppercase">Subject:</span>
                <p className="font-semibold text-slate-200 mt-1">{previewData.rendered_subject}</p>
              </div>

              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <span className="text-xs text-slate-500 font-semibold uppercase">Body:</span>
                <p className="font-mono text-slate-300 whitespace-pre-wrap mt-2 leading-relaxed">
                  {previewData.rendered_body}
                </p>
              </div>

              <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400">
                <span>Detected Placeholders:</span>
                {previewData.detected_variables.map((v) => (
                  <span key={v} className="bg-sky-600/20 text-sky-300 px-2 py-0.5 rounded font-mono">
                    {`{${v}}`}
                  </span>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setIsPreviewModalOpen(false)}
                className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium rounded-xl"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

