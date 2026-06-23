from odoo import models

class ReportInventoryReport(models.AbstractModel):
    _name = 'report.it_parc.report_inventory_filtrable_view'
    _description = 'Rapport inventaire'

    def _get_render_context(self, docids, data=None):
        ctx = super()._get_render_context(docids, data=data)
        wizard = self.env['it.inventory.report.wizard'].browse(docids[0]) if docids else None
        if wizard:
            domain = []
            if wizard.category_id:
                domain.append(('category_id', '=', wizard.category_id.id))
            if wizard.department_id:
                domain.append(('department_id', '=', wizard.department_id.id))
            equipements = self.env['it.equipement'].search(domain)
            ctx['docs'] = equipements
            ctx['category_name'] = wizard.category_id.name or 'Toutes'
            ctx['department_name'] = wizard.department_id.name or 'Tous'
        return ctx


class ReportMaintenanceReport(models.AbstractModel):
    _name = 'report.it_parc.report_maintenance_period_view'
    _description = 'Rapport maintenances'

    def _get_render_context(self, docids, data=None):
        ctx = super()._get_render_context(docids, data=data)
        wizard = self.env['it.maintenance.report.wizard'].browse(docids[0]) if docids else None
        if wizard:
            domain = [('date_start', '>=', wizard.date_start), ('date_start', '<=', wizard.date_end)]
            interventions = self.env['it.intervention'].search(domain)
            ctx['docs'] = interventions
            ctx['date_start'] = wizard.date_start
            ctx['date_end'] = wizard.date_end
            ctx['total_cost'] = sum(interv.cost or 0 for interv in interventions)
        return ctx
