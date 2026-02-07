/**
 * Dashboard Page Component
 * Main interface for asset analysis
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, analysisAPI } from '../services/api';
import ProbabilityCard from '../components/ProbabilityCard';

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [assetName, setAssetName] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [reports, setReports] = useState([]);
  const [pdfLoading, setPdfLoading] = useState(false);

  // Fetch user data on mount
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
    setError('');
    setLoading(true);
    setAnalysis(null);

    try {
      const result = await analysisAPI.analyzeAsset(assetName);
      
      if (!result.asset_found) {
        setError(result.message || 'Asset not found in CoinGecko');
      } else {
        setAnalysis(result);
        fetchReports(); // Refresh reports list
      }
    } catch (err) {
      setError(
        err.response?.data?.detail || 
        'Error analyzing asset. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    if (!analysis?.report_id) return;

    setPdfLoading(true);
    try {
      const result = await analysisAPI.generatePDF(analysis.report_id);
      alert(`PDF generated: ${result.filename}`);
    } catch (err) {
      alert('Error generating PDF');
    } finally {
      setPdfLoading(false);
    }
  };

  const handleLogout = () => {
    authAPI.logout();
    navigate('/login');
  };

  const getProbabilityColor = (prob) => {
    if (prob > 0.7) return 'text-green-400';
    if (prob > 0.6) return 'text-green-300';
    if (prob > 0.4) return 'text-yellow-400';
    if (prob > 0.3) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-white">STRATIFY AI</h1>
              <p className="text-sm text-slate-400">
                {user?.email}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Analysis Input */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-6 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            Analyze Asset
          </h2>
          
          <form onSubmit={handleAnalyze} className="flex gap-4">
            <input
              type="text"
              value={assetName}
              onChange={(e) => setAssetName(e.target.value)}
              placeholder="Enter asset name (e.g., Bitcoin, Ethereum)"
              className="flex-1 px-4 py-3 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </form>

          {error && (
            <div className="mt-4 bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>

        {/* Analysis Results */}
        {analysis && (
          <div className="space-y-6">
            {/* Asset Header */}
            <div className="bg-slate-800 rounded-lg shadow-xl p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    {analysis.asset_name}
                  </h2>
                  <p className="text-slate-400">
                    {analysis.symbol}
                  </p>
                  <p className="text-sm text-slate-500 mt-2">
                    Confidence: {analysis.confidence_level} | 
                    Events Analyzed: {analysis.macro_events_analyzed}
                  </p>
                </div>
                <button
                  onClick={handleGeneratePDF}
                  disabled={pdfLoading}
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded transition disabled:opacity-50"
                >
                  {pdfLoading ? 'Generating...' : 'Download PDF'}
                </button>
              </div>
            </div>

            {/* Probability Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <ProbabilityCard
                title="Short-Term"
                subtitle="0-4 weeks"
                probability={analysis.probabilities.short_term}
                narrative={analysis.narratives.short}
              />
              <ProbabilityCard
                title="Medium-Term"
                subtitle="1-6 months"
                probability={analysis.probabilities.medium_term}
                narrative={analysis.narratives.medium}
              />
              <ProbabilityCard
                title="Long-Term"
                subtitle="6-24 months"
                probability={analysis.probabilities.long_term}
                narrative={analysis.narratives.long}
              />
            </div>

            {/* Most Likely Scenario */}
            <div className="bg-slate-800 rounded-lg shadow-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-3">
                Most Likely Scenario
              </h3>
              <p className="text-slate-300 leading-relaxed">
                {analysis.most_likely_scenario}
              </p>
            </div>
          </div>
        )}

        {/* Recent Reports */}
        {reports.length > 0 && (
          <div className="mt-8 bg-slate-800 rounded-lg shadow-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              Recent Analysis Reports
            </h2>
            <div className="space-y-3">
              {reports.slice(0, 5).map((report) => (
                <div
                  key={report.id}
                  className="bg-slate-700 rounded p-4 flex justify-between items-center"
                >
                  <div>
                    <p className="text-white font-medium">
                      {report.token_name}
                    </p>
                    <p className="text-sm text-slate-400">
                      {new Date(report.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex gap-4 text-sm">
                    <span className={getProbabilityColor(report.short_term_prob)}>
                      ST: {(report.short_term_prob * 100).toFixed(0)}%
                    </span>
                    <span className={getProbabilityColor(report.medium_term_prob)}>
                      MT: {(report.medium_term_prob * 100).toFixed(0)}%
                    </span>
                    <span className={getProbabilityColor(report.long_term_prob)}>
                      LT: {(report.long_term_prob * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
