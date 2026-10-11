import React, { useState } from 'react';

export default function LetterDetailView({ activeDoc, onBack }: any) {
  const [selectedLanguage, setSelectedLanguage] = useState('Français');
  const [activeTab, setActiveTab] = useState<'pdf' | 'text'>('pdf'); // Pour la vue mobile
  
  // Fonction utilitaire pour simuler la traduction (le backend d'Apertus devrait normalement renvoyer la traduction)
  const translate = (text: string, lang: string) => {
      if (!text) return "";
      // Le LLM fait déjà un super travail de normalisation, on affiche directement son texte !
      return text;
  }

  // Fonction pour afficher le texte extrait avec la source en surbrillance
  const HighlightedQuote = ({ label, source_quote, translated_value, verified }: { label: string, source_quote: string, translated_value: string, verified?: boolean }) => {
    // Si on n'a ni citation ni traduction, on n'affiche rien
    if (!source_quote && !translated_value) return null;

    return (
        <div className="mb-4">
          <span className="text-xs font-bold text-slate-500 uppercase">{label}</span>
          
          {/* Affiche la valeur finale (traduite si nécessaire) */}
          <div className="mt-1 mb-2 text-slate-900 font-medium">
             {translated_value}
          </div>

          {/* Affiche le Span de source */}
          <div className="p-3 bg-slate-50 rounded border border-slate-200 text-sm font-serif text-slate-800 relative">
            <span className="bg-yellow-200 px-1 rounded">{source_quote || "Source text not found in document"}</span>
            {verified !== undefined && (
              <span className={`absolute -top-2 -right-2 text-[10px] font-bold px-2 py-0.5 rounded-full ${verified ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                {verified ? '✓ Verified' : '⚠️ Unverified'}
              </span>
            )}
          </div>
        </div>
    );
  };

  // Si on n'a pas de document actif, on affiche une erreur propre
  if (!activeDoc) {
      return (
        <div className="p-8 text-center">
            <p className="text-red-500">Aucun document sélectionné.</p>
            <button onClick={onBack} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded">Retour</button>
        </div>
      );
  }

  // Extraction sécurisée des données du backend
  const extraction = activeDoc?.extraction || {};
  const sender = extraction?.sender || {};
  const actions = extraction?.actions || [];
  const consequences = extraction?.consequences || [];

  return (
    <main className="max-w-7xl mx-auto p-4 md:p-6 mt-2 md:mt-6">
      <button onClick={onBack} className="mb-4 md:mb-6 px-4 py-2 bg-white border border-slate-300 rounded-md text-sm font-medium hover:bg-slate-50">
        ← Back to triage
      </button>

      {/* Mobile Tabs */}
      <div className="flex lg:hidden mb-4 border-b border-slate-200">
        <button onClick={() => setActiveTab('pdf')} className={`pb-2 px-4 font-medium ${activeTab === 'pdf' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500'}`}>Original PDF</button>
        <button onClick={() => setActiveTab('text')} className={`pb-2 px-4 font-medium ${activeTab === 'text' ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500'}`}>Extracted Data</button>
      </div>

      <div className="flex flex-col lg:flex-row gap-6 md:gap-8">
        
        {/* LECTEUR PDF (Masqué sur mobile si l'onglet Texte est actif) */}
        <section className={`flex-1 bg-white border border-slate-200 rounded-xl shadow-sm p-4 flex-col min-h-[600px] lg:min-h-[800px] ${activeTab === 'pdf' ? 'flex' : 'hidden lg:flex'}`}>
          <h2 className="text-sm font-bold text-slate-500 uppercase mb-4 border-b border-slate-100 pb-2">Document Original</h2>
          
          {/* L'iframe. On utilise le path_or_url s'il existe, sinon on tente la route du backend. */}
          {/* Si Yusuf renvoie l'URL du fichier dans activeDoc.url ou activeDoc.path, on l'utilise */}
          <iframe 
             src={activeDoc.url || activeDoc.file_url || activeDoc.path || `/documents/${activeDoc.id}/file`} 
             className="w-full h-full rounded border border-slate-200 bg-slate-100" 
             title="Document PDF" 
             onError={(e) => console.error("Erreur de chargement du PDF", e)}
          />
        </section>

        {/* DÉTAILS ET SOURCES SURLIGNÉES */}
        <section className={`flex-1 flex-col gap-6 ${activeTab === 'text' ? 'flex' : 'hidden lg:flex'}`}>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-200 pb-2">
            <h2 className="text-xl font-bold text-slate-900">Extraction Details & Spans</h2>
            <select 
               value={selectedLanguage} 
               onChange={(e) => setSelectedLanguage(e.target.value)} 
               className="w-full sm:w-auto bg-white border border-slate-300 text-sm rounded-lg p-2"
            >
              <option value="Français">Français</option>
              <option value="Anglais">Anglais</option>
              <option value="Allemand">Allemand</option>
              <option value="Italien">Italien</option>
            </select>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-6 shadow-sm overflow-hidden">
            
            <HighlightedQuote 
              label="Sender Name" 
              source_quote={sender.source_span || sender.value} 
              translated_value={sender.value || "Inconnu"}
              verified={sender.verified} 
            />
            
            <h3 className="text-xs font-bold text-slate-500 uppercase mt-6 mb-2 border-t pt-4">Required Actions</h3>
            {actions.length > 0 ? actions.map((action: any, i: number) => (
              <HighlightedQuote 
                key={`action-${i}`} 
                label={`Action ${i + 1}`} 
                source_quote={action.source_span || action.value} 
                translated_value={translate(action.value, selectedLanguage)}
                verified={action.verified} 
              />
            )) : <p className="text-sm text-slate-500 italic">Aucune action requise trouvée.</p>}

            <h3 className="text-xs font-bold text-slate-500 uppercase mt-6 mb-2 border-t pt-4">Stated Consequences</h3>
            {consequences.length > 0 ? consequences.map((cons: any, i: number) => (
              <HighlightedQuote 
                 key={`cons-${i}`} 
                 label={`Consequence ${i + 1}`} 
                 source_quote={cons.source_span || cons.value} 
                 translated_value={translate(cons.value, selectedLanguage)}
                 verified={cons.verified} 
              />
            )) : <p className="text-sm text-slate-500 italic">Aucune conséquence trouvée.</p>}
          </div>
        </section>
      </div>
    </main>
  );
}