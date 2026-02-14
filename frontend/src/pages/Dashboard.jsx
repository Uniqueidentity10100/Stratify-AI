import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, analysisAPI } from '../services/api';
import ProbabilityCard from '../components/ProbabilityCard';
import {
  Search, LogOut, Download, TrendingUp, TrendingDown,
  Globe, Newspaper, ExternalLink, Clock, Activity,
  DollarSign, Layers, Target, Zap, ChevronRight,
  BarChart3, Shield, AlertTriangle, FileText, Hash,
  ArrowUpRight, ArrowDownRight, Info
} from 'lucide-react';

// ══════════════════════════════════════════════════
//  HELPERS
// ══════════════════════════════════════════════════

const formatCurrency = (n) => {
  if (n == null || isNaN(n)) return '$0';
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `$${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `$${Number(n).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (n >= 1) return `$${Number(n).toFixed(2)}`;
  return `$${Number(n).toFixed(6)}`;
};

const formatPercent = (n) => {
  if (n == null || isNaN(n)) return '0.00%';
  const sign = n >= 0 ? '+' : '';
  return `${sign}${Number(n).toFixed(2)}%`;
};

const formatSupply = (n) => {
  if (!n || isNaN(n)) return '—';
  if (n >= 1e9) return `${(n / 1e9).toFixed(2)}B`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(2)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(1)}K`;
  return n.toLocaleString();
};

const getSentimentBadge = (s) => {
  if (s >= 0.7) return { text: 'Bullish', cls: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' };
  if (s >= 0.55) return { text: 'Positive', cls: 'text-green-400 bg-green-500/10 border-green-500/20' };
  if (s >= 0.45) return { text: 'Neutral', cls: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20' };
  if (s >= 0.3) return { text: 'Negative', cls: 'text-orange-400 bg-orange-500/10 border-orange-500/20' };
  return { text: 'Bearish', cls: 'text-red-400 bg-red-500/10 border-red-500/20' };
};

// ══════════════════════════════════════════════════
//  SUB-COMPONENTS
// ══════════════════════════════════════════════════

function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-center gap-3 mb-5">
      <div className="p-2.5 rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/15">
        <Icon className="w-5 h-5 text-blue-400" />
      </div>
      <div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="space-y-6 mt-8">
      {/* Coin profile skeleton */}
      <div className="glass rounded-2xl p-8">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 rounded-2xl shimmer bg-slate-800" />
          <div className="space-y-3 flex-1">
            <div className="h-8 w-48 shimmer bg-slate-800 rounded-xl" />
            <div className="h-5 w-32 shimmer bg-slate-800 rounded-lg" />
          </div>
        </div>
      </div>
      {/* Stats skeleton */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="glass-light rounded-xl p-4 space-y-2">
            <div className="h-3 w-16 shimmer bg-slate-800 rounded" />
            <div className="h-5 w-20 shimmer bg-slate-800 rounded" />
          </div>
        ))}
      </div>
      {/* Gauges skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="glass rounded-2xl p-8 flex flex-col items-center space-y-4">
            <div className="h-5 w-24 shimmer bg-slate-800 rounded-lg" />
            <div className="w-36 h-36 shimmer bg-slate-800 rounded-full" />
            <div className="h-4 w-full shimmer bg-slate-800 rounded-lg" />
            <div className="h-4 w-3/4 shimmer bg-slate-800 rounded-lg" />
          </div>
        ))}
      </div>
    </div>
  );
}

function StatBox({ icon: Icon, label, value, sub, positive }) {
  return (
    <div className="glass-light rounded-xl p-4 card-hover">
      <div className="flex items-center gap-1.5 mb-1.5">
        <Icon className="w-3.5 h-3.5 text-slate-500" />
        <span className="text-[11px] text-slate-500 uppercase tracking-wide font-medium">{label}</span>
      </div>
      <p className={`text-sm font-bold ${positive !== undefined ? (positive ? 'text-emerald-400' : 'text-red-400') : 'text-white'}`}>
        {value}
      </p>
      {sub && <p className="text-[10px] text-slate-600 mt-0.5">{sub}</p>}
    </div>
  );
}

// ══════════════════════════════════════════════════
//  MAIN DASHBOARD
// ══════════════════════════════════════════════════

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [assetName, setAssetName] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [reports, setReports] = useState([]);
  const [pdfLoading, setPdfLoading] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await authAPI.getCurrentUser();
        setUser(userData);
      } catch (err) {
        navigate('/login');
      }
    };
    fetchUser();
    fetchReports();
  }, [navigate]);

  const fetchReports = async () => {
    try {
      const data = await analysisAPI.getReports();
      setReports(data.reports || []);
    } catch (err) {
      console.error('Error fetching reports:', err);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!assetName.trim()) return;
    setError('');
    setLoading(true);
    setAnalysis(null);
    try {
      const result = await analysisAPI.analyzeAsset(assetName);
      if (!result.asset_found) {
        setError(result.message || 'Asset not found in CoinGecko. Try another name or symbol.');
      } else {
        setAnalysis(result);
        fetchReports();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error analyzing asset. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    if (!analysis?.report_id) return;
    setPdfLoading(true);
    try {
      await analysisAPI.generatePDF(analysis.report_id);
    } catch (err) {
      console.error('PDF generation error:', err);
    } finally {
      setPdfLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    navigate('/login');
  };

  const md = analysis?.market_data;
  const macro = analysis?.macro_data;
  const factors = analysis?.factor_breakdown;

  return (
    <div className="min-h-screen bg-[#06060b]">
      {/* ════════════════════════════════════════
           HEADER
         ════════════════════════════════════════ */}
      <header className="sticky top-0 z-50 glass border-b border-white/[0.04]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <Activity className="w-4.5 h-4.5 text-white" />
              </div>
              <h1 className="text-lg font-bold gradient-text tracking-tight">STRATIFY AI</h1>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-slate-600 hidden sm:block font-mono">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-white/5 transition-all text-xs font-medium"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ════════════════════════════════════════
           MAIN CONTENT
         ════════════════════════════════════════ */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

        {/* ── Search Section ───────────────────── */}
        <div className="mb-10">
          <div className="text-center mb-6">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2 tracking-tight">
              Analyze Any Cryptocurrency
            </h2>
            <p className="text-slate-500 text-sm max-w-md mx-auto">
              Multi-factor macro analysis powered by local AI — enter a name or symbol to begin
            </p>
          </div>

          <form onSubmit={handleAnalyze} className="max-w-2xl mx-auto">
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-600/40 via-purple-600/40 to-cyan-600/40 rounded-2xl opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 transition-opacity duration-500 blur-sm" />
              <div className="relative flex items-center gap-2 bg-[#0c111d] border border-slate-800/80 rounded-2xl p-2 transition-all group-focus-within:border-blue-500/30">
                <Search className="w-5 h-5 text-slate-600 ml-3 flex-shrink-0" />
                <input
                  type="text"
                  value={assetName}
                  onChange={(e) => setAssetName(e.target.value)}
                  placeholder="Search cryptocurrency... (e.g., Bitcoin, Ethereum, Solana)"
                  className="flex-1 bg-transparent text-white placeholder-slate-600 focus:outline-none py-2.5 px-2 text-sm"
                  required
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold rounded-xl transition-all disabled:opacity-50 flex items-center gap-2 shadow-lg shadow-blue-600/20 text-sm whitespace-nowrap"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      Analyze
                      <ChevronRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* ── Error ────────────────────────────── */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8 flex items-center gap-3 bg-red-500/8 border border-red-500/15 text-red-400 px-5 py-4 rounded-xl animate-fade-in">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* ── Loading ──────────────────────────── */}
        {loading && <LoadingState />}

        {/* ═══════════════════════════════════════
             ANALYSIS RESULTS
           ═══════════════════════════════════════ */}
        {analysis && (
          <div className="space-y-6">

            {/* ── Coin Profile Header ──────────── */}
            <div className="glass rounded-2xl p-6 sm:p-8 opacity-0 animate-fade-in-up" style={{ animationFillMode: 'forwards' }}>
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-5">
                <div className="flex items-center gap-5">
                  {analysis.image ? (
                    <img
                      src={analysis.image}
                      alt={analysis.asset_name}
                      className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl shadow-xl shadow-black/30 ring-2 ring-white/5"
                    />
                  ) : (
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                      <DollarSign className="w-8 h-8 text-blue-400" />
                    </div>
                  )}
                  <div>
                    <div className="flex items-center gap-3 flex-wrap">
                      <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">{analysis.asset_name}</h2>
                      <span className="px-2.5 py-0.5 rounded-lg bg-white/5 border border-white/10 text-slate-400 text-xs font-mono tracking-wider">
                        {analysis.symbol}
                      </span>
                    </div>
                    {md && (
                      <div className="flex items-center gap-4 mt-2 flex-wrap">
                        <span className="text-2xl font-bold text-white">{formatCurrency(md.current_price)}</span>
                        <span className={`inline-flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-lg ${
                          md.price_change_24h >= 0
                            ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/15'
                            : 'text-red-400 bg-red-500/10 border border-red-500/15'
                        }`}>
                          {md.price_change_24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                          {formatPercent(md.price_change_24h)}
                        </span>
                        {md.market_cap_rank && (
                          <span className="text-slate-600 text-xs flex items-center gap-1 font-mono">
                            <Hash className="w-3 h-3" />Rank {md.market_cap_rank}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                  <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border ${
                    analysis.confidence_level === 'High'
                      ? 'border-emerald-500/20 bg-emerald-500/8 text-emerald-400'
                      : analysis.confidence_level === 'Medium'
                      ? 'border-yellow-500/20 bg-yellow-500/8 text-yellow-400'
                      : 'border-red-500/20 bg-red-500/8 text-red-400'
                  }`}>
                    <Shield className="w-3 h-3" />
                    {analysis.confidence_level} Confidence
                  </span>
                  <span className="text-slate-700 text-xs font-mono">
                    {analysis.macro_events_analyzed} events
                  </span>
                </div>
              </div>

              {analysis.description && (
                <p className="text-slate-500 text-sm mt-5 leading-relaxed line-clamp-2 border-t border-white/[0.04] pt-4">
                  <Info className="w-3.5 h-3.5 inline mr-1.5 text-slate-600" />
                  {analysis.description}
                </p>
              )}
            </div>

            {/* ── Market Stats Grid ────────────── */}
            {md && (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 opacity-0 animate-fade-in-up stagger-1" style={{ animationFillMode: 'forwards' }}>
                <StatBox icon={DollarSign} label="Market Cap" value={formatCurrency(md.market_cap)} />
                <StatBox icon={BarChart3} label="24h Volume" value={formatCurrency(md.total_volume)} />
                <StatBox icon={TrendingUp} label="24h High" value={formatCurrency(md.high_24h)} />
                <StatBox icon={TrendingDown} label="24h Low" value={formatCurrency(md.low_24h)} />
                <StatBox icon={Target} label="All-Time High" value={formatCurrency(md.ath)} sub={formatPercent(md.ath_change_percentage)} />
                <StatBox icon={Layers} label="Circ. Supply" value={formatSupply(md.circulating_supply)} sub={md.total_supply ? `/ ${formatSupply(md.total_supply)}` : undefined} />
              </div>
            )}

            {/* ── Price Performance ────────────── */}
            {md && (
              <div className="grid grid-cols-3 gap-3 opacity-0 animate-fade-in-up stagger-1" style={{ animationFillMode: 'forwards' }}>
                {[
                  { label: '24 Hours', value: md.price_change_24h },
                  { label: '7 Days', value: md.price_change_7d },
                  { label: '30 Days', value: md.price_change_30d },
                ].map((item, i) => (
                  <div key={i} className={`glass-light rounded-xl p-4 text-center card-hover ${
                    item.value >= 0 ? 'border-emerald-500/10' : 'border-red-500/10'
                  }`}>
                    <span className="text-[11px] text-slate-500 block mb-1.5 uppercase tracking-wide font-medium">{item.label}</span>
                    <div className="flex items-center justify-center gap-1.5">
                      {item.value >= 0
                        ? <ArrowUpRight className="w-4 h-4 text-emerald-400" />
                        : <ArrowDownRight className="w-4 h-4 text-red-400" />
                      }
                      <span className={`text-xl font-bold ${item.value >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {formatPercent(item.value)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* ── Probability Gauges ───────────── */}
            <div className="opacity-0 animate-fade-in-up stagger-2" style={{ animationFillMode: 'forwards' }}>
              <SectionHeader icon={Target} title="Probability Analysis" subtitle="AI-powered outlook across time horizons" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <ProbabilityCard
                  title="Short-Term" subtitle="0 – 4 weeks"
                  probability={analysis.probabilities.short_term}
                  narrative={analysis.narratives.short}
                />
                <ProbabilityCard
                  title="Medium-Term" subtitle="1 – 6 months"
                  probability={analysis.probabilities.medium_term}
                  narrative={analysis.narratives.medium}
                />
                <ProbabilityCard
                  title="Long-Term" subtitle="6 – 24 months"
                  probability={analysis.probabilities.long_term}
                  narrative={analysis.narratives.long}
                />
              </div>
            </div>

            {/* ── Two-Column: Factors + Macro ──── */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* Factor Breakdown */}
              {factors && (
                <div className="glass rounded-2xl p-6 opacity-0 animate-fade-in-up stagger-3" style={{ animationFillMode: 'forwards' }}>
                  <SectionHeader icon={Zap} title="Influence Factors" subtitle="What drives this asset's sensitivity" />
                  <div className="space-y-4">
                    {[
                      { key: 'volatility', label: 'Volatility Level', color: 'from-orange-500 to-amber-500', desc: 'Price swing magnitude' },
                      { key: 'liquidity', label: 'Liquidity Score', color: 'from-blue-500 to-cyan-500', desc: 'Market depth & volume' },
                      { key: 'regulation_exposure', label: 'Regulation Exposure', color: 'from-purple-500 to-pink-500', desc: 'Regulatory sensitivity' },
                      { key: 'interest_rate_impact', label: 'Interest Rate Impact', color: 'from-yellow-500 to-orange-500', desc: 'Rate change sensitivity' },
                      { key: 'geopolitical_risk', label: 'Geopolitical Risk', color: 'from-red-500 to-rose-500', desc: 'Global event exposure' },
                    ].map(({ key, label, color, desc }) => {
                      const val = factors[key] || 0;
                      return (
                        <div key={key} className="group">
                          <div className="flex justify-between items-center mb-1.5">
                            <div>
                              <span className="text-sm text-slate-300 font-medium">{label}</span>
                              <span className="text-[10px] text-slate-600 ml-2 hidden sm:inline">{desc}</span>
                            </div>
                            <span className="text-xs font-mono text-slate-500 tabular-nums">{(val * 100).toFixed(0)}%</span>
                          </div>
                          <div className="w-full bg-slate-800/60 rounded-full h-2">
                            <div
                              className={`bg-gradient-to-r ${color} h-2 rounded-full transition-all duration-1000 ease-out`}
                              style={{ width: `${Math.max(val * 100, 2)}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Macro Indicators */}
              <div className="glass rounded-2xl p-6 opacity-0 animate-fade-in-up stagger-3" style={{ animationFillMode: 'forwards' }}>
                <SectionHeader icon={Globe} title="Macro Environment" subtitle="Economic indicators influencing the analysis" />
                <div className="space-y-4">
                  {macro?.interest_rate && (
                    <div className="bg-slate-800/30 rounded-xl p-5 border border-white/[0.04] card-hover">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                            <BarChart3 className="w-4 h-4 text-blue-400" />
                          </div>
                          <span className="text-sm font-medium text-slate-300">Federal Funds Rate</span>
                        </div>
                        <span className={`text-[11px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                          macro.interest_rate.trend === 'rising'
                            ? 'bg-red-500/10 text-red-400 border border-red-500/15'
                            : macro.interest_rate.trend === 'falling'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/15'
                            : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/15'
                        }`}>
                          {macro.interest_rate.trend}
                        </span>
                      </div>
                      <p className="text-3xl font-bold text-white">{macro.interest_rate.current_rate}%</p>
                      <p className="text-[11px] text-slate-600 mt-1">
                        Previous: {macro.interest_rate.previous_rate}% &bull; Data: {macro.interest_rate.date}
                      </p>
                    </div>
                  )}

                  {macro?.inflation && (
                    <div className="bg-slate-800/30 rounded-xl p-5 border border-white/[0.04] card-hover">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
                            <TrendingUp className="w-4 h-4 text-orange-400" />
                          </div>
                          <span className="text-sm font-medium text-slate-300">Inflation (CPI YoY)</span>
                        </div>
                        <span className={`text-[11px] px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider ${
                          macro.inflation.yoy_inflation > 3
                            ? 'bg-red-500/10 text-red-400 border border-red-500/15'
                            : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/15'
                        }`}>
                          {macro.inflation.yoy_inflation > 3 ? 'elevated' : 'moderate'}
                        </span>
                      </div>
                      <p className="text-3xl font-bold text-white">{macro.inflation.yoy_inflation}%</p>
                      <p className="text-[11px] text-slate-600 mt-1">
                        Current CPI: {macro.inflation.current_cpi} &bull; Data: {macro.inflation.date}
                      </p>
                    </div>
                  )}

                  {!macro?.interest_rate && !macro?.inflation && (
                    <div className="text-center py-8">
                      <Globe className="w-8 h-8 text-slate-700 mx-auto mb-2" />
                      <p className="text-slate-600 text-sm">Macro data currently unavailable</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* ── News Intelligence ────────────── */}
            {analysis.news_sources?.length > 0 && (
              <div className="opacity-0 animate-fade-in-up stagger-4" style={{ animationFillMode: 'forwards' }}>
                <SectionHeader icon={Newspaper} title="News Intelligence" subtitle="Sources that influenced the analysis scoring" />
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {analysis.news_sources.map((news, i) => {
                    const badge = getSentimentBadge(news.sentiment);
                    return (
                      <a
                        key={i}
                        href={news.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="glass-light rounded-xl p-5 card-hover block group"
                      >
                        <div className="flex items-start justify-between gap-3 mb-3">
                          <span className={`text-[11px] px-2.5 py-0.5 rounded-full border font-semibold ${badge.cls}`}>
                            {badge.text} ({(news.sentiment * 100).toFixed(0)}%)
                          </span>
                          <ExternalLink className="w-3.5 h-3.5 text-slate-700 group-hover:text-blue-400 transition flex-shrink-0 mt-0.5" />
                        </div>
                        <h4 className="text-sm font-medium text-white line-clamp-2 mb-3 group-hover:text-blue-300 transition leading-snug">
                          {news.title}
                        </h4>
                        <div className="flex items-center gap-2 text-[11px] text-slate-600">
                          <Newspaper className="w-3 h-3" />
                          <span className="font-medium text-slate-500">{news.source}</span>
                          {news.published_at && (
                            <>
                              <span>&bull;</span>
                              <Clock className="w-3 h-3" />
                              <span>{new Date(news.published_at).toLocaleDateString()}</span>
                            </>
                          )}
                        </div>
                      </a>
                    );
                  })}
                </div>
              </div>
            )}

            {/* ── Most Likely Scenario ─────────── */}
            <div className="glass rounded-2xl p-6 sm:p-8 opacity-0 animate-fade-in-up stagger-5" style={{ animationFillMode: 'forwards' }}>
              <SectionHeader icon={Target} title="Most Likely Scenario" subtitle="AI-generated outlook synthesis" />
              <div className="bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-xl p-5 border border-blue-500/10">
                <p className="text-slate-300 leading-relaxed text-sm">{analysis.most_likely_scenario}</p>
              </div>
            </div>

            {/* ── Download PDF ─────────────────── */}
            <div className="flex justify-center opacity-0 animate-fade-in-up stagger-5" style={{ animationFillMode: 'forwards' }}>
              <button
                onClick={handleGeneratePDF}
                disabled={pdfLoading}
                className="group flex items-center gap-3 px-10 py-4 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-semibold rounded-xl transition-all shadow-lg shadow-emerald-600/20 hover:shadow-emerald-500/30 disabled:opacity-50 text-sm"
              >
                {pdfLoading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <Download className="w-5 h-5 group-hover:animate-bounce" />
                )}
                {pdfLoading ? 'Generating Report...' : 'Download Full PDF Report'}
              </button>
            </div>
          </div>
        )}

        {/* ═══════════════════════════════════════
             ANALYSIS HISTORY
           ═══════════════════════════════════════ */}
        {reports.length > 0 && (
          <div className={`${analysis ? 'mt-14' : 'mt-4'}`}>
            <SectionHeader icon={FileText} title="Analysis History" subtitle="Your recent cryptocurrency analyses" />
            <div className="space-y-2">
              {reports.slice(0, 8).map((report) => (
                <div
                  key={report.id}
                  className="glass-light rounded-xl p-4 flex items-center justify-between card-hover"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/10 flex items-center justify-center flex-shrink-0">
                      <Activity className="w-4 h-4 text-blue-400" />
                    </div>
                    <div>
                      <p className="text-white font-semibold text-sm">{report.token_name}</p>
                      <p className="text-[11px] text-slate-600 flex items-center gap-1 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {new Date(report.created_at).toLocaleDateString('en-US', {
                          month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-5">
                    {[
                      { label: 'Short', value: report.short_term_prob },
                      { label: 'Medium', value: report.medium_term_prob },
                      { label: 'Long', value: report.long_term_prob },
                    ].map(({ label, value }) => (
                      <div key={label} className="text-center min-w-[48px]">
                        <p className="text-[10px] text-slate-600 uppercase tracking-wider font-medium">{label}</p>
                        <p className={`text-sm font-bold tabular-nums ${
                          value > 0.6 ? 'text-emerald-400' : value > 0.4 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {(value * 100).toFixed(0)}%
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Empty State ──────────────────────── */}
        {!analysis && !loading && !error && reports.length === 0 && (
          <div className="text-center py-24">
            <div className="w-20 h-20 rounded-2xl bg-slate-800/30 border border-white/[0.04] flex items-center justify-center mx-auto mb-5">
              <Search className="w-9 h-9 text-slate-700" />
            </div>
            <h3 className="text-lg font-medium text-slate-400 mb-2">No analyses yet</h3>
            <p className="text-slate-600 text-sm max-w-sm mx-auto">
              Search for any cryptocurrency above to get a comprehensive multi-factor macro analysis
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
