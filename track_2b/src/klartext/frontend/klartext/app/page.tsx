"use client";
import React, { useState, useEffect } from 'react';
import TriageDashboard from '../components/TriageDashboard';
import LetterDetailView from '../components/LetterDetailView';

export default function KlartextApp() {
  const [currentView, setCurrentView] = useState<'triage' | 'detail'>('triage');
  const [activeDoc, setActiveDoc] = useState<any>(null);
  
  const [docsList, setDocsList] = useState<any[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  // NOUVEAU : Récupérer l'historique des documents déjà traités au chargement de la page
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("/letters");
        if (res.ok) {
          const history = await res.json();
          // Si l'API renvoie des documents, on les met dans la liste
          setDocsList(history);
        }
      } catch (error) {
        console.warn("Impossible de récupérer l'historique (le backend n'a peut-être pas encore démarré).", error);
      }
    };

    fetchHistory();
  }, []); // Le tableau vide [] signifie que ça s'exécute uniquement à l'ouverture de la page

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach(file => formData.append("files", file)); 

            const uploadRes = await fetch("/documents/batch", {
        method: "POST",
        body: formData,
      });
      const { uploaded, failed } = await uploadRes.json();

      // Tell the user about files that could not be read (e.g. scans without text)
      if (failed.length > 0) {
        alert("Could not read: " + failed.map((f: any) => f.filename).join(", "));
      }

      if (uploaded && uploaded.length > 0) {
        // Run the analysis (8B first, 70B when needed) for each letter in parallel
        const responses = await Promise.all(uploaded.map((doc: any) =>
          fetch(`/documents/${doc.id}/extract`, { method: "POST" })
        ));
        const failedResponse = responses.find((r) => !r.ok);
        if (failedResponse) {
          const err = await failedResponse.json().catch(() => null);
          alert(err?.detail ?? "The analysis failed for at least one letter.");
        }

        // Récupération de la liste mise à jour
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
            🔒 In-memory only
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