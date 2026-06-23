from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ItEquipementCategory(models.Model):
    _name = 'it.equipement.category'
    _description = "Catégorie d'équipement informatique"
    _order = 'name'

    name = fields.Char(string='Nom de la catégorie', required=True)
    description = fields.Text(string='Description')
    equipement_ids = fields.One2many('it.equipement', 'category_id', string='Équipements')

    _sql_constraints = [
        ('unique_category_name', 'UNIQUE(name)', 'Le nom de la catégorie doit être unique.')
    ]


class ItLocation(models.Model):
    _name = 'it.location'
    _description = "Localisation physique de l'équipement"
    _order = 'name'

    name = fields.Char(string='Nom du site', required=True)
    address = fields.Char(string='Adresse')
    equipement_ids = fields.One2many('it.equipement', 'location_id', string='Équipements')

    _sql_constraints = [
        ('unique_location_name', 'UNIQUE(name)', 'Le nom du site doit être unique.')
    ]


class ItEquipement(models.Model):
    _name = 'it.equipement'
    _description = "Équipement informatique"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Désignation', required=True, tracking=True)
    serial_number = fields.Char(string='Numéro de série', required=True, tracking=True)
    category_id = fields.Many2one('it.equipement.category', string='Catégorie', required=True, tracking=True)
    location_id = fields.Many2one('it.location', string='Localisation/Site', tracking=True)
    purchase_value = fields.Float(string="Valeur d'achat (FCFA)", tracking=True)
    purchase_date = fields.Date(string="Date d'achat", tracking=True)
    warranty_date = fields.Date(string="Date de fin de garantie", tracking=True)
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('assigned', 'Affecté'),
        ('maintenance', 'En maintenance'),
        ('retired', 'Retiré')
    ], default='draft', string='État', tracking=True, required=True)

    employee_id = fields.Many2one('hr.employee', string='Employé actuel', tracking=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Département actuel', tracking=True, readonly=True)
    description = fields.Text(string='Description technique')
    
    affectation_ids = fields.One2many('it.affectation', 'equipement_id', string='Historique des affectations')
    intervention_ids = fields.One2many('it.intervention', 'equipement_id', string='Interventions')
    contrat_ids = fields.Many2many('it.contrat', 'it_equipement_contrat_rel', 'equipement_id', 'contrat_id', string='Contrats')

    _sql_constraints = [
        ('unique_serial_number', 'UNIQUE(serial_number)', 'Le numéro de série doit être unique.')
    ]

    @api.constrains('purchase_value')
    def _check_purchase_value(self):
        for rec in self:
            if rec.purchase_value < 0:
                raise ValidationError("La valeur d'achat ne peut pas être négative.")

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_assign(self):
        self.write({'state': 'assigned'})

    def action_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_retire(self):
        self.write({'state': 'retired'})
