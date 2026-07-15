import logging
import requests
from datetime import datetime
from odoo import models, api

_logger = logging.getLogger(__name__)

ML_SERVICE_URL = 'http://ml_service:8000'
REQUEST_TIMEOUT = 30


class MLPredictionRunner(models.AbstractModel):
    _name = 'fleet.ml.runner'
    _description = 'ML Prediction Runner'

    @api.model
    def _call_ml(self, endpoint):
        try:
            response = requests.get(f'{ML_SERVICE_URL}{endpoint}', timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f'ML service call failed for {endpoint}: {e}')
            return None

    @api.model
    def run_maintenance_predictions(self):
        data = self._call_ml('/predict/maintenance')
        if not data or 'predictions' not in data:
            return

        now = datetime.now()
        Vehicle = self.env['fleet.vehicle.custom']
        updated = 0

        for pred in data['predictions']:
            vehicle = Vehicle.browse(pred['vehicle_id'])
            if not vehicle.exists():
                continue

            probability = pred.get('probability', 0.0)
            if probability >= 0.7:
                status = 'overdue'
            elif probability >= 0.4:
                status = 'due_soon'
            else:
                status = 'ok'

            vehicle.write({
                'maintenance_prediction': status,
                'maintenance_risk_score': probability,
                'prediction_last_updated': now,
            })
            updated += 1

        _logger.info(f'Maintenance predictions updated for {updated} vehicles')

    @api.model
    def run_fuel_anomaly_detection(self):
        data = self._call_ml('/predict/fuel-anomaly')
        if not data or 'predictions' not in data:
            return

        now = datetime.now()
        FuelLog = self.env['fleet.fuel.log']
        updated = 0

        for pred in data['predictions']:
            log = FuelLog.browse(pred['fuel_log_id'])
            if not log.exists():
                continue

            log.write({
                'anomaly_status': 'anomaly' if pred['is_anomaly'] else 'normal',
                'anomaly_score': pred['anomaly_score'],
                'prediction_last_updated': now,
            })
            updated += 1

        _logger.info(f'Fuel anomaly predictions updated for {updated} logs')

    @api.model
    def run_all_predictions(self):
        self.run_maintenance_predictions()
        self.run_fuel_anomaly_detection()