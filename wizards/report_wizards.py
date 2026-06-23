from odoo import fields, models

class ItInventoryReportWizard(models.TransientModel):
    _name = 'it.inventory.report.wizard'
    _description = "Assistant de rapport d'inventaire"

    category_id = fields.Many2one('it.equipement.category', string='Catégorie')
    department_id = fields.Many2one('hr.department', string='Département')

    def action_print_pdf(self):
        self.ensure_one()
        domain = []
        if self.category_id:
            domain.append(('category_id', '=', self.category_id.id))
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        equipments = self.env['it.equipement'].search(domain)
        report = self.env.ref('it_parc.action_report_inventory_filtrable')
        return report.report_action(equipments, data={
            'category_name': self.category_id.name or 'Toutes',
            'department_name': self.department_id.name or 'Tous',
        })


class ItMaintenanceReportWizard(models.TransientModel):
    _name = 'it.maintenance.report.wizard'
    _description = "Assistant de rapport des interventions"

    date_start = fields.Date(string='Date de début', required=True, default=fields.Date.today)
    date_end = fields.Date(string='Date de fin', required=True, default=fields.Date.today)

    def action_print_pdf(self):
        self.ensure_one()
        domain = [
            ('date_start', '>=', self.date_start),
            ('date_start', '<=', self.date_end),
        ]
        interventions = self.env['it.intervention'].search(domain)
        total_cost = sum(interv.cost or 0 for interv in interventions)
        report = self.env.ref('it_parc.action_report_maintenance_period')
        return report.report_action(interventions, data={
            'date_start': str(self.date_start),
            'date_end': str(self.date_end),
            'total_cost': total_cost,
        })
