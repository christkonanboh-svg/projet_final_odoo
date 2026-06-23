from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    it_equipement_ids = fields.One2many('it.equipement', 'invoice_id', string='Équipements IT')
    it_equipement_count = fields.Integer(string="Nombre d'équipements", compute='_compute_it_equipement_count')

    @api.depends('it_equipement_ids')
    def _compute_it_equipement_count(self):
        for rec in self:
            rec.it_equipement_count = len(rec.it_equipement_ids)

    def action_open_it_equipements(self):
        self.ensure_one()
        return {
            'name': f'Équipements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'it.equipement',
            'view_mode': 'list,form',
            'domain': [('invoice_id', '=', self.id)],
            'context': {'default_invoice_id': self.id},
        }
