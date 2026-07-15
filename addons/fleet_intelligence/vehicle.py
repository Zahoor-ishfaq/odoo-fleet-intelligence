from odoo import models, fields


class FleetVehicle(models.Model):
    _name = 'fleet.vehicle.custom'
    _description = 'Fleet Vehicle'
    _rec_name = 'plate_number'

    plate_number = fields.Char(string='Plate Number', required=True)
    make = fields.Char(string='Make', required=True)
    model = fields.Char(string='Model', required=True)
    year = fields.Integer(string='Year', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('maintenance', 'In Maintenance'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', required=True)
    odometer = fields.Float(string='Odometer (km)', default=0.0)
    notes = fields.Text(string='Notes')

    trip_ids = fields.One2many('fleet.trip', 'vehicle_id', string='Trips')
    fuel_log_ids = fields.One2many('fleet.fuel.log', 'vehicle_id', string='Fuel Logs')
    maintenance_ids = fields.One2many('fleet.maintenance.custom', 'vehicle_id', string='Maintenance Records')

    trip_count = fields.Integer(string='Trip Count', compute='_compute_counts')
    fuel_log_count = fields.Integer(string='Fuel Log Count', compute='_compute_counts')
    maintenance_count = fields.Integer(string='Maintenance Count', compute='_compute_counts')

    needs_maintenance = fields.Boolean(string='Needs Maintenance', default=False)
    maintenance_probability = fields.Float(string='Maintenance Risk', default=0.0)
    last_prediction_at = fields.Datetime(string='Last Prediction')

    def _compute_counts(self):
        for vehicle in self:
            vehicle.trip_count = len(vehicle.trip_ids)
            vehicle.fuel_log_count = len(vehicle.fuel_log_ids)
            vehicle.maintenance_count = len(vehicle.maintenance_ids)