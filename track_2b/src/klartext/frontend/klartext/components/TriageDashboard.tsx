"use client";
import React, { useMemo, useRef } from 'react';

export default function TriageDashboard({ docsList, isUploading, onFileUpload, onOpenDetail }: any) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Tri automatique par jours restants
  const sortedData = useMemo(() => {
    return [...docsList].sort((a, b) => {
      if (a.days_left === null) return 1;
      if (b.days_left === null) return -1;
      return a.days_left - b.days_left;
    });
  }, [docsList]);

  return (
    <main className="max-w-6xl mx-auto p-6 mt-6 flex flex-col gap-6">
      {/* ZONE D'UPLOAD (BATCH) */}
      <section 
        onClick={() => fileInputRef.current?.click()}
        className="bg-white border-2 border-dashed border-indigo-200 rounded-xl p-8 text-center hover:bg-indigo-50 transition-colors cursor-pointer relative"
      >
        <input 
          type="file" 
          accept=".pdf" 
          multiple // Permet le batch upload
          className="hidden" 
          ref={fileInputRef}
          onChange={onFileUpload}
        />
        {isUploading ? (
          <div className="text-indigo-600 font-bold animate-pulse">Analyse Apertus en cours...</div>
        ) : (
          <>
            <div className="text-indigo-500 mb-2 font-bold text-2xl">+</div>
            <h2 className="text-lg font-bold text-slate-700">Déposer un lot de lettres (PDF)</h2>
            <p className="text-slate-500 text-sm mt-1">L'extraction (Cascade 8B → 70B) se lance automatiquement.</p>
          </>
        )}
      </section>

      {/* TABLEAU DE TRIAGE */}
      <div className="bg-white rounded-xl shadow border border-slate-200 overflow-hidden">
        <div className="p-4 bg-slate-100 border-b border-slate-200">
          <h2 className="font-bold text-lg">Dossiers à traiter (Ordre de priorité)</h2>
        </div>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-slate-500 text-xs uppercase border-b border-slate-200">
              <th className="p-4">Fichier</th>
              <th className="p-4">Expéditeur</th>
              <th className="p-4">Jours restants</th>
              <th className="p-4">Vérification (Modèle)</th>
              <th className="p-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sortedData.map((doc, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="p-4 font-medium text-slate-900">{doc.filename}</td>
                <td className="p-4 text-sm text-slate-600">{doc.extraction?.sender?.value || 'Inconnu'}</td>
                <td className="p-4">
                  {doc.days_left !== null ? (
                     <span className={`text-xs font-bold px-2 py-1 rounded-md ${doc.days_left <= 20 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                       {doc.days_left} jours
                     </span>
                  ) : (
                    <span className="text-xs text-slate-400">Aucun délai</span>
                  )}
                </td>
                <td className="p-4 text-xs font-semibold text-indigo-700">
                  {doc.model_used} {doc.escalated && <span className="text-orange-600 font-bold ml-1">(Escaladé)</span>}
                </td>
                <td className="p-4 text-right">
                  <button onClick={() => onOpenDetail(doc)} className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                    Ouvrir
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}