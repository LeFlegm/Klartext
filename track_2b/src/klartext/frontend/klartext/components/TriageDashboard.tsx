"use client";
import React, { useMemo, useRef } from 'react';

export default function TriageDashboard({ docsList, isUploading, onFileUpload, onOpenDetail }: any) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Automatic sorting by days left
  const sortedData = useMemo(() => {
    // Sécurité au cas où docsList serait undefined au démarrage
    if (!docsList) return [];
    
    return [...docsList].sort((a, b) => {
      if (a.days_left === null) return 1;
      if (b.days_left === null) return -1;
      return a.days_left - b.days_left;
    });
  }, [docsList]);

  return (
    <main className="max-w-6xl mx-auto p-6 mt-6 flex flex-col gap-6">
      {/* UPLOAD ZONE (BATCH) */}
      <section 
        onClick={() => fileInputRef.current?.click()}
        className="bg-white border-2 border-dashed border-indigo-200 rounded-xl p-8 text-center hover:bg-indigo-50 transition-colors cursor-pointer relative"
      >
        <input 
          type="file" 
          accept=".pdf" 
          multiple // Enables batch upload
          className="hidden" 
          ref={fileInputRef}
          onChange={onFileUpload}
        />
        {isUploading ? (
          <div className="text-indigo-600 font-bold animate-pulse">Apertus analysis in progress...</div>
        ) : (
          <>
            <div className="text-indigo-500 mb-2 font-bold text-2xl">+</div>
            <h2 className="text-lg font-bold text-slate-700">Upload a batch of letters (PDF)</h2>
            <p className="text-slate-500 text-sm mt-1">Extraction (8B → 70B cascade) starts automatically.</p>
          </>
        )}
      </section>

      {/* TRIAGE TABLE - Ne s'affiche que s'il y a des documents */}
      {sortedData.length > 0 && (
        <div className="bg-white rounded-xl shadow border border-slate-200 overflow-hidden">
          <div className="p-4 bg-slate-100 border-b border-slate-200">
            <h2 className="font-bold text-lg">Letters to process (Sorted by urgency)</h2>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
                <th className="p-4">File</th>
                <th className="p-4">Sender</th>
                <th className="p-4">Days left</th>
                <th className="p-4">Verification</th>
                <th className="p-4">Model Used</th>
                <th className="p-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedData.map((doc, idx) => (
                <tr key={idx} className="hover:bg-slate-50">
                  <td className="p-4 font-medium text-slate-900">{doc.filename}</td>
                  <td className="p-4 text-sm text-slate-600">{doc.extraction?.sender?.value || 'Unknown'}</td>
                  <td className="p-4">
                    {doc.days_left !== null ? (
                       <span className={`text-xs font-bold px-2 py-1 rounded-md ${doc.days_left <= 20 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                         {doc.days_left_estimated ? '~' : ''}{doc.days_left} days
                       </span>
                    ) : (
                      <span className="text-xs text-slate-400">No deadline</span>
                    )}
                  </td>
                  <td className="p-4">
                    {/* Badge Unverified Count (Le "Twist") */}
                    {doc.unverified_count > 0 ? (
                      <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-1 rounded-full animate-pulse">
                        ⚠️ {doc.unverified_count} unsupported
                      </span>
                    ) : (
                      <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded-full">
                        ✓ All verified
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-xs font-semibold text-indigo-700">
                    {doc.model_used} {doc.escalated && <span className="text-orange-600 font-bold ml-1">(Escalated)</span>}
                  </td>
                  <td className="p-4 text-right">
                    <button onClick={() => onOpenDetail(doc)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                      Open
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {/* BENCHMARK CHARTS SECTION */}
      <section className="bg-white rounded-xl shadow border border-slate-200 p-6 mt-8">
        {/* SECTION ARCHITECTURE LOCALE & FONCTIONNEMENT GLOBAL */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 md:p-8 shadow-sm mt-8">
          <div className="max-w-3xl mx-auto text-center mb-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-semibold mb-3 border border-emerald-200">
              🔒 100% Local & Privacy-First (Air-Gapped)
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-slate-900">How Klartext Protects Your Sensitive Data</h2>
            <p className="text-sm text-slate-600 mt-2">
              Designed for confidential administrative, legal, and health documents. Everything runs locally on your machine or secure server, with zero external cloud calls.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Étape 1 */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 text-left relative">
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-sm mb-3">1</div>
              <h3 className="font-bold text-slate-900 text-sm mb-1">Local PDF Ingestion</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                You upload your administrative letters (KVG, Tax, Debt). Files and extracted texts stay strictly in local memory with zero disk persistence.
              </p>
            </div>

            {/* Étape 2 */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 text-left relative">
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-sm mb-3">2</div>
              <h3 className="font-bold text-slate-900 text-sm mb-1">Local AI Cascade (8B → 70B)</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Our optimized local LLM processes the document. The fast 8B model handles routine extraction, escalating complex clauses to the 70B model.
              </p>
            </div>

            {/* Étape 3 */}
            <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 text-left relative">
              <div className="w-8 h-8 rounded-full bg-indigo-600 text-white font-bold flex items-center justify-center text-sm mb-3">3</div>
              <h3 className="font-bold text-slate-900 text-sm mb-1">Secure Triage & Verifiable Spans</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Letters are automatically sorted by urgency with precise source-span highlights, enabling fast, verifiable human-in-the-loop review.
              </p>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-4">
            <div>🛡️ <strong>Zero Data Leakage:</strong> No third-party APIs, no telemetry, fully compliant with strict data residency.</div>
            <div className="font-mono bg-slate-100 px-2 py-1 rounded text-slate-700">Docker Container • Single-Stack Architecture</div>
          </div>
        </div>
      </section>
    </main>
  );
}