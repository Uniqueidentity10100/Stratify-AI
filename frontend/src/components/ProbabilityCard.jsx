/**
 * Probability Card Component
 * Displays probability score with visual indicator
 */
import React from 'react';

export default function ProbabilityCard({ title, subtitle, probability, narrative }) {
  // Calculate percentage
  const percentage = (probability * 100).toFixed(0);

  // Determine color based on probability
  const getColor = (prob) => {
    if (prob > 0.7) return { bg: 'bg-green-500', text: 'text-green-400', border: 'border-green-500' };
    if (prob > 0.6) return { bg: 'bg-green-400', text: 'text-green-300', border: 'border-green-400' };
    if (prob > 0.4) return { bg: 'bg-yellow-500', text: 'text-yellow-400', border: 'border-yellow-500' };
    if (prob > 0.3) return { bg: 'bg-orange-500', text: 'text-orange-400', border: 'border-orange-500' };
    return { bg: 'bg-red-500', text: 'text-red-400', border: 'border-red-500' };
  };

  const colors = getColor(probability);

  const getOutlook = (prob) => {
    if (prob > 0.7) return 'Strongly Positive';
    if (prob > 0.6) return 'Moderately Positive';
    if (prob > 0.4) return 'Neutral';
    if (prob > 0.3) return 'Moderately Negative';
    return 'Strongly Negative';
  };

  return (
    <div className={`bg-slate-800 rounded-lg shadow-xl p-6 border-l-4 ${colors.border}`}>
      {/* Header */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <p className="text-sm text-slate-400">{subtitle}</p>
      </div>

      {/* Probability Score */}
      <div className="mb-4">
        <div className="flex items-baseline gap-2">
          <span className={`text-5xl font-bold ${colors.text}`}>
            {percentage}
          </span>
          <span className="text-2xl text-slate-500">%</span>
        </div>
        <p className={`text-sm font-medium mt-1 ${colors.text}`}>
          {getOutlook(probability)}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-700 rounded-full h-2 mb-4">
        <div
          className={`${colors.bg} h-2 rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Narrative */}
      <div className="text-sm text-slate-300 leading-relaxed">
        {narrative}
      </div>
    </div>
  );
}
