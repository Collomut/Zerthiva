"""
FAO-56 Crop Salinity Tolerance & Irrigation Reference Tables
Data compiled from FAO Irrigation and Drainage Paper 29 & Paper 56.
"""

CROP_PROFILES = {
    "maize": {
        "display_name": "Maize (Corn)",
        "threshold_ec": 1.7,       # Salinity threshold (dS/m) where yield loss begins
        "slope_percent": 12.0,      # Yield decline % per dS/m increase above threshold
        "min_moisture_vwc": 22.0,   # Refill point (% volumetric water content)
        "max_moisture_vwc": 38.0,   # Field capacity
        "optimal_temp_min": 18.0,   # Soil temperature range (°C)
        "optimal_temp_max": 32.0,
        "standard_npk_dose": "3.5 kg / 100m²"
    },
    "tomato": {
        "display_name": "Tomato",
        "threshold_ec": 2.5,
        "slope_percent": 9.9,
        "min_moisture_vwc": 25.0,
        "max_moisture_vwc": 40.0,
        "optimal_temp_min": 18.0,
        "optimal_temp_max": 28.0,
        "standard_npk_dose": "2.8 kg / 100m²"
    },
    "rice": {
        "display_name": "Rice (Paddy)",
        "threshold_ec": 3.0,
        "slope_percent": 12.0,
        "min_moisture_vwc": 35.0,
        "max_moisture_vwc": 55.0,
        "optimal_temp_min": 20.0,
        "optimal_temp_max": 35.0,
        "standard_npk_dose": "4.0 kg / 100m²"
    },
    "wheat": {
        "display_name": "Wheat",
        "threshold_ec": 6.0,
        "slope_percent": 7.1,
        "min_moisture_vwc": 20.0,
        "max_moisture_vwc": 35.0,
        "optimal_temp_min": 15.0,
        "optimal_temp_max": 25.0,
        "standard_npk_dose": "3.0 kg / 100m²"
    },
    "potato": {
        "display_name": "Potato",
        "threshold_ec": 1.7,
        "slope_percent": 12.0,
        "min_moisture_vwc": 25.0,
        "max_moisture_vwc": 42.0,
        "optimal_temp_min": 15.0,
        "optimal_temp_max": 24.0,
        "standard_npk_dose": "3.2 kg / 100m²"
    },
    "onion": {
        "display_name": "Onion",
        "threshold_ec": 1.2,
        "slope_percent": 16.0,
        "min_moisture_vwc": 22.0,
        "max_moisture_vwc": 38.0,
        "optimal_temp_min": 16.0,
        "optimal_temp_max": 26.0,
        "standard_npk_dose": "2.5 kg / 100m²"
    }
}


def get_crop_profile(crop_name: str) -> dict:
    """Returns crop parameters or defaults to maize if unrecognized"""
    key = str(crop_name).lower().strip()
    return CROP_PROFILES.get(key, CROP_PROFILES["maize"])
