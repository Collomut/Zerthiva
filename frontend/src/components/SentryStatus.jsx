import React from 'react';

export default function SentryStatus({ status = 'OPTIMAL', color = 'GREEN', allowFertilizer = true, action = 'NONE' }) {
  const configs = {
    GREEN: {
      bg: 'bg-emerald-500',
      ring: 'ring-emerald-500/30',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      label: 'Optimal Field Balance',
      meaning: 'Salinity and moisture are healthy. Green light visible to farmer.'
    },
    YELLOW: {
      bg: 'bg-amber-500',
      ring: 'ring-amber-500/30',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      label: 'Irrigation Action Required',
      meaning: 'Soil is dry or near threshold. Yellow light advises farmer to water.'
    },
    RED: {
      bg: 'bg-rose-500',
      ring: 'ring-rose-500/30',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      label: 'Critical Salinity Warning',
      meaning: 'High salt detected. Red light commands farmer to stop fertilizer & flush.'
    },
    BLUE: {
      bg: 'bg-sky-500',
      ring: 'ring-sky-500/30',
      text: 'text-sky-400',
      border: 'border-sky-500/30',
      label: 'Modem Uplink Active',
      meaning: 'Node is transmitting telemetry packet via GSM/GPRS.'
    }
  };

  const current = configs[color] || configs.GREEN;

  return (
    <div className={`p-6 rounded-2xl border ${current.border} bg-slate-900/60 backdrop-blur-md shadow-xl flex flex-col justify-between`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-bold text-white">Field Visual Sentry</h4>
          <p className="text-xs text-slate-400">Physical RGB LED Beacon State</p>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-3.5 h-3.5 rounded-full ${current.bg} animate-pulse ring-4 ${current.ring}`} />
          <span className={`text-xs font-bold uppercase tracking-wider ${current.text}`}>
            {color} PULSE
          </span>
        </div>
      </div>

      <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/60 my-2">
        <div className="text-xs font-medium text-white mb-1">{current.label}</div>
        <div className="text-xs text-slate-400 leading-relaxed">{current.meaning}</div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
        <span className="text-slate-400">Fertilizer Lockout:</span>
        <span className={`px-2 py-0.5 rounded-md font-semibold ${allowFertilizer ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'}`}>
          {allowFertilizer ? 'UNLOCKED (Safe)' : 'LOCKED (Halt Application)'}
        </span>
      </div>
    </div>
  );
}
