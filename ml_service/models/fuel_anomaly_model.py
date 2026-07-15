import pandas as pd
from sklearn.ensemble import IsolationForest

from db import fetch_fuel_logs


class FuelAnomalyDetector:
    def __init__(self):
        self.model = None
        self.feature_cols = ['liters', 'cost', 'price_per_liter', 'km_since_last', 'liters_per_100km']

    def _build_features(self):
        logs = fetch_fuel_logs()
        if logs.empty:
            return pd.DataFrame()

        logs = logs.sort_values(['vehicle_id', 'date']).copy()
        logs['prev_odometer'] = logs.groupby('vehicle_id')['odometer'].shift(1)
        logs['km_since_last'] = logs['odometer'] - logs['prev_odometer']
        logs['km_since_last'] = logs['km_since_last'].fillna(logs['km_since_last'].median())
        logs.loc[logs['km_since_last'] <= 0, 'km_since_last'] = 0.1

        logs['liters_per_100km'] = (logs['liters'] / logs['km_since_last']) * 100
        logs['liters_per_100km'] = logs['liters_per_100km'].clip(upper=200)

        return logs

    def train(self):
        df = self._build_features()
        if len(df) < 20:
            self.model = None
            return {'trained': False, 'reason': 'insufficient data'}
        X = df[self.feature_cols]
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(X)
        return {'trained': True, 'samples': len(df)}

    def predict_all(self):
        df = self._build_features()
        if df.empty or self.model is None:
            return []
        X = df[self.feature_cols]
        preds = self.model.predict(X)
        scores = self.model.score_samples(X)
        df['is_anomaly'] = (preds == -1)
        df['anomaly_score'] = scores.round(4)
        return df[['id', 'vehicle_id', 'is_anomaly', 'anomaly_score']].rename(
            columns={'id': 'fuel_log_id'}
        ).to_dict('records')