from odoo import api, fields, models

class ItAffectation(models.Model):
    _name = 'it.affectation'
    _description = "Affectation d'équipement informatique"
    _order = 'date_start desc'

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
