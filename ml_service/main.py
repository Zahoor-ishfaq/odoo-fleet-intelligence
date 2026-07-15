from fastapi import FastAPI
from models.maintenance_model import MaintenancePredictor
from models.fuel_anomaly_model import FuelAnomalyDetector
from models.route_profit_model import RouteProfitAnalyzer

app = FastAPI(title='Fleet Intelligence ML Service', version='1.0.0')

maintenance_predictor = MaintenancePredictor()
fuel_anomaly_detector = FuelAnomalyDetector()
route_profit_analyzer = RouteProfitAnalyzer()


@app.on_event('startup')
def train_models():
    print('Training maintenance model...')
    print(f'Maintenance: {maintenance_predictor.train()}')
    print('Training fuel anomaly model...')
    print(f'Fuel anomaly: {fuel_anomaly_detector.train()}')
    print('Training route profit model...')
    print(f'Route profit: {route_profit_analyzer.train()}')


@app.get('/')
def root():
    return {'status': 'ok', 'service': 'fleet-intelligence-ml'}


@app.get('/health')
def health():
    return {'status': 'healthy'}


@app.get('/predict/maintenance')
def predict_maintenance():
    return {'predictions': maintenance_predictor.predict_all()}


@app.get('/predict/fuel-anomaly')
def predict_fuel_anomaly():
    return {'predictions': fuel_anomaly_detector.predict_all()}


@app.get('/predict/route-profit')
def predict_route_profit(top_n: int = 5):
    return route_profit_analyzer.route_summary(top_n=top_n)


@app.get('/predict/route-profit/estimate')
def estimate_route_profit(distance_km: float):
    profit = route_profit_analyzer.predict_profit(distance_km)
    return {'distance_km': distance_km, 'estimated_profit': profit}