import pandas as pd
import numpy as np
import os
import asyncio
from ml_pipeline.real_world_data_fetcher import aggregate_real_world_data, get_emdat_distribution_params

# Set random seed for reproducibility
np.random.seed(42)

# Directory for data
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models_data')
os.makedirs(DATA_DIR, exist_ok=True)

def generate_disaster_data(num_samples=20000):
    """
    SDIRS Advanced Data Generator
    Grounded in real-world statistical distributions (EM-DAT, NOAA, NASA FIRMS).
    """
    print(f"Generating {num_samples} samples of SDIRS intelligence data...")
    
    # EM-DAT Distribution Parameters (Module 10 Pillar)
    emdat = get_emdat_distribution_params()
    
    # 1. Base Environment (NOAA/Open-Meteo typical distributions)
    temp = np.random.normal(25, 10, num_samples).clip(-10, 55)
    # Rainfall: Gamma distribution is better for meteorological data
    rainfall = np.random.gamma(shape=2, scale=50, size=num_samples).clip(0, 1000)
    wind_speed = np.random.rayleigh(scale=15, size=num_samples).clip(0, 300)
    
    # Population Density: Log-normal distribution (more cities, many rural areas)
    pop_density = np.random.lognormal(mean=6, sigma=1.5, size=num_samples).clip(1, 25000)
    
    # Historical Frequency (EM-DAT grounded)
    historical_freq = np.random.poisson(lam=3, size=num_samples).clip(0, 20)
    
    # 2. IoT Sensor Fusion Simulation (Seismic, Water, Smoke)
    # Water level correlated with rainfall (Flood)
    water_level = (rainfall / 100 * 1.5 + np.random.normal(0, 0.2, num_samples)).clip(0, 15)
    
    # Smoke PPM (Wildfire indicator - NASA FIRMS grounded)
    # Wildfire frequency is 5% in EM-DAT
    smoke_ppm = np.random.normal(20, 5, num_samples)
    fire_indices = np.random.choice(num_samples, int(num_samples * emdat['wildfire_freq']), replace=False)
    smoke_ppm[fire_indices] += np.random.uniform(200, 800, len(fire_indices))
    smoke_ppm = smoke_ppm.clip(0, 1000)
    
    # Seismic Magnitude (USGS grounded)
    seismic_mag = np.random.exponential(scale=0.5, size=num_samples).clip(0, 9)
    eq_indices = np.random.choice(num_samples, int(num_samples * emdat['earthquake_freq']), replace=False)
    seismic_mag[eq_indices] += np.random.uniform(3, 6, len(eq_indices))
    seismic_mag = seismic_mag.clip(0, 9.5)
    
    humidity = (100 - (temp/55 * 70) - (rainfall/1000 * -20) + np.random.normal(0, 5, num_samples)).clip(5, 100)
    
    # 3. Target Labeling (Severity & Risk Class)
    # Severity Score (Weighted impact based on EM-DAT risk metrics)
    severity_score = (
        (rainfall > 250).astype(int) * 0.4 + 
        (wind_speed > 100).astype(int) * 0.3 + 
        (seismic_mag > 6.0).astype(int) * 0.5 + 
        (smoke_ppm > 400).astype(int) * 0.3 +
        (pop_density / 25000 * 0.2)
    )
    severity = pd.cut(severity_score, bins=[-np.inf, 0.2, 0.5, 0.8, np.inf], labels=[0, 1, 2, 3]).astype(int)
    
    # Risk Class (Predictive probability for Command Center)
    risk_score = (water_level/15 * 0.3 + seismic_mag/9 * 0.3 + smoke_ppm/1000 * 0.2 + (wind_speed/300 * 0.2))
    risk_class = pd.cut(risk_score, bins=[-np.inf, 0.25, 0.5, 0.75, np.inf], labels=[0, 1, 2, 3]).astype(int)
    
    # 4. Resource Demand (Smart Allocation AI V2 Grounding)
    ambulances = (severity * 5 + (pop_density/2000) + np.random.poisson(1, num_samples)).clip(0).astype(int)
    fire_trucks = ( (smoke_ppm > 200).astype(int) * 3 + severity * 2 + np.random.poisson(0.5, num_samples)).clip(0).astype(int)
    rescue_boats = ( (water_level > 5).astype(int) * 5 + (rainfall > 300).astype(int) * 2 + np.random.poisson(0.2, num_samples)).clip(0).astype(int)
    
    df = pd.DataFrame({
        'temp': temp, 'rainfall': rainfall, 'wind_speed': wind_speed,
        'pop_density': pop_density, 'historical_freq': historical_freq,
        'water_level': water_level, 'seismic_mag': seismic_mag,
        'smoke_ppm': smoke_ppm, 'humidity': humidity,
        'severity': severity, 'risk_class': risk_class,
        'ambulances': ambulances, 'fire_trucks': fire_trucks, 'rescue_boats': rescue_boats
    })

    # --- Oversampling to fix class imbalance ---
    print("Oversampling rare disaster events for model robustness...")
    high_sev = df[df['severity'] >= 2]
    critical_sev = df[df['severity'] == 3]
    high_risk = df[df['risk_class'] >= 2]
    
    # Duplicate rare events
    df = pd.concat([
        df, 
        high_sev.sample(n=min(len(high_sev)*5, 5000), replace=True),
        critical_sev.sample(n=min(len(critical_sev)*20, 2000), replace=True),
        high_risk.sample(n=min(len(high_risk)*3, 3000), replace=True)
    ], ignore_index=True)
    
    # 5. Integrate Real-World Fetched Data
    real_events = asyncio.run(aggregate_real_world_data())
    real_rows = []
    for ev in real_events:
        # Map real events to our feature space
        row = {
            'temp': 25.0 + np.random.normal(0, 5),
            'rainfall': 0.0, 'wind_speed': 10.0,
            'pop_density': 1000.0 + np.random.uniform(0, 5000),
            'historical_freq': 5.0, 'water_level': 0.5,
            'seismic_mag': 0.0, 'smoke_ppm': 20.0, 'humidity': 50.0
        }
        
        if ev['event_type'] == 'earthquake':
            row['seismic_mag'] = ev['severity_val']
        elif ev['event_type'] == 'wildfire':
            row['smoke_ppm'] = 200 + ev['severity_val']
            row['temp'] += 10
        elif ev['event_type'] == 'flood':
            row['water_level'] = min(15, ev['severity_val'] / 500)
            row['rainfall'] = 200 + np.random.uniform(0, 200)

        # Recalculate labels for real data to maintain consistency
        s_score = (row['rainfall'] > 250) * 0.4 + (row['wind_speed'] > 100) * 0.3 + (row['seismic_mag'] > 6.0) * 0.5 + (row['smoke_ppm'] > 400) * 0.3 + (row['pop_density']/25000 * 0.2)
        row['severity'] = 3 if s_score > 0.8 else 2 if s_score > 0.5 else 1 if s_score > 0.2 else 0
        
        r_score = (row['water_level']/15 * 0.3 + row['seismic_mag']/9 * 0.3 + row['smoke_ppm']/1000 * 0.2 + (row['wind_speed']/300 * 0.2))
        row['risk_class'] = 3 if r_score > 0.75 else 2 if r_score > 0.5 else 1 if r_score > 0.25 else 0
        
        row['ambulances'] = int(row['severity'] * 5 + (row['pop_density']/2000))
        row['fire_trucks'] = int((row['smoke_ppm'] > 200) * 3 + row['severity'] * 2)
        row['rescue_boats'] = int((row['water_level'] > 5) * 5 + (row['rainfall'] > 300) * 2)
        
        real_rows.append(row)
    
    if real_rows:
        real_df = pd.DataFrame(real_rows)
        df = pd.concat([df, real_df], ignore_index=True)
        print(f"Merged {len(real_rows)} real-world points with {num_samples} synthetic samples.")

    output_path = os.path.join(DATA_DIR, 'disaster_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Final SDIRS Dataset: {len(df)} rows saved to {output_path}")

if __name__ == "__main__":
    generate_disaster_data()
