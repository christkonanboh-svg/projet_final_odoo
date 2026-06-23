import json
from datetime import date, timedelta
from collections import defaultdict

from odoo import http
from odoo.http import request
from odoo.tools.date_utils import relativedelta


class ItParcDashboardController(http.Controller):

    @http.route('/it_parc/dashboard_data', type='json', auth='user')
    def dashboard_data(self, **kwargs):
        env = request.env

        # ── KPI 1 : Nombre total d'équipements ──────────────────
        total = env['it.equipement'].search_count([])

        # ── KPI 2 : Équipements disponibles / affectés ──────────
        assigned = env['it.equipement'].search_count([('state', '=', 'assigned')])

        # ── KPI 3 : Équipements en maintenance ───────────────────
        in_maintenance = env['it.equipement'].search_count([('state', '=', 'maintenance')])

        # ── KPI 4 : Contrats en alerte (< 60 jours) ──────────────
        today = date.today()
        limit = today + timedelta(days=60)
        contracts_alert = env['it.contrat'].search_count([
            ('date_end', '<=', str(limit))
        ])

        # ── KPI 5 : Coût total des interventions de l'année ─────
        year_start = date(today.year, 1, 1)
        year_interventions = env['it.intervention'].search([
            ('date_start', '>=', str(year_start))
        ])
        total_cost_year = sum(year_interventions.mapped('cost'))

        # ── KPI 6 : Alertes à traiter ───────────────────────────
        alerts_pending = env['it.alerte'].search_count([('state', '=', 'to_treat')])

        # ── Graphique : Coûts de maintenance par mois (12 derniers mois) ──
        monthly_costs = defaultdict(float)
        months_labels = []
        for i in range(11, -1, -1):
            m = today - relativedelta(months=i)
            key = m.strftime('%Y-%m')
            months_labels.append(m.strftime('%b %Y'))
            monthly_costs[key] = 0.0

        all_interventions = env['it.intervention'].search([
            ('date_start', '>=', str(today - relativedelta(months=11)))
        ])
        for interv in all_interventions:
            if interv.date_start:
                key = interv.date_start.strftime('%Y-%m')
                if key in monthly_costs:
                    monthly_costs[key] += interv.cost

        chart_labels = months_labels
        chart_values = [monthly_costs[k] for k in sorted(monthly_costs.keys())]

        # ── Graphique camembert : Répartition par catégorie ─────
        categories = env['it.equipement.category'].search([])
        cat_labels = []
        cat_values = []
        for cat in categories:
            count = env['it.equipement'].search_count([('category_id', '=', cat.id)])
            if count > 0:
                cat_labels.append(cat.name)
                cat_values.append(count)

        return {
            'kpis': {
                'total': total,
                'assigned': assigned,
                'in_maintenance': in_maintenance,
                'contracts_alert': contracts_alert,
                'total_cost_year': total_cost_year,
                'alerts_pending': alerts_pending,
            },
            'chart_maintenance': {
                'labels': chart_labels,
                'values': chart_values,
            },
            'chart_categories': {
                'labels': cat_labels,
                'values': cat_values,
            }
        }
