from odoo import api, fields, models

class ItIntervention(models.Model):
    _name = 'it.intervention'
    _description = "Intervention de maintenance"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(string='Référence', required=True, default='Nouveau', copy=False, readonly=True)
    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True, ondelete='cascade', tracking=True)
    technician_id = fields.Many2one('res.users', string='Technicien', required=True, default=lambda self: self.env.user, tracking=True)
    date_start = fields.Datetime(string='Date de début', required=True, default=fields.Datetime.now, tracking=True)
    date_end = fields.Datetime(string='Date de fin', tracking=True)
    duration = fields.Float(string='Durée (heures)', compute='_compute_duration', store=True)
    cost = fields.Float(string='Coût de maintenance (FCFA)', tracking=True)
    report = fields.Html(string="Rapport d'intervention")
    type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Préventive')
    ], default='corrective', string="Type d'intervention", required=True, tracking=True)

    @api.depends('date_start', 'date_end')
    def _compute_duration(self):
        for rec in self:
            if rec.date_start and rec.date_end:
                diff = rec.date_end - rec.date_start
                rec.duration = diff.total_seconds() / 3600.0
            else:
                rec.duration = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('it.intervention') or 'INT/' + fields.Datetime.now().strftime('%Y%m%d/%H%M%S')
        return super().create(vals_list)
