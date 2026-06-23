from odoo import api, models

class ReportInventoryFiltrable(models.AbstractModel):
    _name = 'report.it_parc.report_inventory_filtrable_view'
    _description = 'Parser pour Rapport Inventaire Filtrable'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        category_id = data.get('category_id')
        department_id = data.get('department_id')

        domain = []
        if category_id:
            domain.append(('category_id', '=', category_id))
        if department_id:
            domain.append(('department_id', '=', department_id))

        docs = self.env['it.equipement'].search(domain)
        
        category_name = self.env['it.equipement.category'].browse(category_id).name if category_id else "Toutes"
        department_name = self.env['hr.department'].browse(department_id).name if department_id else "Tous"

        return {
            'doc_ids': docids,
            'doc_model': 'it.equipement',
            'docs': docs,
            'category_name': category_name,
            'department_name': department_name,
        }


class ReportMaintenancePeriod(models.AbstractModel):
    _name = 'report.it_parc.report_maintenance_period_view'
    _description = 'Parser pour Rapport Maintenance Période'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        date_start = data.get('date_start')
        date_end = data.get('date_end')

        domain = []
        if date_start:
            domain.append(('date_start', '>=', date_start))
        if date_end:
            domain.append(('date_start', '<=', date_end))

        docs = self.env['it.intervention'].search(domain)
        
        total_cost = sum(docs.mapped('cost'))

        return {
            'doc_ids': docids,
            'doc_model': 'it.intervention',
            'docs': docs,
            'date_start': date_start,
            'date_end': date_end,
            'total_cost': total_cost,
        }
