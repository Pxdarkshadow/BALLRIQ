import React, { useState } from 'react';
import { Activity, MessageSquare, Users, User, Trophy, ChartBar, Ellipsis, Globe, Moon, Sun } from 'lucide-react';

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
    { id: 'matches', label: language === 'hi' ? 'होम' : (language === 'mr' ? 'होम' : 'Home'), icon: Activity },
    { id: 'dataset', label: language === 'hi' ? 'समाचार' : (language === 'mr' ? 'वातावरण' : 'News'), icon: MessageSquare },
    { id: 'preprocessing', label: language === 'hi' ? 'टीमें' : (language === 'mr' ? 'टीम्स' : 'Teams'), icon: Users },
    { id: 'nlp', label: language === 'hi' ? 'खिलाड़ी' : (language === 'mr' ? 'खिलाडी' : 'Players'), icon: User },
    { id: 'bda', label: language === 'hi' ? 'लीग' : (language === 'mr' ? 'लीग्स' : 'Leagues'), icon: Trophy },
    { id: 'ir', label: language === 'hi' ? 'आंकड़े' : (language === 'mr' ? 'स्टेट्स' : 'Stats'), icon: ChartBar },
    { id: 'eval', label: language === 'hi' ? 'अधिक' : (language === 'mr' ? 'अधिक' : 'More'), icon: Ellipsis },
  ];

  return (
    <header className={`sticky bottom-0 z-50 backdrop-blur-md border-t ${theme === 'dark' ? 'bg-slate-900/90 border-slate-800' : 'bg-white/90 border-slate-200'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 gap-2">
          {/* Brand Logo (centered) */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-500 to-emerald-400 p-0.5 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <span className="text-xl font-black bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">CB</span>
              </div>
            </div>
            <div className="hidden sm:block">
              <span className={`font-extrabold text-lg tracking-tight ${theme === 'dark' ? 'text-white' : 'text-slate-900'}`}>Cric<span className="text-blue-500">Bhasha</span></span>
            </div>
          </div>

          {/* Navigation Links - Bottom Tab Bar */}
          <nav className="flex space-x-4">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex flex-col items-center justify-center w-10 p-1 rounded-md transition-all duration-150 ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/20' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100/20')
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="mt-[2px] text-xs font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Theme Toggle & Language Selector (right-aligned) */}
          <div className="flex items-center gap-2">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className={`p-1 rounded-lg border transition-colors ${
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
      </div>
    </header>
  );
}
