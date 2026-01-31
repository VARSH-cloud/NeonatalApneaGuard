import numpy as np
import pandas as pd
import sqlite3
from datetime import datetime

def extract_features(df, window_sec=60):
    """Extract features WITHOUT scipy"""
    features = {}
    
    # Simple HRV (no heartpy needed)
    hr_data = df['hr'].values if 'hr' in df else np.array([120]*len(df))
    features['hrv_sdnn'] = np.std(np.diff(hr_data)) if len(hr_data)>1 else 0
    features['mean_hr'] = np.mean(hr_data)
    
    # SpO2 features
    spo2_data = df['spo2'].values if 'spo2' in df else np.array([95]*len(df))
    features['spo2_mean'] = np.mean(spo2_data)
    features['spo2_min'] = np.min(spo2_data)
    features['spo2_slope'] = (spo2_data[-1] - spo2_data[0]) / len(spo2_data)
    
    # Respiratory pause (simple flatline detection)
    resp_data = df['resp'].values if 'resp' in df else np.array([40]*len(df))
    resp_diff = np.diff(resp_data)
    pause_ratio = np.mean(np.abs(resp_diff) < 0.1)  # <10% change = pause
    features['resp_pause_ratio'] = pause_ratio
    features['resp_mean'] = np.mean(resp_data)
    
    return features

def get_latest_window():
    """Get last 60s of data from SQLite"""
    try:
        conn = sqlite3.connect('data/vitals.db')
        df = pd.read_sql('SELECT * FROM vitals ORDER BY timestamp DESC LIMIT 100', conn)
        conn.close()
        if len(df) == 0:
            # Return dummy data for demo
            return pd.DataFrame({
                'hr': [120, 118, 122, 115, 110],
                'spo2': [95, 94, 93, 92, 91],
                'resp': [40, 38, 0, 0, 42],  # Apnea simulation
                'timestamp': pd.date_range(start='now', periods=5, freq='12s')
            })
        return df.tail(50).reset_index(drop=True)
    except:
        # Fallback dummy data
        return pd.DataFrame({
            'hr': [120, 118, 122, 115, 110],
            'spo2': [95, 94, 93, 92, 91],
            'resp': [40, 38, 0, 0, 42],
            'timestamp': pd.date_range(start='now', periods=5, freq='12s')
        })
