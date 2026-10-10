"use client";
import React, { useState } from 'react';
import TriageDashboard from '../components/TriageDashboard';
import LetterDetailView from '../components/LetterDetailView';

export default function KlartextApp() {
  const [currentView, setCurrentView] = useState<'triage' | 'detail'>('triage');
  const [activeDoc, setActiveDoc] = useState<any>(null);
  
  // L'application démarre désormais à 100% vide, sans aucune fausse donnée
  const [docsList, setDocsList] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      // 1. Upload all files at once (Batch)
      const formData = new FormData();
      Array.from(files).forEach(file => formData.append("files", file)); 

      // Utilisation de l'URL relative et récupération de { uploaded, failed }
      const uploadRes = await fetch("/documents/batch", {
        method: "POST",
        body: formData,
      });
      const { uploaded, failed } = await uploadRes.json();

      if (failed && failed.length > 0) {
        console.warn("Certains fichiers ont échoué à l'upload :", failed);
      }

      if (uploaded && uploaded.length > 0) {
        // 2. Run extraction (8B/70B) for each successfully uploaded letter
        await Promise.all(uploaded.map((doc: any) =>
          fetch(`/documents/${doc.id}/extract`, { method: "POST" })
        ));

        // 3. Fetch all finalized and sorted letters (URL relative)
        const lettersRes = await fetch("/letters");
        const allLetters = await lettersRes.json();
        
        setDocsList(allLetters);
      }
      
    } catch (error) {
      console.error("API Error:", error);
      alert("Error communicating with local API. Is the backend running?");
    } finally {
      setIsUploading(false);
      event.target.value = '';
    }
  };

  return (
    <div className="bg-slate-50 min-h-screen font-sans text-slate-800">
      <header className="bg-slate-900 text-white p-4 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold tracking-tight">Klartext <span className="font-light text-slate-400">| Triage Desk</span></h1>
          <span className="bg-emerald-900 text-emerald-400 px-3 py-1 rounded-full text-xs border border-emerald-700">
            🔒 Air-gapped
          </span>
        </div>
      </header>

      {currentView === 'triage' ? (
        <TriageDashboard 
          docsList={docsList} 
          isUploading={isUploading} 
          onFileUpload={handleFileUpload} 
          onOpenDetail={(doc: any) => { setActiveDoc(doc); setCurrentView('detail'); }} 
        />
      ) : (
        <LetterDetailView 
          activeDoc={activeDoc} 
          onBack={() => setCurrentView('triage')} 
        />
      )}
    </div>
  );
}