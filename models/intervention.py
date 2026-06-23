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
    maintenance_request_id = fields.Many2one('maintenance.request', string='Demande de maintenance', ondelete='set null', tracking=True)
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
        records = super().create(vals_list)
        for rec in records:
            if rec.equipement_id and rec.equipement_id.state in ('draft', 'assigned'):
                rec.equipement_id.write({'state': 'maintenance'})
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'date_end' in vals or 'state' in vals:
            for rec in self:
                if rec.date_end and rec.equipement_id and rec.equipement_id.state == 'maintenance':
                    active_aff = self.env['it.affectation'].search([
                        ('equipement_id', '=', rec.equipement_id.id),
                        ('state', '=', 'active'),
                    ], limit=1)
                    rec.equipement_id.write({
                        'state': 'assigned' if active_aff else 'draft',
                    })
        return res
