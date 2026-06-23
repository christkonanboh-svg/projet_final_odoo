from odoo import fields, models, api

class ItInventoryReportWizard(models.TransientModel):
    _name = 'it.inventory.report.wizard'
    _description = "Assistant de rapport d'inventaire"

    category_id = fields.Many2one('it.equipement.category', string='Catégorie')
    department_id = fields.Many2one('hr.department', string='Département')

    def action_print_pdf(self):
        self.ensure_one()
        data = {
            'category_id': self.category_id.id,
            'department_id': self.department_id.id,
        }
        return self.env.ref('it_parc.action_report_inventory_filtrable').report_action(self, data=data)


class ItMaintenanceReportWizard(models.TransientModel):
    _name = 'it.maintenance.report.wizard'
    _description = "Assistant de rapport des interventions"

    date_start = fields.Date(string='Date de début', required=True, default=fields.Date.today)
    date_end = fields.Date(string='Date de fin', required=True, default=fields.Date.today)

    def action_print_pdf(self):
        self.ensure_one()
        data = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        return self.env.ref('it_parc.action_report_maintenance_period').report_action(self, data=data)
