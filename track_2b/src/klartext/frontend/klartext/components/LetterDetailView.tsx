import React from 'react';

export default function LetterDetailView({ activeDoc, onBack }: any) {

  const HighlightedQuote = ({ label, source_quote, extracted_value, verified }: { label: string, source_quote: string, extracted_value: any, verified?: boolean }) => {
    
    const final_text = typeof extracted_value === 'object' && extracted_value !== null 
        ? (extracted_value['English'] || extracted_value['Anglais'] || Object.values(extracted_value)[0]) 
        : extracted_value;

    if (!source_quote && !final_text) return null;

    return (
        <div className="mb-4">
          <span className="text-xs font-bold text-slate-500 uppercase">{label}</span>
          <div className="mt-1 mb-2 text-slate-900 font-medium text-lg">
             {final_text || "Data not available"}
          </div>
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

  if (!activeDoc) {
      return (
        <div className="p-8 text-center">
            <p className="text-red-500">No document selected.</p>
            <button onClick={onBack} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded">Go back</button>
        </div>
      );
  }

  const extraction = activeDoc?.extraction || {};
  const sender = extraction?.sender || {};
  const actions = extraction?.actions || [];
  const consequences = extraction?.consequences || [];

  return (
    <main className="max-w-4xl mx-auto p-4 md:p-6 mt-2 md:mt-6">
      <button onClick={onBack} className="mb-4 md:mb-6 px-4 py-2 bg-white border border-slate-300 rounded-md text-sm font-medium hover:bg-slate-50 shadow-sm">
        ← Back to triage
      </button>

      <div className="bg-white border border-slate-200 rounded-xl p-6 md:p-8 shadow-sm">
        <div className="border-b border-slate-200 pb-4 mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Extraction Details & Spans</h2>
          <p className="text-sm text-slate-500 mt-1">Document ID: {activeDoc.id}</p>
        </div>

        <HighlightedQuote 
          label="Sender Name" 
          source_quote={sender.source_span || sender.value} 
          extracted_value={sender.value || "Unknown Sender"}
          verified={sender.verified} 
        />
        
        <h3 className="text-xs font-bold text-slate-500 uppercase mt-8 mb-3 border-t pt-4">Required Actions</h3>
        {actions.length > 0 ? actions.map((action: any, i: number) => (
          <HighlightedQuote 
            key={`action-${i}`} 
            label={`Action ${i + 1}`} 
            source_quote={action.source_span || action.value} 
            extracted_value={action.value}
            verified={action.verified} 
          />
        )) : <p className="text-sm text-slate-500 italic">No required actions found.</p>}

        <h3 className="text-xs font-bold text-slate-500 uppercase mt-8 mb-3 border-t pt-4">Stated Consequences</h3>
        {consequences.length > 0 ? consequences.map((cons: any, i: number) => (
          <HighlightedQuote 
             key={`cons-${i}`} 
             label={`Consequence ${i + 1}`} 
             source_quote={cons.source_span || cons.value} 
             extracted_value={cons.value}
             verified={cons.verified} 
          />
        )) : <p className="text-sm text-slate-500 italic">No consequences found.</p>}
      </div>
    </main>
  );
}