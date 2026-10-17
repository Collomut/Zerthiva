import React from 'react';

export default function SalinityChart({ data = [], threshold = 2.5, cropName = 'Crop' }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-500 text-sm border border-slate-800 rounded-2xl bg-slate-900/50">
        No telemetry data available for chart.
      </div>
    );
  }

  // Calculate scales
  const points = [...data].reverse(); // Oldest to newest
  const values = points.map(p => p.normalized_ec_25 || p.raw_ec || 0);
  const minVal = Math.max(0, Math.min(...values, threshold) - 0.5);
  const maxVal = Math.max(...values, threshold) + 0.8;
  const range = maxVal - minVal || 1;

  const width = 600;
  const height = 220;
  const padLeft = 45;
  const padRight = 20;
  const padTop = 20;
  const padBottom = 35;

  const chartWidth = width - padLeft - padRight;
  const chartHeight = height - padTop - padBottom;

  const getX = (index) => padLeft + (index / (points.length - 1 || 1)) * chartWidth;
  const getY = (val) => padTop + chartHeight - ((val - minVal) / range) * chartHeight;

  // Build SVG polyline points
  const linePoints = points.map((p, idx) => `${getX(idx)},${getY(p.normalized_ec_25 || p.raw_ec || 0)}`).join(' ');
  const thresholdY = getY(threshold);

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <span>Soil Salinity Trend ($\text{EC}_{25}$)</span>
            <span className="text-xs font-normal px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              {cropName}
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">Electrical conductivity normalized to 25°C standard baseline (dS/m)</p>
        </div>
        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-emerald-400 inline-block"></span>
            <span className="text-slate-300">Measured EC</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 border-b-2 border-dashed border-rose-500 inline-block"></span>
            <span className="text-rose-400">FAO Safe Limit ({threshold} dS/m)</span>
          </div>
        </div>
      </div>

      <div className="relative w-full overflow-hidden">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((ratio, idx) => {
            const val = minVal + ratio * range;
            const y = padTop + chartHeight - ratio * chartHeight;
            return (
              <g key={idx}>
                <line x1={padLeft} y1={y} x2={width - padRight} y2={y} stroke="#334155" strokeDasharray="3 3" strokeOpacity="0.4" />
                <text x={padLeft - 8} y={y + 4} textAnchor="end" fill="#64748b" fontSize="10">
                  {val.toFixed(1)}
                </text>
              </g>
            );
          })}

          {/* FAO Threshold Dashed Line */}
          <line
            x1={padLeft}
            y1={thresholdY}
            x2={width - padRight}
            y2={thresholdY}
            stroke="#f43f5e"
            strokeWidth="1.5"
            strokeDasharray="5 4"
          />

          {/* Shaded Area Below Line */}
          <polygon
            points={`${padLeft},${padTop + chartHeight} ${linePoints} ${width - padRight},${padTop + chartHeight}`}
            fill="url(#ecGradient)"
            opacity="0.3"
          />

          {/* Telemetry Line */}
          <polyline
            fill="none"
            stroke="#10b981"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            points={linePoints}
          />

          {/* Active Data Points */}
          {points.map((p, idx) => {
            const val = p.normalized_ec_25 || p.raw_ec || 0;
            const isExceeded = val > threshold;
            return (
              <circle
                key={idx}
                cx={getX(idx)}
                cy={getY(val)}
                r={idx === points.length - 1 ? 4.5 : 2.5}
                fill={isExceeded ? '#f43f5e' : '#10b981'}
                stroke="#0f172a"
                strokeWidth="1.5"
              />
            );
          })}

          <defs>
            <linearGradient id="ecGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="flex justify-between items-center text-[11px] text-slate-500 mt-2 px-1">
        <span>Oldest reading</span>
        <span>Latest reading (Live)</span>
      </div>
    </div>
  );
}
