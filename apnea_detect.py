import pandas as pd
import numpy as np
import sqlite3
import os

# Hardcoded clinical thresholds
APNEA_PAUSE_SEC = 20
SPO2_THRESHOLD = 85
HR_BRADYCARDIA = 100

def rule_based_detect(features):
    """Returns both risk level AND numeric score"""
    score = 0
    
    # Respiratory pause ≥20s (33% of 60s window)
    if features.get('resp_pause_ratio', 0) > 0.33:
        score += 0.4
    
    # SpO2 desaturation
    if features.get('spo2_min', 95) < SPO2_THRESHOLD:
        score += 0.3
    
    # Bradycardia
    if features.get('mean_hr', 120) < HR_BRADYCARDIA:
        score += 0.2
    
    # Risk classification (return BOTH score and risk)
    if score >= 0.7: 
        risk_level = 'SEVERE'
    elif score >= 0.4: 
        risk_level = 'MODERATE'
    else: 
        risk_level = 'MILD'
    
    return risk_level, score  # RETURN TUPLE!

def get_risk_score(features):
    """Combined rule + history scoring - FIXED!"""
    current_risk, base_score = rule_based_detect(features)  # Get both!
    
    # History factor (events last 24h)
    try:
        if os.path.exists('data/vitals.db'):
            conn = sqlite3.connect('data/vitals.db')
            history_events = pd.read_sql("""
                SELECT COUNT(*) as events 
                FROM vitals 
                WHERE timestamp > datetime('now', '-1 day')
            """, conn).iloc[0]['events']
            conn.close()
        else:
            history_events = 0
    except:
        history_events = 0
    
    history_factor = min(history_events / 10, 0.3)
    final_score = min(1.0, base_score + history_factor)
    
    return {
        'risk': current_risk,
        'score': final_score,
        'events_24h': int(history_events)
    }

if __name__ == "__main__":
    try:
        from signal_proc import get_latest_window, extract_features
        df = get_latest_window()
        features = extract_features(df)
        result = get_risk_score(features)
        print("✅ RISK ASSESSMENT:", result)
    except Exception as e:
        print(f"❌ Test error: {e}")
        print("Demo: {'risk': 'MODERATE', 'score': 0.45, 'events_24h': 3}")

