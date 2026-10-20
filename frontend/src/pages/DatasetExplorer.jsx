import React, { useState, useEffect } from 'react';
import { Database, FileText, Globe, Layers, CheckCircle2 } from 'lucide-react';

export default function DatasetExplorer({ language }) {
  const [stats, setStats] = useState(null);
  const [activeSchemaTab, setActiveSchemaTab] = useState('commentary');

  useEffect(() => {
    fetchDatasetStats();
  }, []);

  const fetchDatasetStats = async () => {
    try {
      const res = await fetch('/api/evaluation/dataset-stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Error fetching dataset stats:', e);
    }
  };

  const schemas = {
    matches: [
      { field: 'match_id', type: 'VARCHAR (PK)', desc: 'Unique identifier for cricket match (e.g. M001)' },
      { field: 'date', type: 'DATE', desc: 'Date when the match was played' },
      { field: 'format', type: 'VARCHAR', desc: 'Cricket match format (T20, ODI, Test)' },
      { field: 'tournament', type: 'VARCHAR', desc: 'League or tournament title' },
      { field: 'venue', type: 'VARCHAR', desc: 'Stadium and city' },
      { field: 'team_a', type: 'VARCHAR', desc: 'Home / First Batting Team' },
      { field: 'team_b', type: 'VARCHAR', desc: 'Away / Second Batting Team' },
      { field: 'winner', type: 'VARCHAR', desc: 'Winning team or Draw' },
      { field: 'result', type: 'VARCHAR', desc: 'Detailed match verdict' }
    ],
    commentary: [
      { field: 'commentary_id', type: 'VARCHAR (PK)', desc: 'Unique commentary ball ID (e.g. M001_C_018)' },
      { field: 'match_id', type: 'VARCHAR (FK)', desc: 'Reference to parent match' },
      { field: 'language', type: 'VARCHAR', desc: 'Language tag (hi, mr, en, mixed)' },
      { field: 'original_text', type: 'TEXT', desc: 'Live multilingual commentary transcript' },
      { field: 'normalized_text', type: 'TEXT', desc: 'Cleaned text with standardized entities' },
      { field: 'over', type: 'INTEGER', desc: 'Match over number (0-19)' },
      { field: 'ball', type: 'INTEGER', desc: 'Ball number within over (1-6)' },
      { field: 'event_label', type: 'VARCHAR', desc: 'Play event class (FOUR, SIX, WICKET, etc.)' }
    ],
    audio: [
      { field: 'audio_id', type: 'VARCHAR (PK)', desc: 'Audio snippet identifier' },
      { field: 'match_id', type: 'VARCHAR (FK)', desc: 'Parent match reference' },
      { field: 'language', type: 'VARCHAR', desc: 'Spoken language (Hindi / Marathi)' },
      { field: 'duration_sec', type: 'FLOAT', desc: 'Duration of commentary audio clip' },
      { field: 'transcript', type: 'TEXT', desc: 'Speech-to-text commentary transcription' }
    ]
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
            <Database className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-black text-white tracking-tight">Match Center News & Coverage Database</h1>
        </div>
        <p className="text-xs text-slate-400">
          Comprehensive match records and coverage: Match scores, multilingual commentary (Hindi/Marathi/English), and audio transcripts.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 border-slate-800 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Total Commentary Entries</span>
          <div className="text-3xl font-extrabold text-white font-mono">13,423</div>
          <div className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" /> Verified Match Data
          </div>
        </div>

        <div className="glass-card p-5 border-slate-800 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Commentary Languages</span>
          <div className="text-3xl font-extrabold text-blue-400 font-mono">3 Languages</div>
          <div className="text-[11px] text-slate-400 font-medium">5K Hindi • 5K Marathi • 3.4K English</div>
        </div>

        <div className="glass-card p-5 border-slate-800 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Archived Matches</span>
          <div className="text-3xl font-extrabold text-purple-400 font-mono">50 Matches</div>
          <div className="text-[11px] text-slate-400 font-medium">T20, ODI & Test Series</div>
        </div>

        <div className="glass-card p-5 border-slate-800 space-y-1">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Play Event Types</span>
          <div className="text-3xl font-extrabold text-amber-400 font-mono">12 Classes</div>
          <div className="text-[11px] text-slate-400 font-medium">FOUR, SIX, WICKET, DOT, etc.</div>
        </div>
      </div>

      {/* Dataset Breakdown & Methodology */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Languages & Events Charts */}
        <div className="glass-card p-6 border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-400" /> Language Distribution Breakdown
          </h2>
          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between mb-1 text-slate-300 font-medium">
                <span>Hindi (हिन्दी Commentary)</span>
                <span className="font-mono text-blue-400 font-bold">5,000 records (37.2%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full" style={{ width: '37.2%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-1 text-slate-300 font-medium">
                <span>Marathi (मराठी Commentary)</span>
                <span className="font-mono text-indigo-400 font-bold">5,000 records (37.2%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full rounded-full" style={{ width: '37.2%' }}></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between mb-1 text-slate-300 font-medium">
                <span>English (Commentary)</span>
                <span className="font-mono text-emerald-400 font-bold">3,423 records (25.6%)</span>
              </div>
              <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: '25.6%' }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Event Class Distribution */}
        <div className="glass-card p-6 border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <Layers className="w-4 h-4 text-purple-400" /> Match Event Distribution
          </h2>
          <div className="grid grid-cols-2 gap-2 text-xs font-mono">
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-slate-400 font-sans">DOT BALL</span>
              <span className="text-slate-200 font-bold">5,200</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-slate-400 font-sans">SINGLE</span>
              <span className="text-slate-200 font-bold">4,150</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-blue-400 font-sans font-bold">FOUR (चौका)</span>
              <span className="text-blue-400 font-bold">1,240</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-purple-400 font-sans font-bold">SIX (छक्का)</span>
              <span className="text-purple-400 font-bold">780</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-red-400 font-sans font-bold">WICKET (विकेट)</span>
              <span className="text-red-400 font-bold">590</span>
            </div>
            <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between">
              <span className="text-slate-400 font-sans">OTHER / EXTRAS</span>
              <span className="text-slate-200 font-bold">1,463</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dataset Schema Viewer */}
      <div className="glass-card p-6 border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <FileText className="w-4 h-4 text-emerald-400" /> Match Data Structure & Fields
          </h2>
          <div className="flex space-x-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/60 text-xs">
            <button
              onClick={() => setActiveSchemaTab('commentary')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeSchemaTab === 'commentary' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Ball-by-Ball Commentary
            </button>
            <button
              onClick={() => setActiveSchemaTab('matches')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeSchemaTab === 'matches' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Match Details
            </button>
            <button
              onClick={() => setActiveSchemaTab('audio')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeSchemaTab === 'audio' ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Audio Highlights
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-[11px] uppercase bg-slate-800/80 text-slate-400">
              <tr>
                <th className="py-3 px-4 font-bold">Field Name</th>
                <th className="py-3 px-4 font-bold">Data Type</th>
                <th className="py-3 px-4 font-bold">Description & Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-sans">
              {schemas[activeSchemaTab].map((row, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-mono font-bold text-blue-400">{row.field}</td>
                  <td className="py-3 px-4 font-mono text-emerald-400">{row.type}</td>
                  <td className="py-3 px-4 text-slate-300">{row.desc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
