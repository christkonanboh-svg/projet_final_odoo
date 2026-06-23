from odoo import api, fields, models

class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = "Affectation d'équipement informatique"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'
    _rec_name = 'display_name'

    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True)
    department_id = fields.Many2one('hr.department', string='Département', required=True)
    date_start = fields.Date(string='Date de début', default=fields.Date.today, required=True)
    date_end = fields.Date(string='Date de fin')
    reason = fields.Text(string="Motif d'affectation")
    state = fields.Selection([
        ('active', 'Actif'),
        ('completed', 'Terminé')
    ], default='active', string='Statut', required=True)

    display_name = fields.Char(string='Affectation', compute='_compute_display_name', store=True)

    @api.depends('equipement_id', 'employee_id', 'date_start')
    def _compute_display_name(self):
        for rec in self:
            parts = []
            if rec.equipement_id:
                parts.append(rec.equipement_id.name)
            if rec.employee_id:
                parts.append(rec.employee_id.name)
            if rec.date_start:
                parts.append(str(rec.date_start))
            rec.display_name = ' - '.join(parts) if parts else f"Affectation #{rec.id}"
