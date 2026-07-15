from datetime import datetime, timedelta
from odoo import models, api


class FleetDashboard(models.AbstractModel):
    _name = 'fleet.dashboard'
    _description = 'Fleet Intelligence Dashboard Data'

    @api.model
    def get_dashboard_data(self):
        Vehicle = self.env['fleet.vehicle.custom']
        Trip = self.env['fleet.trip']
        FuelLog = self.env['fleet.fuel.log']

        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        maintenance_due = Vehicle.search_count([
            ('maintenance_prediction', 'in', ['due_soon', 'overdue'])
        ])
        total_vehicles = Vehicle.search_count([])
        anomaly_count = FuelLog.search_count([
            ('anomaly_status', '=', 'anomaly'),
            ('date', '>=', month_start.date()),
        ])

        trips = Trip.search([])
        route_stats = {}
        for trip in trips:
            key = f'{trip.origin} → {trip.destination}'
            if key not in route_stats:
                route_stats[key] = {'route': key, 'trips': 0, 'profit': 0.0}
            route_stats[key]['trips'] += 1
            route_stats[key]['profit'] += trip.profit

        unprofitable = sorted(route_stats.values(), key=lambda r: r['profit'])[:5]

        six_months_ago = datetime.now() - timedelta(days=180)
        cost_trend = {}
        for log in FuelLog.search([('date', '>=', six_months_ago.date())]):
            key = log.date.strftime('%Y-%m')
            cost_trend[key] = cost_trend.get(key, 0.0) + log.cost
        cost_trend_list = [{'month': k, 'cost': round(v, 2)} for k, v in sorted(cost_trend.items())]

        return {
            'maintenance_due': maintenance_due,
            'total_vehicles': total_vehicles,
            'anomaly_count': anomaly_count,
            'unprofitable_routes': [
                {'route': r['route'], 'trips': r['trips'], 'profit': round(r['profit'], 2)}
                for r in unprofitable
            ],
            'cost_trend': cost_trend_list,
        }