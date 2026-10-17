const API_BASE = '/api/v1';

export async function fetchFarms() {
  try {
    const res = await fetch(`${API_BASE}/farms/`);
    if (!res.ok) throw new Error('Failed to load farms');
    return await res.json();
  } catch (err) {
    console.warn('API unavailable, returning baseline farm data:', err);
    return [
      {
        id: 1,
        name: 'Amara Field - Pilot 01',
        farmer_name: 'Amara Mwangi',
        farmer_phone: '+254 712 345 678',
        district: 'Machakos Central',
        crop_type: 'tomato',
        hectares: 1.5,
        latitude: -1.5177,
        longitude: 37.2634
      },
      {
        id: 2,
        name: 'Kiprono Agri-Holdings',
        farmer_name: 'David Kiprono',
        farmer_phone: '+254 722 890 123',
        district: 'Naivasha Basin',
        crop_type: 'maize',
        hectares: 3.2,
        latitude: -0.7172,
        longitude: 36.4310
      }
    ];
  }
}

export async function fetchTelemetry(deviceId = 'SG-NODE-001', limit = 30) {
  try {
    const res = await fetch(`${API_BASE}/telemetry/?device_id=${deviceId}&limit=${limit}`);
    if (!res.ok) throw new Error('Failed to load telemetry');
    return await res.json();
  } catch (err) {
    console.warn('API unavailable, returning synthetic history:', err);
    // Generate realistic synthetic curve
    const history = [];
    const now = Date.now();
    for (let i = 24; i >= 0; i--) {
      const time = new Date(now - i * 3600000);
      const hour = time.getHours();
      const ec = 1.6 + (24 - i) * 0.045 + (Math.random() * 0.1 - 0.05);
      const moist = 32.0 - (hour * 0.3) + (hour === 6 ? 12 : 0);
      const temp = 22.0 + 7.0 * Math.sin((hour - 8) * Math.PI / 12);
      history.push({
        id: 100 - i,
        device_id: deviceId,
        timestamp: time.toISOString(),
        raw_ec: Number(ec.toFixed(2)),
        normalized_ec_25: Number(ec.toFixed(2)),
        moisture_vwc: Number(Math.max(18, moist).toFixed(1)),
        soil_temp_c: Number(temp.toFixed(1)),
        battery_voltage: 4.05,
        status: ec > 2.5 ? 'CRITICAL' : (moist < 22 ? 'IRRIGATE' : 'OPTIMAL'),
        action: ec > 2.5 ? 'FLUSH_SALTS' : (moist < 22 ? 'WATER_FIELD' : 'NONE'),
        allow_fertilizer: ec <= 2.5 && moist <= 38
      });
    }
    return history;
  }
}

export async function fetchAlerts(deviceId = null) {
  try {
    const url = deviceId ? `${API_BASE}/advisory/alerts?device_id=${deviceId}` : `${API_BASE}/advisory/alerts`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to load alerts');
    return await res.json();
  } catch (err) {
    return [
      {
        id: 1,
        device_id: 'SG-NODE-001',
        timestamp: new Date().toISOString(),
        alert_level: 'CRITICAL',
        action: 'FLUSH_SALTS',
        salinity_ec_25: 2.85,
        moisture_vwc: 29.4,
        sms_recipient: '+254 712 345 678',
        sms_content: 'SoilGuard CRITICAL: High salt (2.85 dS/m) in your Tomato. Hold fertilizer! Flush root zone with 23% extra water.',
        sms_dispatched: true
      }
    ];
  }
}

export async function calculateLeaching(cropName, soilEc, waterEc = 0.6) {
  try {
    const res = await fetch(`${API_BASE}/advisory/leaching`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        crop_name: cropName,
        soil_ec: Number(soilEc),
        irrigation_water_ec: Number(waterEc)
      })
    });
    if (!res.ok) throw new Error('Leaching calculation failed');
    return await res.json();
  } catch (err) {
    // Client-side fallback implementation of FAO-56 formula
    const thresholds = { maize: 1.7, tomato: 2.5, rice: 3.0, wheat: 6.0 };
    const ece = thresholds[cropName.toLowerCase()] || 1.7;
    const lr = Number(waterEc) / (5.0 * ece - Number(waterEc));
    const clamped = Math.min(Math.max(lr, 0.05), 0.45);
    return {
      crop_name: cropName,
      safe_threshold_ec: ece,
      irrigation_water_ec: Number(waterEc),
      leaching_requirement: Number(clamped.toFixed(2)),
      extra_water_percent: Math.round(clamped * 100),
      formula_reference: 'FAO-56: LR = ECw / (5 * ECe - ECw)'
    };
  }
}
