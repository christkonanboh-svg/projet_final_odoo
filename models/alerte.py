from odoo import api, fields, models
from datetime import timedelta

class ItAlerte(models.Model):
    _name = 'it.alerte'
    _description = "Alerte de garantie / contrat"
    _order = 'date_expiration asc'

    name = fields.Char(string='Sujet', required=True)
    type = fields.Selection([
        ('warranty', 'Garantie Équipement'),
        ('contract', 'Contrat Fournisseur')
    ], string="Type d'alerte", required=True)
    equipement_id = fields.Many2one('it.equipement', string='Équipement', ondelete='cascade')
    contrat_id = fields.Many2one('it.contrat', string='Contrat', ondelete='cascade')
    date_expiration = fields.Date(string="Date d'expiration", required=True)
    days_remaining = fields.Integer(string='Jours restants', compute='_compute_days_remaining_field', store=True)
    state = fields.Selection([
        ('to_treat', 'À traiter'),
        ('treated', 'Traité')
    ], default='to_treat', string='Statut', required=True)

    @api.depends('date_expiration')
    def _compute_days_remaining_field(self):
        today = fields.Date.today()
        for rec in self:
            if rec.date_expiration:
                delta = rec.date_expiration - today
                rec.days_remaining = delta.days
            else:
                rec.days_remaining = 0

    def action_treat(self):
        self.write({'state': 'treated'})

    @api.model
    def cron_scan_expirations(self):
        self._generate_alerts(delay_days=30)

    @api.model
    def _generate_alerts(self, delay_days):
        today = fields.Date.today()
        limit_date = today + timedelta(days=delay_days)
        
        # 1. Scan des équipements
        equipments = self.env['it.equipement'].search([
            ('warranty_date', '!=', False),
            ('warranty_date', '<=', limit_date),
            ('state', '!=', 'retired')
        ])
        for equip in equipments:
            existing = self.search([
                ('type', '=', 'warranty'),
                ('equipement_id', '=', equip.id),
                ('date_expiration', '=', equip.warranty_date),
                ('state', '=', 'to_treat')
            ])
            if not existing:
                days_left = (equip.warranty_date - today).days
                self.create({
                    'name': f"Garantie expirant bientôt : {equip.name} (S/N: {equip.serial_number})",
                    'type': 'warranty',
                    'equipement_id': equip.id,
                    'date_expiration': equip.warranty_date,
                    'state': 'to_treat'
                })

        # 2. Scan des contrats
        contracts = self.env['it.contrat'].search([
            ('date_end', '!=', False),
            ('date_end', '<=', limit_date)
        ])
        for contract in contracts:
            existing = self.search([
                ('type', '=', 'contract'),
                ('contrat_id', '=', contract.id),
                ('date_expiration', '=', contract.date_end),
                ('state', '=', 'to_treat')
            ])
            if not existing:
                days_left = (contract.date_end - today).days
                self.create({
                    'name': f"Contrat expirant bientôt : {contract.name}",
                    'type': 'contract',
                    'contrat_id': contract.id,
                    'date_expiration': contract.date_end,
                    'state': 'to_treat'
                })
        return True
