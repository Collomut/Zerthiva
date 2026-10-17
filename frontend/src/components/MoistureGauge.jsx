import React from 'react';

export default function MoistureGauge({ moisture = 30.0, minRefill = 22.0, fieldCapacity = 38.0 }) {
  const clamped = Math.min(Math.max(moisture, 0), 100);

  let statusText = 'Optimal Moisture';
  let statusColor = 'text-emerald-400';
  let barColor = 'bg-emerald-500';

  if (moisture < minRefill) {
    statusText = 'Soil Dry — Irrigate';
    statusColor = 'text-amber-400';
    barColor = 'bg-amber-500';
  } else if (moisture > fieldCapacity) {
    statusText = 'Waterlogged — Pause';
    statusColor = 'text-rose-400';
    barColor = 'bg-rose-500';
  }

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl flex flex-col justify-between">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-sm font-bold text-white">Soil Moisture Level</h4>
          <p className="text-xs text-slate-400">Volumetric Water Content (VWC %)</p>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800 border border-slate-700 ${statusColor}`}>
          {statusText}
        </span>
      </div>

      <div className="my-6">
        <div className="flex items-baseline justify-between mb-2">
          <span className="text-4xl font-extrabold text-white">{moisture.toFixed(1)}%</span>
          <span className="text-xs text-slate-400">Target: {minRefill}% – {fieldCapacity}%</span>
        </div>

        {/* Progress Track */}
        <div className="relative w-full h-3 bg-slate-800 rounded-full overflow-hidden">
          {/* Target Zone Highlight */}
          <div
            className="absolute top-0 bottom-0 bg-emerald-500/20 border-x border-emerald-500/40"
            style={{
              left: `${minRefill}%`,
              width: `${fieldCapacity - minRefill}%`
            }}
          />
          {/* Active Level */}
          <div
            className={`h-full rounded-full transition-all duration-500 ${barColor}`}
            style={{ width: `${clamped}%` }}
          />
        </div>

        {/* Threshold Markers */}
        <div className="flex justify-between text-[10px] text-slate-500 mt-1.5 font-mono">
          <span>0% (Dry)</span>
          <span style={{ marginLeft: `${minRefill - 10}%` }}>Refill ({minRefill}%)</span>
          <span>Capacity ({fieldCapacity}%)</span>
          <span>100% (Sat)</span>
        </div>
      </div>

      <div className="text-xs text-slate-400 bg-slate-800/40 rounded-xl p-3 border border-slate-800 flex items-center justify-between">
        <span>Capacitive Sensor Status</span>
        <span className="text-emerald-400 font-medium">Calibrated (12-bit ADC)</span>
      </div>
    </div>
  );
}
