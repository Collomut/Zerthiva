import React, { useState, useEffect } from 'react';
import { fetchFarms, fetchTelemetry, fetchAlerts } from './services/api';
import StatCard from './components/StatCard';
import SalinityChart from './components/SalinityChart';
import MoistureGauge from './components/MoistureGauge';
import SentryStatus from './components/SentryStatus';
import AlertBanner from './components/AlertBanner';
import LeachingModal from './components/LeachingModal';

export default function App() {
  const [farms, setFarms] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCalculatorOpen, setIsCalculatorOpen] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState(new Date().toLocaleTimeString());

  // Load initial data
  const loadDashboardData = async () => {
    try {
      const farmsData = await fetchFarms();
      setFarms(farmsData);
      const activeFarm = farmsData[0] || null;
      setSelectedFarm(activeFarm);

      const teleData = await fetchTelemetry('SG-NODE-001', 30);
      setTelemetry(teleData);

      const alertData = await fetchAlerts('SG-NODE-001');
      setAlerts(alertData);
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 15000); // Polling every 15s
    return () => clearInterval(interval);
  }, []);

  // Compute latest reading
  const latest = telemetry[0] || {
    normalized_ec_25: 1.65,
    raw_ec: 1.62,
    moisture_vwc: 31.4,
    soil_temp_c: 24.2,
    battery_voltage: 4.08,
    status: 'OPTIMAL',
    action: 'NONE',
    allow_fertilizer: true
  };

  const cropThreshold = selectedFarm?.crop_type === 'maize' ? 1.7 : 2.5;
  const isSaline = latest.normalized_ec_25 > cropThreshold;

  // Status mapping
  const ecStatus = isSaline ? 'danger' : (latest.normalized_ec_25 > cropThreshold * 0.85 ? 'warning' : 'optimal');
  const moistStatus = latest.moisture_vwc < 22.0 ? 'warning' : (latest.moisture_vwc > 38.0 ? 'warning' : 'optimal');
  const tempStatus = (latest.soil_temp_c >= 18 && latest.soil_temp_c <= 32) ? 'optimal' : 'warning';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Navigation Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/70 backdrop-blur-md sticky top-0 z-40 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-400 flex items-center justify-center font-black text-xl text-white shadow-lg shadow-emerald-950/40">
            🌱
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight text-white">SoilGuard</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                SIS v1.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Soil Intelligence System — Extension Officer Dashboard</p>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/60 border border-slate-700/60 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>Live Node: <strong className="text-white">SG-NODE-001</strong></span>
          </div>

          <button
            onClick={loadDashboardData}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white transition-colors"
          >
            <span>↻</span>
            <span className="hidden sm:inline">Refreshed: {lastRefreshed}</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-8 space-y-6">
        {/* Farm Selector & Context Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Farm:</span>
            <select
              value={selectedFarm?.id || 1}
              onChange={(e) => {
                const f = farms.find(farm => farm.id === Number(e.target.value));
                if (f) setSelectedFarm(f);
              }}
              className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs font-semibold text-white focus:outline-none focus:border-emerald-500"
            >
              {farms.map(f => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.farmer_name} — {f.crop_type.toUpperCase()})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-4 text-xs text-slate-400">
            <div>District: <strong className="text-slate-200">{selectedFarm?.district || 'Central'}</strong></div>
            <div>Acreage: <strong className="text-slate-200">{selectedFarm?.hectares || 1.5} Ha</strong></div>
            <div>Crop: <strong className="text-emerald-400 uppercase font-bold">{selectedFarm?.crop_type || 'Tomato'}</strong></div>
          </div>
        </div>

        {/* Dynamic Alert Banner */}
        <AlertBanner
          status={latest.status}
          message={
            latest.status === 'CRITICAL'
              ? `High salt concentration (${latest.normalized_ec_25} dS/m exceeds ${cropThreshold} dS/m threshold). Hold all fertilizer. Water with extra leaching volume.`
              : (latest.status === 'IRRIGATE'
                ? `Soil moisture (${latest.moisture_vwc}%) dropped below refill point. Standard irrigation needed.`
                : `Optimal field equilibrium. EC is safe (${latest.normalized_ec_25} dS/m) and moisture is balanced (${latest.moisture_vwc}%).`)
          }
          onOpenCalculator={() => setIsCalculatorOpen(true)}
        />

        {/* 4 Primary Stat Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Root Zone Salinity"
            value={latest.normalized_ec_25.toFixed(2)}
            unit="dS/m"
            subtitle={`Safe Limit: ${cropThreshold} dS/m`}
            status={ecStatus}
            icon="🧂"
          />

          <StatCard
            title="Soil Moisture"
            value={latest.moisture_vwc.toFixed(1)}
            unit="% VWC"
            subtitle="Target: 22% – 38%"
            status={moistStatus}
            icon="💧"
          />

          <StatCard
            title="Soil Temperature"
            value={latest.soil_temp_c.toFixed(1)}
            unit="°C"
            subtitle="Normalized to 25°C baseline"
            status={tempStatus}
            icon="🌡️"
          />

          <StatCard
            title="Node Power & Solar"
            value={latest.battery_voltage.toFixed(2)}
            unit="Volts"
            subtitle="Li-ion 3.7V / 5W Solar"
            status="optimal"
            icon="⚡"
          />
        </div>

        {/* Main 2-Column Agronomic Visualizer */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Time-Series Chart & Telemetry Log Table */}
          <div className="lg:col-span-2 space-y-6">
            <SalinityChart
              data={telemetry}
              threshold={cropThreshold}
              cropName={selectedFarm?.crop_type?.toUpperCase() || 'TOMATO'}
            />

            {/* Recent Telemetry Table */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white">Recent 15-Minute Sensor Telemetry</h3>
                  <p className="text-xs text-slate-400">Timestamped edge readings logged on MicroSD & synced via GPRS</p>
                </div>
                <span className="text-xs text-slate-400">{telemetry.length} records</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-700/60">
                    <tr>
                      <th className="py-2.5 px-3">Time</th>
                      <th className="py-2.5 px-3">$\text{EC}_{25}$</th>
                      <th className="py-2.5 px-3">Moist</th>
                      <th className="py-2.5 px-3">Temp</th>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Action</th>
                      <th className="py-2.5 px-3">Fertilizer</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {telemetry.slice(0, 8).map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-slate-300 font-sans">
                          {new Date(row.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </td>
                        <td className={`py-2.5 px-3 font-bold ${row.normalized_ec_25 > cropThreshold ? 'text-rose-400' : 'text-emerald-400'}`}>
                          {row.normalized_ec_25} dS/m
                        </td>
                        <td className="py-2.5 px-3 text-slate-300">{row.moisture_vwc}%</td>
                        <td className="py-2.5 px-3 text-slate-300">{row.soil_temp_c}°C</td>
                        <td className="py-2.5 px-3 font-sans">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            row.status === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300' : (
                              row.status === 'IRRIGATE' ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'
                            )
                          }`}>
                            {row.status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-sans text-slate-300">{row.action}</td>
                        <td className="py-2.5 px-3 font-sans">
                          <span className={row.allow_fertilizer ? 'text-emerald-400 font-semibold' : 'text-rose-400 font-bold'}>
                            {row.allow_fertilizer ? 'ALLOW' : 'LOCKED'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Column: Gauges, Beacon Sentry, and Alerts */}
          <div className="space-y-6">
            <SentryStatus
              status={latest.status}
              color={latest.status === 'CRITICAL' ? 'RED' : (latest.status === 'IRRIGATE' ? 'YELLOW' : 'GREEN')}
              allowFertilizer={latest.allow_fertilizer}
              action={latest.action}
            />

            <MoistureGauge
              moisture={latest.moisture_vwc}
              minRefill={22.0}
              fieldCapacity={38.0}
            />

            {/* Farmer SMS Dispatch Audit Card */}
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>📱 Cellular SMS Gateway</span>
                </h4>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Feature Phone Ready
                </span>
              </div>
              <p className="text-xs text-slate-400 mb-3">Direct notifications sent to farmer Nokia 105 in plain language:</p>

              <div className="space-y-2.5">
                {alerts.length > 0 ? (
                  alerts.slice(0, 2).map((a, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60 text-xs">
                      <div className="flex items-center justify-between text-slate-400 mb-1 text-[11px]">
                        <span>To: <strong className="text-slate-200">{a.sms_recipient || selectedFarm?.farmer_phone}</strong></span>
                        <span>{new Date(a.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                      <p className="text-slate-200 leading-relaxed font-sans">{a.sms_content}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-3 rounded-xl bg-slate-800/40 text-center text-xs text-slate-500">
                    No critical SMS alerts triggered today.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Interactive FAO Leaching Calculator Modal */}
      <LeachingModal
        isOpen={isCalculatorOpen}
        onClose={() => setIsCalculatorOpen(false)}
        defaultCrop={selectedFarm?.crop_type || 'tomato'}
        defaultEc={latest.normalized_ec_25}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 px-8 py-5 text-center text-xs text-slate-500">
        <p>SoilGuard — Soil Intelligence System (SIS) · Agricultural Technology & Innovation Competition 2026</p>
        <p className="mt-1 text-[11px] text-slate-600">Hardware BOM Target: $30–35 · Peer-Reviewed FAO-56 Agronomic Decision Core</p>
      </footer>
    </div>
  );
}
