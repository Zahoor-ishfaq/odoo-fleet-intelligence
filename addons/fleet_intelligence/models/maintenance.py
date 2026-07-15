from odoo import models, fields


class FleetMaintenance(models.Model):
    _name = 'fleet.maintenance.custom'
    _description = 'Fleet Maintenance'
    _order = 'date desc'

    name = fields.Char(string='Reference', required=True, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle.custom', string='Vehicle', required=True)
    maintenance_type = fields.Selection([
        ('oil_change', 'Oil Change'),
        ('tire_change', 'Tire Change'),
        ('brake_service', 'Brake Service'),
        ('engine_repair', 'Engine Repair'),
        ('general_service', 'General Service'),
        ('other', 'Other'),
    ], string='Type', required=True)
    date = fields.Date(string='Service Date', required=True)
    cost = fields.Monetary(string='Cost', currency_field='currency_id', required=True)
    odometer_at_service = fields.Float(string='Odometer at Service (km)')
    next_due_km = fields.Float(string='Next Due (km)')
    notes = fields.Text(string='Notes')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.ref('base.SAR'))