import React, { useState, useEffect } from 'react';
import { Search, Sliders, Layers, RefreshCw, Zap } from 'lucide-react';

export default function IRExplorer({ language }) {
  const [query, setQuery] = useState('Kohli boundary four six');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alpha, setAlpha] = useState(0.5);

  const sampleQueries = [
    { label: 'English Boundary', query: 'Virat Kohli boundary four six' },
    { label: 'Hindi Boundary', query: 'कोहली चौका छक्का सीमा रेखा' },
    { label: 'Marathi Boundary', query: 'कोहलीने मारलेला चौकार किंवा षटकार' },
    { label: 'English Wicket', query: 'Jasprit Bumrah wicket bowled caught' },
    { label: 'Hindi Wicket', query: 'बुमराह विकेट बोल्ड आउट' },
    { label: 'Marathi Wicket', query: 'बुमराहने घेतलेली विकेट बाद' }
  ];

  useEffect(() => {
    const savedSearch = sessionStorage.getItem('ballriq-search');
    if (savedSearch) {
      setQuery(savedSearch);
      runSearch(savedSearch);
      sessionStorage.removeItem('ballriq-search');
    } else {
      runSearch(query);
    }
  }, []);

  const runSearch = async (queryText) => {
    const q = queryText || query;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`/api/ir/compare?query=${encodeURIComponent(q)}&top_k=5`);
      if (res.ok) {
        const data = await res.json();
        setComparison(data);
      }
    } catch (e) {
      console.error('Error running IR comparison:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
            <Search className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-black text-white tracking-tight">Cricket Stats & Commentary Search Engine</h1>
        </div>
        <p className="text-xs text-slate-400">
          Search across 15,000+ multilingual cricket moments using keyword, context-aware, and combined search options.
        </p>
      </div>

      {/* Query Bar */}
      <div className="glass-card p-6 border-slate-800 space-y-4">
        <div className="flex flex-wrap gap-2 items-center justify-between">
          <span className="text-xs font-bold text-slate-300">Sample Match Search Queries:</span>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((sq, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(sq.query);
                  runSearch(sq.query);
                }}
                className="px-2.5 py-1 text-xs rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium transition-colors"
              >
                {sq.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Type query in English, Hindi, or Marathi..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={() => runSearch()}
            disabled={loading}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-blue-600/20 transition-all"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            Search Moments
          </button>
        </div>
      </div>

      {/* 4-Way Side-by-Side Results Grid */}
      {comparison && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* 1. TF-IDF */}
          <div className="glass-card p-4 border-slate-800 space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-bold text-slate-300">Keyword Match Search</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">Keyword Match</span>
              </div>
              <div className="space-y-2.5">
                {comparison.methods?.tfidf?.results?.map((doc, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-blue-400">Rank #{doc.rank || idx + 1}</span>
                      <span className="font-mono text-emerald-400">Score: {doc.score?.toFixed(3)}</span>
                    </div>
                    <p className="text-slate-300 line-clamp-2 text-[11px] leading-snug">{doc.content}</p>
                    <div className="text-[9px] text-slate-500 font-mono">{doc.match_id} • Over {doc.over}.{doc.ball}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 2. BM25 */}
          <div className="glass-card p-4 border-slate-800 space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-bold text-blue-300">Relevance Search</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 font-mono">High Relevance</span>
              </div>
              <div className="space-y-2.5">
                {comparison.methods?.bm25?.results?.map((doc, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-blue-400">Rank #{doc.rank || idx + 1}</span>
                      <span className="font-mono text-emerald-400">Score: {doc.score?.toFixed(3)}</span>
                    </div>
                    <p className="text-slate-300 line-clamp-2 text-[11px] leading-snug">{doc.content}</p>
                    <div className="text-[9px] text-slate-500 font-mono">{doc.match_id} • Over {doc.over}.{doc.ball}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 3. Semantic Vector Search */}
          <div className="glass-card p-4 border-slate-800 space-y-3 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-bold text-purple-300">Contextual / Meaning Search</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 font-mono">Context Aware</span>
              </div>
              <div className="space-y-2.5">
                {comparison.methods?.semantic?.results?.map((doc, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-purple-400">Rank #{doc.rank || idx + 1}</span>
                      <span className="font-mono text-emerald-400">Score: {doc.score?.toFixed(3)}</span>
                    </div>
                    <p className="text-slate-300 line-clamp-2 text-[11px] leading-snug">{doc.content}</p>
                    <div className="text-[9px] text-slate-500 font-mono">{doc.match_id} • Over {doc.over}.{doc.ball}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 4. Hybrid Search */}
          <div className="glass-card p-4 border-slate-800 space-y-3 flex flex-col justify-between bg-blue-950/10 border-blue-500/40">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
                <span className="text-xs font-bold text-emerald-400">Combined Smart Search</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono font-bold">Top Recommended</span>
              </div>
              <div className="space-y-2.5">
                {comparison.methods?.hybrid?.results?.map((doc, idx) => (
                  <div key={idx} className="p-2.5 rounded-lg bg-slate-900/90 border border-blue-500/30 text-xs space-y-1 shadow-sm">
                    <div className="flex justify-between items-center text-[10px] text-slate-400">
                      <span className="font-bold text-emerald-400">Rank #{doc.rank || idx + 1}</span>
                      <span className="font-mono text-emerald-400">Score: {doc.score?.toFixed(3)}</span>
                    </div>
                    <p className="text-slate-200 line-clamp-2 text-[11px] leading-snug font-medium">{doc.content}</p>
                    <div className="text-[9px] text-slate-400 font-mono">{doc.match_id} • Over {doc.over}.{doc.ball}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
