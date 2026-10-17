import React from 'react';

export default function AlertBanner({ status = 'OPTIMAL', message, onOpenCalculator }) {
  if (status === 'OPTIMAL') {
    return (
      <div className="bg-emerald-950/30 border border-emerald-500/30 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-lg">
            ✓
          </div>
          <div>
            <h4 className="text-sm font-bold text-emerald-200">Soil Equilibrium Stable</h4>
            <p className="text-xs text-emerald-400/80">{message || 'All root-zone salinity and moisture metrics are within safe agronomic parameters.'}</p>
          </div>
        </div>
        <button
          onClick={onOpenCalculator}
          className="text-xs px-3.5 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 font-medium transition-colors"
        >
          FAO-56 Calculator
        </button>
      </div>
    );
  }

  if (status === 'IRRIGATE') {
    return (
      <div className="bg-amber-950/30 border border-amber-500/30 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-lg">
            💧
          </div>
          <div>
            <h4 className="text-sm font-bold text-amber-200">Irrigation Cycle Recommended</h4>
            <p className="text-xs text-amber-400/80">{message || 'Soil moisture is below refill point. Salinity is safe for standard irrigation.'}</p>
          </div>
        </div>
        <button
          onClick={onOpenCalculator}
          className="text-xs px-3.5 py-1.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 font-medium transition-colors"
        >
          View Irrigation Specs
        </button>
      </div>
    );
  }

  // Critical Salinity State
  return (
    <div className="bg-rose-950/40 border border-rose-500/50 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 backdrop-blur-md shadow-lg shadow-rose-950/20 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-lg">
          ⚠️
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-extrabold text-rose-200">CRITICAL SALINITY DETECTED — FLUSH REQUIRED</h4>
            <span className="text-[10px] px-2 py-0.5 rounded bg-rose-500/30 text-rose-200 border border-rose-500/40 font-bold uppercase">
              SMS Dispatched
            </span>
          </div>
          <p className="text-xs text-rose-300/90 mt-0.5">{message || 'Electrical conductivity exceeds crop tolerance. Hold fertilizer and initiate leaching flush immediately.'}</p>
        </div>
      </div>
      <button
        onClick={onOpenCalculator}
        className="text-xs px-3.5 py-1.5 rounded-xl bg-rose-500 hover:bg-rose-600 text-white font-bold transition-colors shadow-md"
      >
        Compute Flush Volume
      </button>
    </div>
  );
}
