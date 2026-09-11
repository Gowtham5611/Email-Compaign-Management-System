import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, Key, CheckCircle2, AlertCircle, ShieldCheck, Server } from 'lucide-react';
import api from '../../services/api';

export default function Settings() {
  const [smtpHost, setSmtpHost] = useState('smtp.gmail.com');
  const [smtpPort, setSmtpPort] = useState(465);
  const [smtpUsername, setSmtpUsername] = useState('');
  const [smtpPassword, setSmtpPassword] = useState('');
  const [senderName, setSenderName] = useState('Email Campaign Management System');
  const [useTls, setUseTls] = useState(true);
  const [isPasswordSet, setIsPasswordSet] = useState(false);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState(null);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const res = await api.get('/settings');
      setSmtpHost(res.data.smtp_host);
      setSmtpPort(res.data.smtp_port);
      setSmtpUsername(res.data.smtp_username || '');
      setSenderName(res.data.sender_name || 'Email Campaign Management System');
      setUseTls(res.data.use_tls);
      setIsPasswordSet(res.data.is_password_set);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const res = await api.post('/settings', {
        smtp_host: smtpHost,
        smtp_port: parseInt(smtpPort),
        smtp_username: smtpUsername,
        smtp_password: smtpPassword || undefined,
        sender_name: senderName,
        use_tls: useTls
      });
      setIsPasswordSet(res.data.is_password_set);
      setSmtpPassword('');
      setMessage({ type: 'success', text: 'SMTP Settings saved successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to save settings.' });
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setMessage(null);
    try {
      const res = await api.post('/settings/test-smtp', {
        smtp_host: smtpHost,
        smtp_port: parseInt(smtpPort),
        smtp_username: smtpUsername,
        smtp_password: smtpPassword || undefined,
        sender_name: senderName,
        use_tls: useTls
      });
      setMessage({ type: 'success', text: res.data.message });
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'SMTP test connection failed.' });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between bg-slate-950 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">SMTP & Application Settings</h1>
          <p className="text-sm text-slate-400 mt-1">Configure email delivery servers, credentials, and security defaults</p>
        </div>
      </div>

      {message && (
        <div className={`p-4 rounded-xl border flex items-center gap-3 text-sm ${
          message.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'
        }`}>
          {message.type === 'success' ? <CheckCircle2 className="w-5 h-5 shrink-0" /> : <AlertCircle className="w-5 h-5 shrink-0" />}
          <span>{message.text}</span>
        </div>
      )}

      {/* Security Tip */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3 text-xs text-slate-300">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-slate-200">Credential Storage & Encryption:</p>
          <p className="text-slate-400 mt-0.5">
            SMTP app passwords are kept strictly encrypted on the backend server. Passwords are never sent to or displayed on the frontend in plain text.
          </p>
        </div>
      </div>

      <form onSubmit={handleSave} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
        <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-4">
          <Server className="w-5 h-5 text-sky-400" />
          SMTP Server Configuration
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              SMTP Server Host
            </label>
            <input
              type="text"
              required
              value={smtpHost}
              onChange={(e) => setSmtpHost(e.target.value)}
              placeholder="smtp.gmail.com"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              SMTP Port
            </label>
            <input
              type="number"
              required
              value={smtpPort}
              onChange={(e) => setSmtpPort(e.target.value)}
              placeholder="465"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              SMTP Username (Sender Email)
            </label>
            <input
              type="email"
              required
              value={smtpUsername}
              onChange={(e) => setSmtpUsername(e.target.value)}
              placeholder="your-email@gmail.com"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>App Password / Key</span>
              {isPasswordSet && (
                <span className="text-emerald-400 text-[11px] font-semibold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Password Configured
                </span>
              )}
            </label>
            <input
              type="password"
              value={smtpPassword}
              onChange={(e) => setSmtpPassword(e.target.value)}
              placeholder={isPasswordSet ? "•••••••• (Leave blank to keep existing)" : "Enter App Password"}
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Sender Display Name
            </label>
            <input
              type="text"
              value={senderName}
              onChange={(e) => setSenderName(e.target.value)}
              placeholder="Email Campaign Management System"
              className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="flex items-center pt-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={useTls}
                onChange={(e) => setUseTls(e.target.checked)}
                className="w-4 h-4 rounded border-slate-700 bg-slate-950 text-sky-600 focus:ring-0"
              />
              <span className="text-sm font-medium text-slate-300">Enable SSL/TLS Security</span>
            </label>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-t border-slate-800 pt-6">
          <button
            type="button"
            onClick={handleTestConnection}
            disabled={testing}
            className="w-full sm:w-auto px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl transition-all border border-slate-700 flex items-center justify-center gap-2"
          >
            {testing ? (
              <span className="w-4 h-4 border-2 border-slate-200 border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <Key className="w-4 h-4 text-amber-400" />
            )}
            Test Connection
          </button>

          <button
            type="submit"
            disabled={saving}
            className="w-full sm:w-auto px-6 py-2.5 bg-sky-600 hover:bg-sky-500 text-white text-sm font-semibold rounded-xl transition-all shadow-lg shadow-sky-600/30 flex items-center justify-center gap-2"
          >
            {saving ? (
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save Configuration
          </button>
        </div>
      </form>
    </div>
  );
}

