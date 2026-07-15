from odoo import models, fields, api


class FleetFuelLog(models.Model):
    _name = 'fleet.fuel.log'
    _description = 'Fuel Log'
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle.custom', string='Vehicle', required=True)
    date = fields.Date(string='Date', required=True)
    liters = fields.Float(string='Liters', required=True)
    cost = fields.Monetary(string='Cost', currency_field='currency_id', required=True)
    odometer = fields.Float(string='Odometer (km)', required=True)
    price_per_liter = fields.Float(string='Price/Liter', compute='_compute_price_per_liter', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.ref('base.SAR'))

    anomaly_status = fields.Selection([
        ('normal', 'Normal'),
        ('anomaly', 'Anomaly'),
    ], string='Anomaly Status', readonly=True, default='normal')
    anomaly_score = fields.Float(string='Anomaly Score', readonly=True, digits=(6, 4))
    prediction_last_updated = fields.Datetime(string='Prediction Updated', readonly=True)

    @api.depends('cost', 'liters')
    def _compute_price_per_liter(self):
        for log in self:
            log.price_per_liter = log.cost / log.liters if log.liters else 0.0