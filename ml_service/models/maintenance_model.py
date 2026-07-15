import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta

from db import fetch_vehicles, fetch_maintenance, fetch_trips


class MaintenancePredictor:
    def __init__(self):
        self.model = None
        self.feature_cols = ['odometer', 'age_years', 'km_since_last_service',
                             'days_since_last_service', 'trip_count_last_30d']

    def _build_features(self):
        vehicles = fetch_vehicles()
        maint = fetch_maintenance()
        trips = fetch_trips()

        today = pd.Timestamp(datetime.now().date())
        rows = []

        for _, v in vehicles.iterrows():
            v_maint = maint[maint['vehicle_id'] == v['id']].sort_values('date')
            v_trips = trips[trips['vehicle_id'] == v['id']]

            if len(v_maint) == 0:
                continue

            last_service = v_maint.iloc[-1]
            last_service_date = pd.Timestamp(last_service['date'])
            km_since = v['odometer'] - (last_service['odometer_at_service'] or 0)
            days_since = (today - last_service_date).days

            recent_trips = v_trips[
                pd.to_datetime(v_trips['start_time']) >= (today - timedelta(days=30))
            ]

            needs_soon = 1 if (
                km_since > 8000 or days_since > 150 or
                (last_service['next_due_km'] and v['odometer'] >= last_service['next_due_km'])
            ) else 0

            rows.append({
                'vehicle_id': v['id'],
                'odometer': v['odometer'],
                'age_years': datetime.now().year - v['year'],
                'km_since_last_service': km_since,
                'days_since_last_service': days_since,
                'trip_count_last_30d': len(recent_trips),
                'needs_maintenance': needs_soon,
            })

        return pd.DataFrame(rows)

    def train(self):
        df = self._build_features()
        if len(df) < 5 or df['needs_maintenance'].nunique() < 2:
            self.model = None
            return {'trained': False, 'reason': 'insufficient data'}
        X = df[self.feature_cols]
        y = df['needs_maintenance']
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        return {'trained': True, 'samples': len(df)}

    def predict_all(self):
        df = self._build_features()
        if df.empty:
            return []
        if self.model is None:
            return df[['vehicle_id']].assign(needs_maintenance=False, probability=0.0).to_dict('records')

        X = df[self.feature_cols]
        probs = self.model.predict_proba(X)[:, 1]
        preds = self.model.predict(X)
        df['needs_maintenance'] = preds.astype(bool)
        df['probability'] = probs.round(3)
        return df[['vehicle_id', 'needs_maintenance', 'probability']].to_dict('records')