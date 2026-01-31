from flask import Flask
import time
import os
from signal_proc import get_latest_window, extract_features
from apnea_detect import get_risk_score

app = Flask(__name__)

def console_alert(severity, features, risk_result):
    print("\n" + "="*60)
    print(f"🚨 {severity} APNEA DETECTED! 🚨")
    print(f"💓 HR: {features.get('mean_hr', 120):.0f} bpm")
    print(f"🫁 SpO2: {features.get('spo2_mean', 95):.0f}%")
    print(f"⚠️  Score: {risk_result['score']:.2f}")
    print(f"📊 Events/24h: {risk_result['events_24h']}")
    print("="*60 + "\n")

@app.route('/')
def health_check():
    return {"status": "NeonatalApneaGuard Backend ✅", "timestamp": time.time()}

@app.route('/monitor')
def monitor():
    try:
        df = get_latest_window()
        features = extract_features(df)
        risk_result = get_risk_score(features)
        
        if risk_result['risk'] == 'SEVERE':
            console_alert('SEVERE', features, risk_result)
        elif risk_result['risk'] == 'MODERATE':
            print(f"⚠️  MODERATE: Score {risk_result['score']:.2f}")
        
        return {
            'risk': risk_result,
            'features': features,
            'status': 'OK'
        }
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    print("🚀 Backend LIVE: http://localhost:5000")
    app.run(debug=True, port=5000)

