from odoo import models

class ReportInventoryFiltrable(models.AbstractModel):
    _name = 'report.it_parc.report_inventory_filtrable_view'
    _description = 'Rapport Inventaire'

    def _get_render_context(self, docids, data=None):
        ctx = dict(data or {})
        if 'category_name' not in ctx:
            ctx['category_name'] = 'Toutes'
        if 'department_name' not in ctx:
            ctx['department_name'] = 'Tous'
        return ctx


class ReportMaintenancePeriod(models.AbstractModel):
    _name = 'report.it_parc.report_maintenance_period_view'
    _description = 'Rapport Maintenance'

    def _get_render_context(self, docids, data=None):
        ctx = dict(data or {})
        if 'date_start' not in ctx:
            ctx['date_start'] = '—'
        if 'date_end' not in ctx:
            ctx['date_end'] = '—'
        if 'total_cost' not in ctx:
            ctx['total_cost'] = 0
        return ctx
