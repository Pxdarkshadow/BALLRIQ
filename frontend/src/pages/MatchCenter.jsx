import React, { useState, useEffect } from 'react';
import { Play, Shield, MessageSquare, Send, Sparkles, Clock, Award, BarChart2, Flame, Users, Info, Activity } from 'lucide-react';

export default function MatchCenter({ language }) {
  const [matches, setMatches] = useState([]);
  const [selectedMatchId, setSelectedMatchId] = useState('');
  const [matchDetail, setMatchDetail] = useState(null);
  const [activeSubTab, setActiveSubTab] = useState('overview');
  const [commentaryLang, setCommentaryLang] = useState(language);
  const [commentaryInfo, setCommentaryInfo] = useState({ total: 0, items: [] });
  const [commType, setCommType] = useState('ALL');
  const [players, setPlayers] = useState([]);
  const [eventsData, setEventsData] = useState([]);
  const [phaseStats, setPhaseStats] = useState([]);

  // RAG QA state
  const [qaQuestion, setQaQuestion] = useState('');
  const [qaHistory, setQaHistory] = useState([]);
  const [qaLoading, setQaLoading] = useState(false);
  const [suggestedQueries, setSuggestedQueries] = useState([]);

  useEffect(() => { fetchMatches(); }, []);

  useEffect(() => {
    if (selectedMatchId) {
      fetchMatchDetail(selectedMatchId);
      fetchPlayers(selectedMatchId);
      fetchEvents(selectedMatchId);
      fetchSuggestedQuestions(selectedMatchId);
      fetchPhaseStats(selectedMatchId);
    }
  }, [selectedMatchId]);

  useEffect(() => {
    if (selectedMatchId) {
      let url = `/api/matches/${selectedMatchId}/commentary?limit=200`;
      if (commentaryLang) url += `&language=${commentaryLang}`;
      if (commType !== 'ALL' && commType !== 'KEY') url += `&event_type=${commType}`;

      fetch(url)
        .then(r => r.json())
        .then(d => {
          let items = d.items || [];
          if (commType === 'KEY') items = items.filter(c => ['FOUR', 'SIX', 'WICKET'].includes(c.event_label));
          setCommentaryInfo({ items, total: d.total || items.length });
        })
        .catch(e => console.error(e));
    }
  }, [selectedMatchId, commentaryLang, commType]);

  useEffect(() => { setCommentaryLang(language); }, [language]);

  const fetchMatches = async () => {
    try {
      const res = await fetch('/api/matches');
      if (res.ok) {
        const data = await res.json();
        // API returns a JSON ARRAY of matches
        const ms = Array.isArray(data) ? data : data.matches || [];
        setMatches(ms);
        if (ms.length > 0) setSelectedMatchId(ms[0].match_id);
      }
    } catch (e) { console.error('Error fetching matches:', e); }
  };

  const fetchMatchDetail = async (id) => {
    try {
      const res = await fetch(`/api/matches/${id}`);
      if (res.ok) setMatchDetail(await res.json());
    } catch (e) { console.error('Error fetching match detail:', e); }
  };

  const fetchPlayers = async (id) => {
    try {
      const res = await fetch(`/api/matches/${id}/players`);
      if (res.ok) setPlayers(await res.json());
    } catch (e) { console.error('Error fetching players:', e); }
  };

  const fetchEvents = async (id) => {
    try {
      const res = await fetch(`/api/matches/${id}/events`);
      if (res.ok) setEventsData(await res.json());
    } catch (e) { console.error('Error fetching events:', e); }
  };

  const fetchPhaseStats = async (id) => {
    try {
      const res = await fetch(`/api/bda/phase-analytics?match_id=${id}`);
      if (res.ok) setPhaseStats(await res.json() || []);
    } catch (e) { console.error('Error fetching phase stats:', e); }
  };

  const fetchSuggestedQuestions = async (id) => {
    try {
      const res = await fetch(`/api/rag/suggested-questions/${id}`);
      if (res.ok) {
        const data = await res.json();
        const langKey = language === 'hi' ? 'hi' : (language === 'mr' ? 'mr' : 'en');
        setSuggestedQueries(data.questions?.[langKey] || data.questions?.['en'] || []);
      }
    } catch (e) { console.error('Error fetching questions:', e); }
  };

  const handleAskRAG = async (qText) => {
    const queryToAsk = qText || qaQuestion;
    if (!queryToAsk.trim()) return;

    setQaLoading(true);
    setQaHistory(prev => [...prev, { sender: 'user', text: queryToAsk }]);
    setQaQuestion('');

    try {
      const res = await fetch('/api/rag/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryToAsk, match_id: selectedMatchId, language })
      });
      if (res.ok) {
        const data = await res.json();
        setQaHistory(prev => [...prev, { sender: 'bot', ...data }]);
      }
    } catch (e) {
      setQaHistory(prev => [...prev, { sender: 'bot', answer: 'Failed to connect to RAG server.', is_grounded: false, citations: [] }]);
    } finally {
      setQaLoading(false);
    }
  };

  const selectedMatch = matches.find(m => m.match_id === selectedMatchId) || matches[0] || {};
  const innings = [...(matchDetail?.innings || [])].sort((a,b) => a.innings_number - b.innings_number);

  // Tie player_id to names for UI if we have them
  const pMap = Object.fromEntries(players.map(p => [p.player_id, p]));
  const pName = (id) => pMap[id]?.name || id;

  const topBatter = innings.flatMap(i => i.batting_stats || []).sort((a,b) => (b.runs || 0) - (a.runs || 0))[0];

  // Momentum sparkline data
  const oversMap = new Map();
  let maxRunsInOver = 0;
  [...(commentaryInfo.items)].reverse().forEach(c => {
    if (c.over == null) return;
    const runs = c.event_label === 'SIX' ? 6 : c.event_label === 'FOUR' ? 4 : c.event_label === 'TRIPLE' ? 3 : c.event_label === 'DOUBLE' ? 2 : c.event_label === 'SINGLE' ? 1 : 0;
    const o = c.over;
    if (!oversMap.has(o)) oversMap.set(o, 0);
    const sum = oversMap.get(o) + runs;
    oversMap.set(o, sum);
    if (sum > maxRunsInOver) maxRunsInOver = sum;
  });
  const sparkData = Array.from(oversMap.entries()).sort((a,b) => a[0] - b[0]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-bold tracking-wider text-slate-400 uppercase flex items-center gap-2">
            <Play className="w-4 h-4 text-blue-400 fill-blue-400" />
            {language === 'hi' ? 'मैच सूची' : (language === 'mr' ? 'सामने यादी' : 'Matches')}
          </h2>
          <span className="text-xs text-slate-500 font-mono">{matches.length} matches indexed</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {matches.slice(0, 4).map((m) => {
            const isSelected = m.match_id === selectedMatchId;
            return (
              <div
                key={m.match_id}
                onClick={() => setSelectedMatchId(m.match_id)}
                className={`cursor-pointer p-3.5 rounded-xl border transition-all ${
                  isSelected ? 'bg-blue-950/40 border-blue-500/80 shadow-lg shadow-blue-500/10' : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-2">
                  <span className="font-semibold text-blue-400 uppercase">{m.format}</span>
                  <span>{m.tournament}</span>
                </div>
                <div className="space-y-1 text-sm font-bold text-slate-200">
                  <div className="flex justify-between items-center">
                    <span>{m.team_a}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>{m.team_b}</span>
                  </div>
                </div>
                <div className="mt-2.5 pt-2 border-t border-slate-800/80 text-[11px] text-emerald-400 font-medium truncate">
                  {m.result || `${m.winner} won`}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card p-6 relative overflow-hidden bg-slate-900/60 rounded-xl border border-slate-800">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl -z-10"></div>
            <div className="flex justify-between items-start text-xs text-slate-400 mb-4 pb-3 border-b border-slate-800">
              <span className="font-bold text-slate-300">{selectedMatch?.tournament} • {selectedMatch?.venue}</span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-bold">COMPLETED</span>
            </div>

            <div className="grid grid-cols-3 items-center text-center py-4">
              <div className="space-y-1">
                <div className="w-12 h-12 mx-auto rounded-full bg-slate-800 flex items-center justify-center font-black text-blue-400 border border-slate-700 text-lg">
                  {selectedMatch?.team_a?.slice(0, 2).toUpperCase()}
                </div>
                <div className="font-bold text-slate-100 text-base">{selectedMatch?.team_a}</div>
                <div className="text-xl font-extrabold text-blue-400 font-mono">
                  {innings[0] ? `${innings[0].total_runs}/${innings[0].wickets}` : "—"}
                  {innings[0] && <span className="text-xs text-slate-400 font-normal"> ({innings[0].overs?.toFixed(1)})</span>}
                </div>
              </div>

              <div className="space-y-1">
                <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">VS</span>
                <div className="text-xs font-semibold text-emerald-400">{selectedMatch?.result}</div>
                <div className="text-[11px] text-slate-400">
                  {selectedMatch.toss_winner ? `Toss: ${selectedMatch.toss_winner} elected to ${selectedMatch.toss_decision}` : ''}
                </div>
              </div>

              <div className="space-y-1">
                <div className="w-12 h-12 mx-auto rounded-full bg-slate-800 flex items-center justify-center font-black text-emerald-400 border border-slate-700 text-lg">
                  {selectedMatch?.team_b?.slice(0, 2).toUpperCase()}
                </div>
                <div className="font-bold text-slate-100 text-base">{selectedMatch?.team_b}</div>
                <div className="text-xl font-extrabold text-slate-200 font-mono">
                  {innings[1] ? `${innings[1].total_runs}/${innings[1].wickets}` : "—"}
                  {innings[1] && <span className="text-xs text-slate-400 font-normal"> ({innings[1].overs?.toFixed(1)})</span>}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-4 border-b border-slate-800 mt-4 text-xs font-bold">
              {[
                { id: 'overview', icon: Info, label: 'Overview' },
                { id: 'timeline', icon: Clock, label: 'Timeline' },
                { id: 'scorecard', icon: Award, label: 'Scorecard' },
                { id: 'players', icon: Users, label: 'Players' },
                { id: 'momentum', icon: Activity, label: 'Momentum' },
                { id: 'bda-phase', icon: BarChart2, label: 'BDA Analytics' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveSubTab(tab.id)}
                  className={`pb-2.5 transition-colors flex items-center gap-1.5 ${
                    activeSubTab === tab.id ? 'text-blue-400 border-b-2 border-blue-500' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {activeSubTab === 'overview' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Match Overview</h3>
              <div className="text-xs text-slate-300">
                {selectedMatch.result}. {innings.map(i => `${i.batting_team} scored ${i.total_runs}/${i.wickets}`).join(', ')}.
                {topBatter && ` Top batter: ${pName(topBatter.player_id)} (${topBatter.runs} runs)`}
              </div>

              <div className="mt-4">
                <h4 className="text-[11px] font-bold text-slate-400 uppercase mb-2">Key Events</h4>
                <div className="flex gap-4">
                  {eventsData && eventsData.map((e, idx) => (
                    <div key={idx} className="bg-slate-800/50 p-2 rounded text-center border border-slate-700 flex-1">
                      <div className="text-lg font-mono text-blue-400">{e.count}</div>
                      <div className="text-[10px] text-slate-400 uppercase">{e.event}</div>
                    </div>
                  ))}
                  {(!eventsData || eventsData.length === 0) && <div className="text-xs text-slate-500">No event summary available</div>}
                </div>
              </div>
            </div>
          )}

          {activeSubTab === 'timeline' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <Flame className="w-4 h-4 text-amber-400" />
                  Live Commentary
                </h3>
                <div className="flex gap-2">
                  <select
                    value={commType}
                    onChange={e => setCommType(e.target.value)}
                    className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded px-2 py-1 outline-none"
                  >
                    <option value="ALL">All Events</option>
                    <option value="KEY">Key Moments</option>
                    <option value="WICKET">Wickets</option>
                    <option value="FOUR">Fours</option>
                    <option value="SIX">Sixes</option>
                  </select>
                  <div className="flex bg-slate-800/80 rounded border border-slate-700/60 text-xs">
                    {['en', 'hi', 'mr'].map(l => (
                      <button key={l} onClick={() => setCommentaryLang(l)} className={`px-2 py-1 ${commentaryLang === l ? 'bg-blue-600 text-white font-bold rounded' : 'text-slate-400'}`}>
                        {l.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                {commentaryInfo.items.map((comm) => {
                  const isBoundary = comm.event_label === 'FOUR' || comm.event_label === 'SIX';
                  const isWicket = comm.event_label === 'WICKET';
                  return (
                    <div key={comm.commentary_id} className={`p-3 rounded-lg border text-xs transition-colors ${
                      isWicket ? 'bg-red-950/20 border-red-800/40 text-red-100' :
                      isBoundary ? 'bg-blue-950/20 border-blue-800/40 text-blue-100' :
                      'bg-slate-900/50 border-slate-800/80 text-slate-300'
                    }`}>
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center space-x-2">
                          <span className="px-2 py-0.5 font-mono font-bold bg-slate-800 text-slate-300 rounded text-[11px]">
                            {comm.over != null && comm.ball != null ? `${comm.over}.${comm.ball}` : '-'}
                          </span>
                          {comm.event_label && (
                            <span className={`font-black text-[10px] px-1.5 py-0.5 rounded uppercase ${
                              isWicket ? 'bg-red-500 text-white' :
                              comm.event_label === 'SIX' ? 'bg-purple-600 text-white' :
                              comm.event_label === 'FOUR' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'
                            }`}>
                              {comm.event_label}
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-slate-500">{comm.language || commentaryLang}</span>
                      </div>
                      <p className="text-slate-200 leading-relaxed font-sans">{comm.original_text || comm.normalized_text}</p>
                    </div>
                  );
                })}
                {commentaryInfo.items.length === 0 && <div className="text-slate-500 text-xs text-center py-4">No commentary available.</div>}
              </div>
            </div>
          )}

          {activeSubTab === 'scorecard' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-6">
              {innings.map(inn => (
                <div key={inn.id}>
                  <h3 className="text-sm font-bold text-slate-200 mb-3">{inn.batting_team} Innings</h3>
                  {inn.batting_stats?.length > 0 && (
                    <div className="overflow-x-auto mb-4">
                      <table className="w-full text-xs text-left mb-2">
                        <thead className="text-[11px] uppercase bg-slate-800/60 text-slate-400">
                          <tr><th className="py-2 px-3">Batter</th><th className="py-2 px-2">R</th><th className="py-2 px-2">B</th><th className="py-2 px-2">4s</th><th className="py-2 px-2">6s</th><th className="py-2 px-2">SR</th></tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {inn.batting_stats.map(b => (
                            <tr key={b.id} className="hover:bg-slate-800/30">
                              <td className="py-2 px-3 font-sans font-bold text-slate-200">
                                {pName(b.player_id)}
                                {b.dismissal && <div className="text-[10px] text-slate-500 font-normal">{b.dismissal}</div>}
                              </td>
                              <td className="py-2 px-2 font-bold text-blue-400">{b.runs}</td>
                              <td className="py-2 px-2 text-slate-300">{b.balls}</td>
                              <td className="py-2 px-2 text-slate-400">{b.fours}</td>
                              <td className="py-2 px-2 text-purple-400">{b.sixes}</td>
                              <td className="py-2 px-2 text-emerald-400">{b.strike_rate}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {inn.bowling_stats?.length > 0 && (
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left">
                        <thead className="text-[11px] uppercase bg-slate-800/60 text-slate-400">
                          <tr><th className="py-2 px-3">Bowler</th><th className="py-2 px-2">O</th><th className="py-2 px-2">R</th><th className="py-2 px-2">W</th><th className="py-2 px-2">Econ</th></tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {inn.bowling_stats.map(b => (
                            <tr key={b.id} className="hover:bg-slate-800/30">
                              <td className="py-2 px-3 font-sans font-bold text-slate-200">{pName(b.player_id)}</td>
                              <td className="py-2 px-2 text-slate-300">{b.overs}</td>
                              <td className="py-2 px-2 text-slate-400">{b.runs_conceded}</td>
                              <td className="py-2 px-2 font-bold text-blue-400">{b.wickets}</td>
                              <td className="py-2 px-2 text-emerald-400">{b.economy}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
              {innings.length === 0 && <div className="text-slate-500 text-xs">Scorecard unavailable.</div>}
            </div>
          )}

          {activeSubTab === 'players' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Players</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {players.map(p => (
                  <div key={p.player_id} className="p-3 bg-slate-800/40 rounded border border-slate-700/50">
                    <div className="font-bold text-sm text-slate-200">{p.name || p.player_id}</div>
                    <div className="text-[11px] text-slate-400 mt-1">{p.team} • {p.role}</div>
                  </div>
                ))}
                {players.length === 0 && <div className="col-span-full py-4 text-center text-xs text-slate-500">No squad data</div>}
              </div>
            </div>
          )}

          {activeSubTab === 'momentum' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Run Momentum (Per Over)</h3>
              {sparkData.length > 0 ? (
                <div className="h-32 flex items-end gap-[2px] mt-6">
                  {sparkData.map(([o, runs]) => {
                    const h = maxRunsInOver > 0 ? (runs / maxRunsInOver) * 100 : 0;
                    return (
                      <div key={o} className="group relative flex-1 flex flex-col items-center select-none" style={{ minWidth: '4px' }}>
                        <div className="w-full bg-blue-500 hover:bg-blue-400 transition-colors" style={{ height: `${Math.max(4, h)}%`, borderRadius: '4px 4px 0 0' }}></div>
                        <div className="opacity-0 group-hover:opacity-100 absolute -top-8 bg-slate-800 text-white text-[10px] px-2 py-1 rounded shadow-lg border border-slate-700 whitespace-nowrap z-10 pointer-events-none">
                          Over {o}: {runs} runs
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-slate-500 text-xs py-8 text-center">Graph requires event commentary</div>
              )}
            </div>
          )}

          {activeSubTab === 'bda-phase' && (
            <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-emerald-400" /> Phase Analytics
                </h3>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {phaseStats.map((p, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">{p.phase}</span>
                    <div className="text-2xl font-extrabold text-white font-mono">{p.total_runs} <span className="text-xs font-normal text-slate-400">runs</span></div>
                    <div className="text-[11px] text-slate-400 space-y-1 font-sans">
                      <div className="flex justify-between"><span>Run Rate:</span><span className="text-slate-200 font-bold">{p.estimated_run_rate}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="glass-card p-5 bg-slate-900/60 rounded-xl border border-slate-800 h-[650px] flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-2.5 pb-3 border-b border-slate-800">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center border border-blue-500/30">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-100">Ask BALLRIQ AI</h3>
                  <p className="text-[11px] text-slate-400">Grounded Hybrid RAG</p>
                </div>
              </div>
              <div className="mt-3">
                <div className="flex flex-wrap gap-1.5">
                  {suggestedQueries.slice(0, 3).map((sq, i) => (
                    <button key={i} onClick={() => handleAskRAG(sq)} className="text-[11px] text-left px-2.5 py-1 rounded-md bg-slate-800/80 hover:bg-slate-800 border border-slate-700/60 text-slate-300">
                      {sq}
                    </button>
                  ))}
                </div>
              </div>
              <div className="mt-4 space-y-3 max-h-[380px] overflow-y-auto pr-1">
                {qaHistory.length === 0 ? (
                  <div className="text-center py-12 text-slate-500 text-xs">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40 text-blue-400" />
                    Ask natural language questions about players, overs, wickets, boundaries, or turning points in Hindi, Marathi, or English.
                  </div>
                ) : (
                  qaHistory.map((msg, i) => (
                    <div key={i} className={`text-xs space-y-1.5 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                      <div className={`inline-block p-3 rounded-xl max-w-[90%] text-left ${msg.sender === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-800/90 border border-slate-700/80 text-slate-100 rounded-bl-none'}`}>
                        <p>{msg.text || msg.answer}</p>
                        {msg.citations?.length > 0 && (
                          <div className="mt-2.5 pt-2 border-t border-slate-700/60 text-[10px] space-y-1">
                            {msg.citations.map((c, ci) => (
                              <div key={ci} className="bg-slate-900/80 p-1 rounded border border-slate-800">
                                <span className="font-mono text-emerald-400 font-bold">Over {c.over}.{c.ball}</span> • {c.snippet}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
                {qaLoading && <div className="text-xs text-blue-400 flex items-center gap-2 p-2 bg-slate-800/40 rounded-lg"><Sparkles className="w-3.5 h-3.5 animate-spin" /> Retrieving...</div>}
              </div>
            </div>
            <div className="pt-3 border-t border-slate-800">
              <form onSubmit={e => { e.preventDefault(); handleAskRAG(); }} className="flex items-center gap-2">
                <input
                  type="text"
                  value={qaQuestion}
                  onChange={(e) => setQaQuestion(e.target.value)}
                  placeholder="Ask a question..."
                  className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 outline-none focus:border-blue-500"
                />
                <button type="submit" disabled={qaLoading || !qaQuestion.trim()} className="p-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg">
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}