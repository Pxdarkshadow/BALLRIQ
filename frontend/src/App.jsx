import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import MatchCenter from './pages/MatchCenter';
import NewsExplorer from './pages/DatasetExplorer';
import TeamsExplorer from './pages/PreprocessingExplorer';
import PlayersExplorer from './pages/NLPExplorer';
import LeaguesExplorer from './pages/BDAExplorer';
import StatsExplorer from './pages/IRExplorer';
import MoreExplorer from './pages/EvaluationDashboard';

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

        <main className="flex-1 overflow-hidden">
          {activeTab === 'matches' && <MatchCenter language={language} />}
          {activeTab === 'dataset' && <NewsExplorer language={language} />}
          {activeTab === 'preprocessing' && <TeamsExplorer language={language} />}
          {activeTab === 'nlp' && <PlayersExplorer language={language} />}
          {activeTab === 'bda' && <LeaguesExplorer language={language} />}
          {activeTab === 'ir' && <StatsExplorer language={language} />}
          {activeTab === 'eval' && <MoreExplorer language={language} />}
        </main>
      </div>
    </div>
  );
}
