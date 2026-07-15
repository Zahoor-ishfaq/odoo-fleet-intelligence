import pandas as pd
from sklearn.linear_model import LinearRegression

from db import fetch_trips


class RouteProfitAnalyzer:
    def __init__(self):
        self.model = None

    def _load(self):
        trips = fetch_trips()
        if trips.empty:
            return pd.DataFrame()
        trips = trips.dropna(subset=['distance_km', 'revenue', 'cost'])
        trips['route'] = trips['origin'] + ' → ' + trips['destination']
        return trips

    def train(self):
        df = self._load()
        if len(df) < 10:
            self.model = None
            return {'trained': False, 'reason': 'insufficient data'}
        X = df[['distance_km']]
        y = df['profit']
        self.model = LinearRegression()
        self.model.fit(X, y)
        return {'trained': True, 'samples': len(df)}

    def route_summary(self, top_n=10):
        df = self._load()
        if df.empty:
            return {'unprofitable': [], 'most_profitable': []}

        summary = df.groupby('route').agg(
            trip_count=('id', 'count'),
            avg_distance=('distance_km', 'mean'),
            total_revenue=('revenue', 'sum'),
            total_cost=('cost', 'sum'),
            total_profit=('profit', 'sum'),
            avg_profit=('profit', 'mean'),
        ).round(2).reset_index()

        summary['margin_pct'] = ((summary['total_profit'] / summary['total_revenue']) * 100).round(1)
        summary = summary.sort_values('avg_profit')

        unprofitable = summary.head(top_n).to_dict('records')
        most_profitable = summary.tail(top_n).sort_values('avg_profit', ascending=False).to_dict('records')

        return {'unprofitable': unprofitable, 'most_profitable': most_profitable}

    def predict_profit(self, distance_km):
        if self.model is None:
            return None
        return round(float(self.model.predict([[distance_km]])[0]), 2)