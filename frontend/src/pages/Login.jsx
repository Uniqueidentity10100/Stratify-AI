import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import { Shield, TrendingUp, Brain, ArrowRight, Eye, EyeOff, Activity, Zap, Globe } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        await authAPI.login(email, password);
      } else {
        await authAPI.register(email, password);
        await authAPI.login(email, password);
      }
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: TrendingUp, label: 'Real-time Macro Analysis', desc: 'FRED economic data & live news intelligence' },
    { icon: Brain, label: 'AI-Powered Narratives', desc: 'Local Ollama LLM generates plain-English insights' },
    { icon: Shield, label: 'Multi-Factor Scoring', desc: 'Structured influence engine across time horizons' },
    { icon: Globe, label: 'Global Intelligence', desc: 'Geopolitical, regulatory & market sentiment fusion' },
  ];

  const stats = [
    { value: '3', label: 'Time Horizons' },
    { value: '5+', label: 'Data Sources' },
    { value: 'AI', label: 'Narratives' },
  ];

  return (
    <div className="min-h-screen bg-[#06060b] flex items-center justify-center p-4 relative overflow-hidden">
      {/* ── Animated Background ──────────────── */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-blue-600/8 rounded-full blur-[120px] animate-float" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-600/8 rounded-full blur-[120px] animate-float" style={{ animationDelay: '2s' }} />
        <div className="absolute top-[30%] right-[20%] w-[400px] h-[400px] bg-cyan-600/5 rounded-full blur-[100px] animate-float" style={{ animationDelay: '4s' }} />
        {/* Grid overlay */}
        <div className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}
        />
      </div>

      <div className="relative z-10 w-full max-w-6xl flex flex-col lg:flex-row items-center gap-12 lg:gap-20">
        {/* ── Left: Brand & Features ──────────── */}
        <div className="hidden lg:block flex-1 space-y-10">
          <div className="opacity-0 animate-fade-in-up" style={{ animationFillMode: 'forwards' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-black tracking-tight">
                  <span className="gradient-text">STRATIFY</span>
                  <span className="text-white"> AI</span>
                </h1>
              </div>
            </div>
            <p className="text-slate-400 text-lg leading-relaxed max-w-md">
              Decode how macroeconomic forces, regulatory actions, and global events
              shape cryptocurrency trajectories across multiple time horizons.
            </p>
          </div>

          {/* Feature Cards */}
          <div className="space-y-3">
            {features.map((f, i) => (
              <div
                key={i}
                className="flex items-center gap-4 p-4 rounded-xl glass-light card-hover opacity-0 animate-fade-in-up"
                style={{ animationDelay: `${0.2 + i * 0.1}s`, animationFillMode: 'forwards' }}
              >
                <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-blue-500/15 to-purple-500/15 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <f.icon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <p className="text-white font-semibold text-sm">{f.label}</p>
                  <p className="text-slate-500 text-xs mt-0.5">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Stats Row */}
          <div className="flex items-center gap-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.7s', animationFillMode: 'forwards' }}>
            {stats.map((s, i) => (
              <div key={i} className="text-center">
                <p className="text-2xl font-bold gradient-text">{s.value}</p>
                <p className="text-xs text-slate-600 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        </div>

        {/* ── Right: Auth Form ────────────────── */}
        <div className="w-full max-w-md opacity-0 animate-fade-in-up" style={{ animationDelay: '0.1s', animationFillMode: 'forwards' }}>
          {/* Mobile Brand */}
          <div className="lg:hidden text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-3xl font-black">
                <span className="gradient-text">STRATIFY</span>
                <span className="text-white"> AI</span>
              </h1>
            </div>
            <p className="text-slate-500 text-sm">Multi-Factor Influence Intelligence</p>
          </div>

          {/* Form Card */}
          <div className="glass rounded-2xl p-8 shadow-2xl shadow-black/20">
            {/* Toggle */}
            <div className="flex gap-1 p-1 bg-slate-900/80 rounded-xl mb-7">
              <button
                onClick={() => setIsLogin(true)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-300 ${
                  isLogin
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-600/25'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all duration-300 ${
                  !isLogin
                    ? 'bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-lg shadow-blue-600/25'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Create Account
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all text-sm"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/60 border border-slate-700/50 rounded-xl text-white placeholder-slate-600 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all pr-12 text-sm"
                    placeholder="••••••••"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
                  <Zap className="w-4 h-4 flex-shrink-0" />
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 text-white font-semibold py-3.5 px-4 rounded-xl transition-all duration-300 disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-600/25 hover:shadow-blue-500/40 text-sm"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    {isLogin ? 'Sign In to Dashboard' : 'Create Account'}
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>
          </div>

          <p className="text-center text-slate-700 text-xs mt-6">
            Powered by Ollama AI & Real-time Macro Intelligence
          </p>
        </div>
      </div>
    </div>
  );
}
