from odoo import api, fields, models

class ItContratRenewWizard(models.TransientModel):
    _name = 'it.contrat.renew.wizard'
    _description = "Assistant de renouvellement de contrat"

    contrat_id = fields.Many2one('it.contrat', string='Contrat', required=True)
    new_date_start = fields.Date(string='Nouvelle date de début', required=True, default=fields.Date.today)
    new_date_end = fields.Date(string='Nouvelle date de fin', required=True)
    new_amount = fields.Float(string='Nouveau montant (FCFA)')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'it.contrat':
            contrat = self.env['it.contrat'].browse(active_id)
            res.update({
                'contrat_id': contrat.id,
                'new_date_start': contrat.date_end,
                'new_amount': contrat.amount,
            })
        return res

    def action_confirm(self):
        self.ensure_one()
        contrat = self.contrat_id
        
        # Log old values for history
        old_start = contrat.date_start
        old_end = contrat.date_end
        old_amount = contrat.amount
        
        contrat.write({
            'date_start': self.new_date_start,
            'date_end': self.new_date_end,
            'amount': self.new_amount,
        })
        
        # Message log in chatter if inherited, otherwise write in log.
        # We will inherit mail.thread on contrat
        if hasattr(contrat, 'message_post'):
            contrat.message_post(body=f"Contrat renouvelé. <br/>"
                                      f"Ancienne période : {old_start} au {old_end} (Montant : {old_amount} FCFA)<br/>"
                                      f"Nouvelle période : {self.new_date_start} au {self.new_date_end} (Montant : {self.new_amount} FCFA)")
        
        return {'type': 'ir.actions.act_window_close'}
