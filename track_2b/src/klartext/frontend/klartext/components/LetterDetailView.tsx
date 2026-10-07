"use client";
import React from 'react';

export default function LetterDetailView({ activeDoc, onBack }: any) {
  return (
    <main className="flex h-[calc(100vh-72px)] overflow-hidden">
      {/* PANNEAU GAUCHE : PDF */}
      <section className="w-1/2 bg-slate-200 p-6 border-r border-slate-300 flex flex-col">
        <button onClick={onBack} className="mb-4 text-slate-600 font-bold text-sm hover:text-slate-900 self-start bg-white px-3 py-1 rounded shadow-sm">
          ← Retour au tableau
        </button>
        <div className="bg-white flex-1 rounded shadow p-8 text-slate-500 flex flex-col items-center justify-center border border-slate-300">
          <span className="text-4xl mb-4">📄</span>
          <p className="text-center font-medium">Original du PDF</p>
          <p className="text-xs mt-2">{activeDoc.filename}</p>
        </div>
      </section>

      {/* PANNEAU DROIT : EXTRACTION ET TRADUCTION */}
      <section className="w-1/2 bg-white p-6 overflow-y-auto space-y-6">
        <div className="flex justify-between items-center border-b pb-4">
          <h2 className="text-xl font-bold text-slate-800">Détails du dossier</h2>
          <select className="text-sm bg-slate-100 border border-slate-300 rounded px-2 py-1 outline-none">
            <option>Français (Assistant)</option>
            <option>Tigrinya (Bénéficiaire)</option>
            <option>Dari (Bénéficiaire)</option>
            <option>Somali (Bénéficiaire)</option>
          </select>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-1">Expéditeur</div>
          <div className="text-lg font-medium">{activeDoc.extraction?.sender?.value}</div>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-3">Actions requises</div>
          <ul className="list-disc list-inside space-y-2">
            {activeDoc.extraction?.actions?.map((act: any, i: number) => (
              <li key={i} className="text-slate-800">{act.value}</li>
            ))}
          </ul>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-3">Conséquences annoncées</div>
          <div className="space-y-3">
            {activeDoc.extraction?.consequences?.map((cons: any, i: number) => (
              <div key={i}>
                {cons.verified ? (
                  <div className="bg-green-50 border-l-4 border-green-500 p-3 text-sm flex flex-col gap-1">
                     <span className="text-slate-800 font-medium">{cons.value}</span>
                     <span className="text-[10px] text-green-700 font-bold">✓ SOURCE VÉRIFIÉE</span>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-300 p-4 rounded text-sm text-red-900 flex flex-col gap-2 relative shadow-sm">
                     <div className="flex items-center gap-2">
                       <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase animate-pulse">
                         ⚠️ Affirmation non sourcée
                       </span>
                     </div>
                     <span className="line-through opacity-70 italic text-slate-500">{cons.value}</span>
                     <p className="text-xs text-red-700 mt-1">
                       Le système a détecté et signalé cette information car elle n'apparaît pas dans le texte original.
                     </p>
                  </div>
                )}
              </div>
            ))}
            {(!activeDoc.extraction?.consequences || activeDoc.extraction.consequences.length === 0) && (
              <span className="text-slate-500 italic text-sm">Aucune conséquence trouvée.</span>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}