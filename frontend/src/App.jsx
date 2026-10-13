import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MatchCenter from './pages/MatchCenter';
import DatasetExplorer from './pages/DatasetExplorer';
import PreprocessingExplorer from './pages/PreprocessingExplorer';
import NLPExplorer from './pages/NLPExplorer';
import BDAExplorer from './pages/BDAExplorer';
import IRExplorer from './pages/IRExplorer';
import EvaluationDashboard from './pages/EvaluationDashboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('matches');
  const [language, setLanguage] = useState('en'); // 'en', 'hi', 'mr'
  const [theme, setTheme] = useState(() => localStorage.getItem('ballriq-theme') || 'dark');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ballriq-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  const handleSearch = (query) => {
    if (query) {
      sessionStorage.setItem('ballriq-search', query);
      setActiveTab('ir');
    }
  };

  return (
    <div className={`min-h-screen flex flex-col justify-between transition-colors ${theme === 'dark' ? 'bg-[#090d16] text-slate-100' : 'bg-slate-50 text-slate-900'}`}>
      <div>
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          language={language}
          setLanguage={setLanguage}
          theme={theme}
          toggleTheme={toggleTheme}
          onSearch={handleSearch}
        />

        <main>
          {activeTab === 'matches' && <MatchCenter language={language} />}
          {activeTab === 'dataset' && <DatasetExplorer language={language} />}
          {activeTab === 'preprocessing' && <PreprocessingExplorer language={language} />}
          {activeTab === 'nlp' && <NLPExplorer language={language} />}
          {activeTab === 'bda' && <BDAExplorer language={language} />}
          {activeTab === 'ir' && <IRExplorer language={language} />}
          {activeTab === 'eval' && <EvaluationDashboard language={language} />}
        </main>
      </div>

      {/* Footer */}
      <footer className={`border-t py-6 mt-12 text-center text-xs ${theme === 'dark' ? 'border-slate-800/80 bg-slate-950/60 text-slate-500' : 'border-slate-200 bg-white/60 text-slate-500'}`}>
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span className={`font-bold ${theme === 'dark' ? 'text-slate-300' : 'text-slate-700'}`}>BALLRIQ</span> • Multilingual Cricket Intelligence & Big Data Platform
          </div>
          <div className="font-mono text-[11px]">
            PySpark • DuckDB • Parquet • XLM-R • BM25 • FAISS • Hybrid RAG
          </div>
        </div>
      </footer>
    </div>
  );
}
