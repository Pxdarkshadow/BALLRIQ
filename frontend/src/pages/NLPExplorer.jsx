import React, { useState, useEffect } from 'react';
import { Cpu, Tag, BarChart3, ShieldCheck, RefreshCw, Zap } from 'lucide-react';

export default function NLPExplorer({ language }) {
  const [inputText, setInputText] = useState('कोहली ने शानदार कवर ड्राइव से चौका जड़ा');
  const [prediction, setPrediction] = useState(null);
  const [entities, setEntities] = useState(null);
  const [loading, setLoading] = useState(false);

  const samples = [
    { label: 'Hindi Four', text: 'कोहली ने शानदार कवर ड्राइव से चौका जड़ा' },
    { label: 'Marathi Six', text: 'रोहितने लाँग-ऑनवर अप्रतिम षटकार मारला' },
    { label: 'Hindi Wicket', text: 'बुमराह की गेंद पर बल्लेबाज बोल्ड होकर पवेलियन लौटा' },
    { label: 'Marathi Wicket', text: 'मोहम्मद शमीच्या चेंडूवर फलंदाज बाद झाला' },
    { label: 'Hinglish Dot', text: 'Good bowling by Hardik, dot ball no run given' }
  ];

  useEffect(() => {
    runAnalysis(inputText);
  }, []);

  const runAnalysis = async (textToTest) => {
    const text = textToTest || inputText;
    if (!text.trim()) return;

    setLoading(true);
    try {
      const [resClf, resEnt] = await Promise.all([
        fetch('/api/nlp/classify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        }),
        fetch('/api/nlp/entities', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        })
      ]);

      if (resClf.ok) {
        const dataClf = await resClf.json();
        setPrediction(dataClf);
      }
      if (resEnt.ok) {
        const dataEnt = await resEnt.json();
        setEntities(dataEnt);
      }
    } catch (e) {
      console.error('Error during NLP analysis:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-purple-600/20 text-purple-400 rounded-lg border border-purple-500/30">
            <Cpu className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-black text-white tracking-tight">Player & Play Highlights Extraction</h1>
        </div>
        <p className="text-xs text-slate-400">
          Automatic event recognition and player mention tracking from live match commentary.
        </p>
      </div>

      {/* Input Console */}
      <div className="glass-card p-6 border-slate-800 space-y-4">
        <div className="flex flex-wrap gap-2 items-center justify-between">
          <span className="text-xs font-bold text-slate-300">Sample Commentary Highlights:</span>
          <div className="flex flex-wrap gap-2">
            {samples.map((s, i) => (
              <button
                key={i}
                onClick={() => {
                  setInputText(s.text);
                  runAnalysis(s.text);
                }}
                className="px-2.5 py-1 text-xs rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium transition-colors"
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter multilingual cricket commentary line..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500"
          />
          <button
            onClick={() => runAnalysis()}
            disabled={loading}
            className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-purple-600/20 transition-all"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            Analyze Play
          </button>
        </div>
      </div>

      {/* Analysis Output Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Col: Event Classification & Probabilities */}
        <div className="glass-card p-6 border-slate-800 space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" /> Identified Match Event
            </h2>
            <span className="text-[11px] text-slate-400 font-mono">Match Event Tagger</span>
          </div>

          {prediction && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-900/80 rounded-xl border border-slate-800">
                <div>
                  <span className="text-xs text-slate-400 font-bold block mb-1">MATCH EVENT</span>
                  <div className="text-2xl font-black text-purple-400 font-mono tracking-wide">{prediction.predicted_event}</div>
                </div>
                <div className="text-right">
                  <span className="text-xs text-slate-400 font-bold block mb-1">CONFIDENCE</span>
                  <div className="text-2xl font-black text-emerald-400 font-mono">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* All Probabilities Bar Chart */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-300 block">Event Probability Distribution:</span>
                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {prediction.all_probabilities && Object.entries(prediction.all_probabilities)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 6)
                    .map(([cls, prob], idx) => (
                      <div key={idx} className="text-xs space-y-0.5">
                        <div className="flex justify-between text-slate-300 font-mono text-[11px]">
                          <span className={cls === prediction.predicted_event ? 'text-purple-400 font-bold' : 'text-slate-400'}>{cls}</span>
                          <span>{(prob * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${cls === prediction.predicted_event ? 'bg-purple-500' : 'bg-slate-600'}`}
                            style={{ width: `${Math.max(3, prob * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Col: Entity Extraction & Structured Output */}
        <div className="glass-card p-6 border-slate-800 space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h2 className="text-sm font-bold text-slate-200 flex items-center gap-2">
              <Tag className="w-4 h-4 text-blue-400" /> Player Mentions & Play Details
            </h2>
            <span className="text-[11px] text-slate-400 font-mono">Player & Play Parser</span>
          </div>

          {entities && (
            <div className="space-y-4 text-xs">
              {/* Entity Tags */}
              <div className="space-y-2">
                <span className="text-slate-400 font-bold block">Identified Players & Match Roles:</span>
                <div className="flex flex-wrap gap-1.5">
                  {(entities.entities || []).length === 0 ? (
                    <span className="text-slate-500 italic">No specific player mentions extracted.</span>
                  ) : (
                    entities.entities.map((ent, idx) => (
                      <span key={idx} className="px-2.5 py-1 rounded-md bg-blue-950/40 border border-blue-800/60 text-blue-300 font-medium">
                        <span className="text-slate-400 font-normal">{ent.entity_type || 'PLAYER'}:</span> {ent.canonical || ent.original}
                      </span>
                    ))
                  )}
                </div>
              </div>

              {/* Structured JSON Event Representation */}
              <div className="space-y-1.5">
                <span className="text-slate-400 font-bold block">Structured Play Summary:</span>
                <pre className="p-3 bg-slate-900 rounded-lg border border-slate-800 font-mono text-[11px] text-emerald-400 overflow-x-auto">
                  {JSON.stringify(entities.structured_event || {
                    event: prediction?.predicted_event || "FOUR",
                    player: entities.player_mentions?.[0] || "Virat Kohli",
                    confidence: prediction?.confidence || 0.97
                  }, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
