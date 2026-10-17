import React, { useState } from 'react';
import { calculateLeaching } from '../services/api';

export default function LeachingModal({ isOpen, onClose, defaultCrop = 'tomato', defaultEc = 2.8 }) {
  const [crop, setCrop] = useState(defaultCrop);
  const [soilEc, setSoilEc] = useState(defaultEc);
  const [waterEc, setWaterEc] = useState(0.6);
  const [result, setResult] = useState(null);

  if (!isOpen) return null;

  const handleCompute = async (e) => {
    e.preventDefault();
    const res = await calculateLeaching(crop, soilEc, waterEc);
    setResult(res);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-3xl p-6 shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-white">FAO-56 Leaching Requirement Calculator</h3>
            <p className="text-xs text-slate-400">Salt leaching fraction calculation based on FAO standard protocols</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold transition-colors"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleCompute} className="space-y-4 my-5">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Crop Profile</label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="maize">Maize (Corn) — Safe Threshold: 1.7 dS/m</option>
              <option value="tomato">Tomato — Safe Threshold: 2.5 dS/m</option>
              <option value="rice">Rice (Paddy) — Safe Threshold: 3.0 dS/m</option>
              <option value="wheat">Wheat — Safe Threshold: 6.0 dS/m</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Current Soil EC (dS/m)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={soilEc}
                onChange={(e) => setSoilEc(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Water Source EC (dS/m)</label>
              <input
                type="number"
                step="0.05"
                min="0.1"
                value={waterEc}
                onChange={(e) => setWaterEc(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-colors shadow-lg shadow-emerald-900/30"
          >
            Compute Leaching Requirement
          </button>
        </form>

        {result && (
          <div className="bg-slate-800/60 p-4 rounded-2xl border border-emerald-500/30 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Standard Formula:</span>
              <span className="font-mono text-emerald-300">{result.formula_reference}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-white">Leaching Fraction (LR):</span>
              <span className="text-xl font-extrabold text-emerald-400">{result.leaching_requirement}</span>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-slate-700/60">
              <span className="text-xs text-slate-300">Extra Water Recommended:</span>
              <span className="text-base font-bold text-amber-400">+{result.extra_water_percent}% over normal irrigation</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
