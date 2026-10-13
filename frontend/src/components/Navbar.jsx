import React, { useState } from 'react';
import { Activity, Database, Sparkles, Cpu, Search, BarChart3, Radio, Globe, Moon, Sun } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, language, setLanguage, theme, toggleTheme, onSearch }) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearch(searchQuery.trim());
      setSearchQuery('');
    }
  };

  const navItems = [
    { id: 'matches', label: language === 'hi' ? 'मैच सेंटर' : (language === 'mr' ? 'मॅच सेंटर' : 'Match Center'), icon: Activity },
    { id: 'dataset', label: language === 'hi' ? 'डेटासेट' : (language === 'mr' ? 'डेटासेट' : 'Dataset Explorer'), icon: Database },
    { id: 'preprocessing', label: language === 'hi' ? 'प्रीप्रोसेसिंग' : (language === 'mr' ? 'प्रीप्रोसेसिंग' : 'Preprocessing'), icon: Sparkles },
    { id: 'nlp', label: language === 'hi' ? 'एनएलपी मॉडल' : (language === 'mr' ? 'एनएलपी मॉडेल' : 'NLP Models'), icon: Cpu },
    { id: 'bda', label: language === 'hi' ? 'बिग डेटा (BDA)' : (language === 'mr' ? 'बिग डेटा (BDA)' : 'Big Data (BDA)'), icon: BarChart3 },
    { id: 'ir', label: language === 'hi' ? 'सर्च (IR)' : (language === 'mr' ? 'शोध (IR)' : 'IR Search'), icon: Search },
    { id: 'eval', label: language === 'hi' ? 'मूल्यांकन' : (language === 'mr' ? 'मूल्यांकन' : 'Evaluation'), icon: Radio },
  ];

  return (
    <header className={`sticky top-0 z-50 backdrop-blur-md border-b ${theme === 'dark' ? 'bg-slate-900/90 border-slate-800' : 'bg-white/90 border-slate-200'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 cursor-pointer shrink-0" onClick={() => setActiveTab('matches')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-emerald-400 p-0.5 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <span className="text-xl font-black bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">CB</span>
              </div>
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center space-x-2">
                <span className={`font-extrabold text-lg tracking-tight ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>Cric<span className="text-blue-500">Bhasha</span></span>
                <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-500/10 text-blue-500 rounded border border-blue-500/30 uppercase tracking-wider">BDA + NLP + IR</span>
              </div>
              <p className={`text-[11px] font-medium ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Multilingual Cricket Intelligence</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : (theme === 'dark' ? 'text-slate-300 hover:text-white hover:bg-slate-800/60' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          <div className="flex items-center gap-3 ml-auto">
            {/* Search Bar */}
            <form onSubmit={handleSearchSubmit} className="relative hidden md:block">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search queries..."
                className={`w-48 pl-8 pr-3 py-1.5 text-xs rounded-full border focus:outline-none focus:border-blue-500 transition-colors ${
                  theme === 'dark'
                    ? 'bg-slate-800/80 border-slate-700 text-slate-200 placeholder-slate-500'
                    : 'bg-slate-100 border-slate-200 text-slate-900 placeholder-slate-400'
                }`}
              />
              <Search className={`w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`} />
            </form>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-1.5 rounded-lg border transition-colors ${
                theme === 'dark'
                  ? 'bg-slate-800/80 border-slate-700 text-slate-400 hover:text-white'
                  : 'bg-slate-100 border-slate-200 text-slate-500 hover:text-slate-900'
              }`}
            >
              {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

            {/* Language Selector */}
            <div className={`flex items-center border rounded-lg p-1 ${theme === 'dark' ? 'bg-slate-800/80 border-slate-700/70' : 'bg-slate-100 border-slate-200'}`}>
              <Globe className={`w-3.5 h-3.5 ml-1.5 mr-1 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`} />
              <button
                onClick={() => setLanguage('en')}
                className={`px-2 py-1 text-xs font-bold rounded-md transition-colors ${
                  language === 'en'
                    ? 'bg-blue-600 text-white'
                    : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={`px-2 py-1 text-xs font-bold rounded-md transition-colors ${
                  language === 'hi'
                    ? 'bg-blue-600 text-white'
                    : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')
                }`}
              >
                हिन्दी
              </button>
              <button
                onClick={() => setLanguage('mr')}
                className={`px-2 py-1 text-xs font-bold rounded-md transition-colors ${
                  language === 'mr'
                    ? 'bg-blue-600 text-white'
                    : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200' : 'text-slate-500 hover:text-slate-700')
                }`}
              >
                मराठी
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Bar */}
        <div className={`lg:hidden flex overflow-x-auto py-2 space-x-1 border-t scrollbar-none ${theme === 'dark' ? 'border-slate-800' : 'border-slate-200'}`}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center space-x-1.5 px-2.5 py-1.5 rounded-md text-[11px] font-medium whitespace-nowrap ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : (theme === 'dark' ? 'text-slate-400 bg-slate-800/40' : 'text-slate-600 bg-slate-100')
                }`}
              >
                <Icon className="w-3 h-3" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
