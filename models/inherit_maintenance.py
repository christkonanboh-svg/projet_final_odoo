from odoo import api, fields, models


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    it_intervention_id = fields.Many2one('it.intervention', string='Intervention IT Parc', ondelete='set null')

    def action_open_it_intervention(self):
        self.ensure_one()
        if not self.it_intervention_id:
            return
        return {
            'name': self.it_intervention_id.name,
            'type': 'ir.actions.act_window',
            'res_model': 'it.intervention',
            'view_mode': 'form',
            'res_id': self.it_intervention_id.id,
        }
