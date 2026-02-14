import React from 'react';

export default function ProbabilityCard({ title, subtitle, probability, narrative }) {
  const percentage = Math.round(probability * 100);

  const getColors = (p) => {
    if (p > 0.7) return { stroke: '#22c55e', text: 'text-emerald-400', label: 'Strongly Positive', bg: 'from-emerald-500/10 to-emerald-500/5', border: 'border-emerald-500/15' };
    if (p > 0.6) return { stroke: '#4ade80', text: 'text-green-400', label: 'Moderately Positive', bg: 'from-green-500/10 to-green-500/5', border: 'border-green-500/15' };
    if (p > 0.4) return { stroke: '#eab308', text: 'text-yellow-400', label: 'Neutral', bg: 'from-yellow-500/10 to-yellow-500/5', border: 'border-yellow-500/15' };
    if (p > 0.3) return { stroke: '#f97316', text: 'text-orange-400', label: 'Moderately Negative', bg: 'from-orange-500/10 to-orange-500/5', border: 'border-orange-500/15' };
    return { stroke: '#ef4444', text: 'text-red-400', label: 'Strongly Negative', bg: 'from-red-500/10 to-red-500/5', border: 'border-red-500/15' };
  };

  const c = getColors(probability);

  // SVG Gauge
  const size = 150;
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - probability * circumference;

  return (
    <div className={`glass rounded-2xl p-6 card-hover bg-gradient-to-b ${c.bg} ${c.border}`}>
      {/* Header */}
      <div className="text-center mb-5">
        <h3 className="text-base font-semibold text-white">{title}</h3>
        <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>
      </div>

      {/* Animated SVG Gauge */}
      <div className="flex justify-center mb-5">
        <div className="relative">
          <svg width={size} height={size} className="transform -rotate-90">
            {/* Background track */}
            <circle
              cx={size / 2} cy={size / 2} r={radius}
              fill="none"
              stroke="rgba(51,65,85,0.25)"
              strokeWidth={strokeWidth}
            />
            {/* Glow filter */}
            <defs>
              <filter id={`glow-${title.replace(/\s/g, '')}`} x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="4" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {/* Value arc */}
            <circle
              cx={size / 2} cy={size / 2} r={radius}
              fill="none"
              stroke={c.stroke}
              strokeWidth={strokeWidth}
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className="gauge-animate"
              filter={`url(#glow-${title.replace(/\s/g, '')})`}
            />
          </svg>
          {/* Center value */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-4xl font-bold ${c.text} tracking-tight`}>{percentage}</span>
            <span className="text-xs text-slate-500 font-medium">percent</span>
          </div>
        </div>
      </div>

      {/* Outlook Badge */}
      <div className="text-center mb-4">
        <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full ${c.text} bg-white/5 border ${c.border}`}>
          {c.label}
        </span>
      </div>

      {/* Narrative */}
      <p className="text-sm text-slate-400 leading-relaxed text-center">{narrative}</p>
    </div>
  );
}
