import React from 'react';

export default function StatCard({ title, value, unit, subtitle, status = 'neutral', icon }) {
  const statusStyles = {
    optimal: 'border-emerald-500/40 bg-emerald-950/20 text-emerald-400',
    warning: 'border-amber-500/40 bg-amber-950/20 text-amber-400',
    danger: 'border-rose-500/40 bg-rose-950/20 text-rose-400',
    neutral: 'border-slate-800 bg-slate-800/50 text-slate-300'
  };

  const badgeStyles = {
    optimal: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    warning: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    danger: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
    neutral: 'bg-slate-700/50 text-slate-300 border-slate-600'
  };

  return (
    <div className={`p-5 rounded-2xl border backdrop-blur-sm transition-all duration-300 hover:border-slate-700 ${statusStyles[status] || statusStyles.neutral}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {icon && <span className="text-xl opacity-80">{icon}</span>}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-3xl font-extrabold tracking-tight text-white">{value}</span>
        {unit && <span className="text-sm font-medium text-slate-400">{unit}</span>}
      </div>
      {subtitle && (
        <div className="mt-2.5 flex items-center justify-between text-xs">
          <span className="text-slate-400">{subtitle}</span>
          <span className={`px-2 py-0.5 rounded-full border text-[11px] font-medium capitalize ${badgeStyles[status] || badgeStyles.neutral}`}>
            {status}
          </span>
        </div>
      )}
    </div>
  );
}
