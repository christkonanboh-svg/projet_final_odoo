from datetime import timedelta
from odoo import api, fields, models

class ItContrat(models.Model):
    _name = 'it.contrat'
    _description = "Contrat de maintenance / licence"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end asc'

    name = fields.Char(string='Référence du contrat', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Fournisseur', required=True, tracking=True)
    date_start = fields.Date(string='Date de début', required=True, default=fields.Date.today, tracking=True)
    date_end = fields.Date(string='Date de fin', required=True, tracking=True)
    amount = fields.Float(string='Montant du contrat (FCFA)', tracking=True)
    equipement_ids = fields.Many2many('it.equipement', 'it_equipement_contrat_rel', 'contrat_id', 'equipement_id', string='Équipements couverts')
    days_remaining = fields.Integer(string='Jours restants', compute='_compute_days_remaining', search='_search_days_remaining')

    @api.depends('date_end')
    def _compute_days_remaining(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_end:
                delta = rec.date_end - today
                rec.days_remaining = delta.days
            else:
                rec.days_remaining = 0

    def _search_days_remaining(self, operator, value):
        today = fields.Date.today()
        target_date = today + timedelta(days=value)
        return [('date_end', operator, target_date)]
