"use client";
import React, { useState } from 'react';

export default function LetterDetailView({ activeDoc, onBack }: any) {
  // État pour stocker la phrase (source_span) actuellement survolée
  const [hoveredSpan, setHoveredSpan] = useState<string | null>(null);

  // Fonction factice simulant le texte complet extrait du PDF par le backend
  const fullText = activeDoc.full_text || `...texte complet du document non disponible pour ${activeDoc.filename}... \n\n${activeDoc.extraction?.actions?.[0]?.source_span || ''} \n\n${activeDoc.extraction?.consequences?.[0]?.source_span || ''}`;

  // Fonction pour surligner la phrase dans le texte complet
  const renderTextWithHighlight = (text: string, highlight: string | null) => {
    if (!highlight || !text.includes(highlight)) return <span className="whitespace-pre-wrap">{text}</span>;
    const parts = text.split(highlight);
    return (
      <span className="whitespace-pre-wrap leading-relaxed">
        {parts[0]}
        <mark className="bg-yellow-300 text-slate-900 px-1 rounded transition-colors duration-300 shadow-sm">{highlight}</mark>
        {parts[1]}
      </span>
    );
  };

  return (
    <main className="flex h-[calc(100vh-72px)] overflow-hidden">
      {/* PANNEAU GAUCHE : Affichage du texte extrait (au lieu du faux PDF) */}
      <section className="w-1/2 bg-slate-50 p-6 border-r border-slate-300 flex flex-col overflow-y-auto">
        <button onClick={onBack} className="mb-6 text-slate-600 font-bold text-sm hover:text-slate-900 self-start bg-white px-3 py-1 rounded shadow-sm border border-slate-200">
          ← Back to triage
        </button>
        <div className="bg-white flex-1 rounded shadow-sm p-8 text-slate-700 font-serif border border-slate-200">
          <h3 className="text-sm font-sans font-bold text-slate-400 mb-4 border-b pb-2">Extracted Text (Highlight View)</h3>
          {renderTextWithHighlight(fullText, hoveredSpan)}
        </div>
      </section>

      {/* PANNEAU DROIT : EXTRACTION & EXPLANATION */}
      <section className="w-1/2 bg-white p-6 overflow-y-auto space-y-6">
        <div className="flex justify-between items-center border-b pb-4">
          <h2 className="text-xl font-bold text-slate-800">Letter details</h2>
          <select className="text-sm bg-slate-100 border border-slate-300 rounded px-2 py-1 outline-none">
            <option>English (Caseworker)</option>
            <option>Tigrinya (Client)</option>
            <option>Dari (Client)</option>
            <option>Somali (Client)</option>
          </select>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-1">Sender</div>
          <div className="text-lg font-medium">{activeDoc.extraction?.sender?.value}</div>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-3">Required actions</div>
          <ul className="space-y-3">
            {activeDoc.extraction?.actions?.map((act: any, i: number) => (
              <li 
                key={i} 
                className="text-slate-800 p-2 hover:bg-slate-50 rounded cursor-pointer transition-colors border-l-2 border-transparent hover:border-indigo-400"
                onMouseEnter={() => setHoveredSpan(act.source_span)}
                onMouseLeave={() => setHoveredSpan(null)}
              >
                • {act.value}
              </li>
            ))}
          </ul>
        </div>

        <div className="border border-slate-200 rounded p-4 shadow-sm">
          <div className="text-xs text-slate-500 uppercase font-bold mb-3">Stated consequences</div>
          <div className="space-y-3">
            {activeDoc.extraction?.consequences?.map((cons: any, i: number) => (
              <div 
                key={i}
                onMouseEnter={() => setHoveredSpan(cons.source_span)}
                onMouseLeave={() => setHoveredSpan(null)}
                className="cursor-pointer hover:opacity-90 transition-opacity"
              >
                {cons.verified ? (
                  <div className="bg-green-50 border-l-4 border-green-500 p-3 text-sm flex flex-col gap-1">
                     <span className="text-slate-800 font-medium">{cons.value}</span>
                     <span className="text-[10px] text-green-700 font-bold">✓ VERIFIED SOURCE</span>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-300 p-4 rounded text-sm text-red-900 flex flex-col gap-2 relative shadow-sm">
                     <div className="flex items-center gap-2">
                       <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded uppercase animate-pulse">
                         ⚠️ Unsupported claim
                       </span>
                     </div>
                     <span className="line-through opacity-70 italic text-slate-500">{cons.value}</span>
                     <p className="text-xs text-red-700 mt-1">
                       The system detected and flagged this information because it does not appear in the original text.
                     </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}