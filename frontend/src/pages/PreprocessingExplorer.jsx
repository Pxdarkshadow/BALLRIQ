import React, { useState, useEffect } from 'react';
import { Sparkles, ArrowDown, CheckCircle2, RefreshCw } from 'lucide-react';

export default function PreprocessingExplorer({ language }) {
  const [inputText, setInputText] = useState('कोहली ने  शानदार!!!  चौका मारा और ४ रन लिए');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const sampleInputs = [
    { label: 'Hindi Boundary', text: 'कोहली ने  शानदार!!!  चौका मारा और ४ रन लिए' },
    { label: 'Marathi Wicket', text: 'बुमराहने अप्रतिम यॉर्कर टाकला आणि फलंदाज बाद झाला!!!' },
    { label: 'Code-Mixed Hinglish', text: 'Virat Kohli ne amazing cover drive maara and ball boundary paar gayi' },
    { label: 'Marathi Code-Mixed', text: 'कोहलीने super six मारला, काय shot होता तो' }
  ];

  useEffect(() => {
    runPreprocessing(inputText);
  }, []);

  const runPreprocessing = async (textToProcess) => {
    const text = textToProcess || inputText;
    if (!text.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/nlp/preprocess', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (e) {
      console.error('Error running preprocessing:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg border border-indigo-500/30">
            <Sparkles className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-black text-white tracking-tight">Multilingual NLP Preprocessing Pipeline</h1>
        </div>
        <p className="text-xs text-slate-400">
          Trace every granular string transformation step: Unicode normalization, text cleaning, language ID, number normalization, cricket terminology, player aliases, and tokenization.
        </p>
      </div>

      {/* Interactive Input Section */}
      <div className="glass-card p-6 border-slate-800 space-y-4">
        <div className="flex flex-wrap gap-2 items-center justify-between">
          <span className="text-xs font-bold text-slate-300">Preset Academic Test Samples:</span>
          <div className="flex flex-wrap gap-2">
            {sampleInputs.map((sample, i) => (
              <button
                key={i}
                onClick={() => {
                  setInputText(sample.text);
                  runPreprocessing(sample.text);
                }}
                className="px-2.5 py-1 text-xs rounded-md bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 font-medium transition-colors"
              >
                {sample.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type raw cricket commentary in Hindi, Marathi, or English..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            onClick={() => runPreprocessing()}
            disabled={loading}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl flex items-center gap-2 shadow-lg shadow-indigo-600/20 transition-all"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Transform Pipeline
          </button>
        </div>
      </div>

      {/* Step-by-Step Transformation Ladder */}
      {result && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Step Breakdown */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Step-by-Step Pipeline Execution ({result.steps?.length || 7} Steps)
            </h2>

            <div className="space-y-3">
              {result.steps?.map((step, idx) => (
                <div key={idx} className="glass-card p-4 border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-400 flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-indigo-500/20 flex items-center justify-center text-[10px] font-black border border-indigo-500/40">
                        {idx + 1}
                      </span>
                      {step.step_name?.replace(/_/g, ' ').toUpperCase()}
                    </span>
                    <span className="text-[10px] text-slate-500 uppercase font-mono">{step.operation || 'Transformation'}</span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                    <div className="p-2.5 bg-slate-900/60 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-500 font-bold block mb-1 uppercase">Input</span>
                      <p className="text-slate-400 font-mono break-all">{step.input_text || result.original_text}</p>
                    </div>
                    <div className="p-2.5 bg-indigo-950/20 rounded-lg border border-indigo-800/40">
                      <span className="text-[10px] text-indigo-400 font-bold block mb-1 uppercase">Transformed Output</span>
                      <p className="text-indigo-200 font-mono font-semibold break-all">{step.output_text || result.final_text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right 1 Col: Language & Tokenization Summary */}
          <div className="space-y-4">
            <div className="glass-card p-5 border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Pipeline Inspection Metadata
              </h3>

              <div className="space-y-3 text-xs">
                <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 space-y-1">
                  <span className="text-slate-400 font-medium">Detected Language:</span>
                  <div className="text-base font-bold text-white font-mono uppercase">{result.detected_language}</div>
                  <div className="text-[11px] text-slate-500">Confidence: {(result.language_confidence * 100).toFixed(1)}% • Code-Mixed: {result.is_code_mixed ? 'Yes' : 'No'}</div>
                </div>

                <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 space-y-1">
                  <span className="text-slate-400 font-medium">Final Normalized Representation:</span>
                  <p className="text-emerald-400 font-mono font-bold break-all">{result.final_text}</p>
                </div>

                <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 space-y-2">
                  <span className="text-slate-400 font-medium">Tokenized Output Array ({result.tokens?.length || 0}):</span>
                  <div className="flex flex-wrap gap-1">
                    {result.tokens?.map((t, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-200 font-mono text-[11px]">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
