from odoo import models, fields, api
from odoo.exceptions import UserError


class FleetTrip(models.Model):
    _name = 'fleet.trip'
    _description = 'Fleet Trip'
    _order = 'start_time desc'

    name = fields.Char(string='Trip Reference', required=True, default='New')
    vehicle_id = fields.Many2one('fleet.vehicle.custom', string='Vehicle', required=True)
    driver_name = fields.Char(string='Driver', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    origin = fields.Char(string='Origin', required=True)
    destination = fields.Char(string='Destination', required=True)
    distance_km = fields.Float(string='Distance (km)', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time')
    revenue = fields.Monetary(string='Revenue', currency_field='currency_id')
    cost = fields.Monetary(string='Cost', currency_field='currency_id')
    profit = fields.Monetary(string='Profit', compute='_compute_profit', store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.ref('base.SAR'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('invoiced', 'Invoiced'),
    ], string='Status', default='draft')
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True)

    @api.depends('revenue', 'cost')
    def _compute_profit(self):
        for trip in self:
            trip.profit = trip.revenue - trip.cost

    def action_generate_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            raise UserError('Invoice already exists for this trip.')
        if not self.revenue:
            raise UserError('Trip has no revenue to invoice.')
        if not self.partner_id:
            raise UserError('Please set a Customer before generating an invoice.')

        company = self.env.company
        tax = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('amount', '=', 15.0),
            ('company_id', '=', company.id),
        ], limit=1)

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'name': f'Trip: {self.origin} → {self.destination}',
                'quantity': 1,
                'price_unit': self.revenue,
                'account_id': self._get_default_income_account(company).id,
                'tax_ids': [(6, 0, tax.ids)],
            })],
        })
        self.invoice_id = invoice.id
        self.state = 'invoiced'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }

    def _get_default_income_account(self, company):
        """Fallback income account since invoice lines here have no product to derive one from."""
        account = self.env['account.account'].search([
            ('account_type', '=', 'income'),
            ('company_id', '=', company.id),
        ], limit=1)
        if not account:
            raise UserError(
                'No income account is configured for company %s. '
                'Please configure one under Accounting settings before generating invoices.'
                % company.name
            )
        return account