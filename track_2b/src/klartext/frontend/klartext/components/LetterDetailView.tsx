import React, { useState } from 'react';

// The ten languages the backend can explain a letter in (codes match services/explainer.py).
const LANGUAGES: { code: string; label: string; rtl?: boolean }[] = [
  { code: 'en', label: 'English' },
  { code: 'fr', label: 'Français' },
  { code: 'de', label: 'Deutsch' },
  { code: 'it', label: 'Italiano' },
  { code: 'tr', label: 'Türkçe' },
  { code: 'ar', label: 'العربية', rtl: true },
  { code: 'uk', label: 'Українська' },
  { code: 'ti', label: 'ትግርኛ' },
  { code: 'prs', label: 'دری', rtl: true },
  { code: 'so', label: 'Soomaali' },
];

// One extracted fact: the English summary, and the verbatim quote from the letter it rests on.
function HighlightedQuote({ label, quote, value, verified }: { label: string; quote?: string; value: string; verified?: boolean }) {
  if (!quote && !value) return null;
  return (
    <div className="mb-4">
      <span className="text-xs font-bold text-slate-500 uppercase">{label}</span>
      <div className="mt-1 mb-2 text-slate-900 font-medium">{value}</div>
      <div className="p-3 bg-slate-50 rounded border border-slate-200 text-sm font-serif text-slate-800 relative">
        <span className="bg-yellow-200 px-1 rounded">{quote || value}</span>
        {verified !== undefined && (
          <span className={`absolute -top-2 -right-2 text-[10px] font-bold px-2 py-0.5 rounded-full ${verified ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {verified ? '✓ Verified' : '⚠️ Unverified'}
          </span>
        )}
      </div>
    </div>
  );
}

export default function LetterDetailView({ activeDoc, onBack }: any) {
  const [activeTab, setActiveTab] = useState<'pdf' | 'text'>('pdf'); // mobile layout only
  const [language, setLanguage] = useState('');
  const [explanations, setExplanations] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!activeDoc) {
    return (
      <div className="p-8 text-center">
        <p className="text-red-500">No letter selected.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded">Back</button>
      </div>
    );
  }

  const extraction = activeDoc.extraction || {};
  const sender = extraction.sender || {};
  // Same rule as the scorer and the triage: a deadline counts only if it has a date or a number of days.
  const rawDeadline = extraction.deadline;
  const deadline = rawDeadline && (rawDeadline.iso_date || rawDeadline.relative_days != null) ? rawDeadline : null;
  const actions = extraction.actions || [];
  const consequences = extraction.consequences || [];

  // Ask the backend to explain the letter in the chosen language (verified facts only).
  async function explain(code: string) {
    setLanguage(code);
    setError(null);
    if (!code || explanations[`${activeDoc.id}:${code}`]) return;
    setLoading(true);
    try {
      const res = await fetch(`/documents/${activeDoc.id}/explain?language=${code}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? 'The explanation failed.');
      setExplanations(prev => ({ ...prev, [`${activeDoc.id}:${code}`]: data.explanation?.text ?? '' }));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const chosen = LANGUAGES.find(l => l.code === language);
  const explanation = explanations[`${activeDoc.id}:${language}`];

  const deadlineValue = deadline
    ? [deadline.value, deadline.iso_date ? `(${deadline.iso_date})` : null,
       activeDoc.days_left != null ? `${activeDoc.days_left_estimated ? '~' : ''}${activeDoc.days_left} days left` : null]
        .filter(Boolean).join(' ')
    : '';

  return (
    <main className="max-w-7xl mx-auto p-4 md:p-6 mt-2 md:mt-6">
      <button onClick={onBack} className="mb-4 md:mb-6 px-4 py-2 bg-white border border-slate-300 rounded-md text-sm font-medium hover:bg-slate-50">
        ← Back to triage
      </button>

      <div className="flex lg:hidden mb-4 border-b border-slate-200">
        <button onClick={() => setActiveTab('pdf')} className={`pb-2 px-4 font-medium ${activeTab === 'pdf' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500'}`}>Original letter</button>
        <button onClick={() => setActiveTab('text')} className={`pb-2 px-4 font-medium ${activeTab === 'text' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500'}`}>Extracted data</button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 md:gap-8">
        {/* The uploaded PDF, served from memory by the backend */}
        <section className={`flex-1 bg-white border border-slate-200 rounded-xl shadow-sm p-4 flex-col min-h-[600px] lg:min-h-[800px] ${activeTab === 'pdf' ? 'flex' : 'hidden lg:flex'}`}>
          <h2 className="text-sm font-bold text-slate-500 uppercase mb-4 border-b border-slate-100 pb-2">Original letter</h2>
          <iframe
            src={`/documents/${activeDoc.id}/file#navpanes=0&view=FitH`}
            className="w-full h-full rounded border border-slate-200 bg-slate-100"
            title="Original letter (PDF)"
          />
        </section>

        <section className={`flex-1 flex-col gap-6 ${activeTab === 'text' ? 'flex' : 'hidden lg:flex'}`}>
          <div className="border-b border-slate-200 pb-2">
            <h2 className="text-xl font-bold text-slate-900">Extracted facts and their quotes</h2>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-6 shadow-sm overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-3">
              <label className="text-xs font-bold text-slate-500 uppercase" htmlFor="lang">Explain this letter in</label>
              <select
                id="lang"
                value={language}
                onChange={(e) => explain(e.target.value)}
                className="bg-white border border-slate-300 text-sm rounded-lg p-2"
              >
                <option value="">Choose a language…</option>
                {LANGUAGES.map(l => <option key={l.code} value={l.code}>{l.label}</option>)}
              </select>
            </div>
            {loading && <p className="text-sm text-slate-500 mb-3">Writing the explanation…</p>}
            {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
            {explanation && (
              <div className="mb-4 p-3 bg-indigo-50 border border-indigo-100 rounded text-slate-900" dir={chosen?.rtl ? 'rtl' : 'ltr'}>
                <p>{explanation}</p>
                <p className="mt-2 text-[11px] text-slate-500" dir="ltr">Generated from the verified facts below only.</p>
              </div>
            )}

            <HighlightedQuote label="Sender" quote={sender.source_span} value={sender.value || 'Unknown'} verified={sender.verified} />

            <h3 className="text-xs font-bold text-slate-500 uppercase mt-6 mb-2 border-t pt-4">Deadline</h3>
            {deadline
              ? <HighlightedQuote label="Date or period" quote={deadline.source_span} value={deadlineValue} verified={deadline.verified} />
              : <p className="text-sm text-slate-500 italic">No deadline found in this letter.</p>}

            <h3 className="text-xs font-bold text-slate-500 uppercase mt-6 mb-2 border-t pt-4">Required actions</h3>
            {actions.length > 0 ? actions.map((a: any, i: number) => (
              <HighlightedQuote key={`action-${i}`} label={`Action ${i + 1}`} quote={a.source_span} value={a.value} verified={a.verified} />
            )) : <p className="text-sm text-slate-500 italic">No required action found.</p>}

            <h3 className="text-xs font-bold text-slate-500 uppercase mt-6 mb-2 border-t pt-4">Stated consequences</h3>
            {consequences.length > 0 ? consequences.map((c: any, i: number) => (
              <HighlightedQuote key={`cons-${i}`} label={`Consequence ${i + 1}`} quote={c.source_span} value={c.value} verified={c.verified} />
            )) : <p className="text-sm text-slate-500 italic">No consequence found.</p>}
          </div>
        </section>
      </div>
    </main>
  );
}
