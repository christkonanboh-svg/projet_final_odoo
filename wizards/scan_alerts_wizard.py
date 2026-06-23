from odoo import api, fields, models

class ItScanAlertsWizard(models.TransientModel):
    _name = 'it.scan.alerts.wizard'
    _description = "Assistant de scan manuel des alertes"

    delay_days = fields.Integer(string='Délai de détection (jours)', default=30, required=True)

    def action_confirm(self):
        self.ensure_one()
        self.env['it.alerte']._generate_alerts(self.delay_days)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Scan terminé',
                'message': f"Le scan des équipements et contrats expirant sous {self.delay_days} jours a été exécuté.",
                'type': 'success',
                'sticky': False,
            }
        }
