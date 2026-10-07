"use client";
import React, { useState } from 'react';
import TriageDashboard from '../components/TriageDashboard';
import LetterDetailView from '../components/LetterDetailView';

// Dossier factice pour prouver le Twist
const initialDocs = [
  {
    id: "e4a1b2c3",
    filename: "CH_VD_TAX_001_fr.pdf",
    extraction: {
      document_type: "tax",
      sender: { value: "Administration Fiscale de la Commune de Belleville", verified: true },
      deadline: { value: "15 novembre 2026", verified: true },
      actions: [{ value: "Régler le solde de 850,25 CHF", verified: true }],
      consequences: [
        { value: "Facturation d'intérêts moratoires", verified: true },
        { value: "Amende de 100 CHF pour retard", verified: false } // Le Twist
      ]
    },
    days_left: 42,
    model_used: "apertus-v1.5-8b",
    escalated: false,
    latency_ms: 2345
  }
];

export default function KlartextApp() {
  const [currentView, setCurrentView] = useState<'triage' | 'detail'>('triage');
  const [activeDoc, setActiveDoc] = useState<any>(null);
  const [docsList, setDocsList] = useState(initialDocs);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      // Pour gérer le batch upload, on itère sur les fichiers
      for (let i = 0; i < files.length; i++) {
        const formData = new FormData();
        formData.append("file", files[i]);

        const response = await fetch("http://localhost:8000/documents", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const newDocument = await response.json();
          setDocsList(prev => [...prev, newDocument]);
        } else {
          console.error("Erreur serveur pour le fichier", files[i].name);
        }
      }
    } catch (error) {
      console.error(error);
      alert("Erreur de connexion à l'API locale.");
    } finally {
      setIsUploading(false);
      // Réinitialiser l'input file
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