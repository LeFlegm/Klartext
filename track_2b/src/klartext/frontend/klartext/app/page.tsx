"use client";
import React, { useState } from 'react';
import TriageDashboard from '../components/TriageDashboard';
import LetterDetailView from '../components/LetterDetailView';

// Mock data to prove the Twist
const initialDocs = [
  {
    id: "e4a1b2c3",
    filename: "CH_VD_TAX_001_fr.pdf",
    extraction: {
      document_type: "tax",
      sender: { value: "Tax Administration of Belleville", verified: true },
      deadline: { value: "November 15, 2026", verified: true },
      actions: [{ value: "Pay the balance of 850.25 CHF", verified: true }],
      consequences: [
        { value: "Billing of default interest", verified: true },
        { value: "100 CHF fine for late submission", verified: false } // The Twist
      ]
    },
    days_left: 42,
    days_left_estimated: false,
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
      // 1. Upload all files at once (Batch)
      const formData = new FormData();
      Array.from(files).forEach(file => formData.append("files", file)); 

      const uploadRes = await fetch("http://localhost:8000/documents/batch", {
        method: "POST",
        body: formData,
      });
      const uploadedDocs = await uploadRes.json();

      // 2. Run extraction (8B/70B) for each letter in parallel
      await Promise.all(uploadedDocs.map((doc: any) =>
        fetch(`http://localhost:8000/documents/${doc.id}/extract`, { method: "POST" })
      ));

      // 3. Fetch all finalized and sorted letters
      const lettersRes = await fetch("http://localhost:8000/letters");
      const allLetters = await lettersRes.json();
      
      setDocsList(allLetters);
      
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