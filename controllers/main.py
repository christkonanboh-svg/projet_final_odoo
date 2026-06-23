import io
import base64
from datetime import date, timedelta

from odoo import http
from odoo.http import request, content_disposition

try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None


class ItParcExcelController(http.Controller):

    def _get_workbook_styles(self, workbook):
        """Définit les styles réutilisables."""
        styles = {}
        styles['header'] = workbook.add_format({
            'bold': True, 'bg_color': '#1e3a5f', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True
        })
        styles['title'] = workbook.add_format({
            'bold': True, 'font_size': 14, 'font_color': '#1e3a5f'
        })
        styles['subtitle'] = workbook.add_format({
            'italic': True, 'font_color': '#555555', 'font_size': 10
        })
        styles['normal'] = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        styles['normal_center'] = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        styles['number'] = workbook.add_format({'border': 1, 'num_format': '#,##0', 'align': 'right'})
        styles['total'] = workbook.add_format({'bold': True, 'bg_color': '#e8f0fe', 'border': 1, 'num_format': '#,##0'})
        styles['total_label'] = workbook.add_format({'bold': True, 'bg_color': '#e8f0fe', 'border': 1, 'align': 'right'})
        styles['red_bg'] = workbook.add_format({'bg_color': '#f8d7da', 'font_color': '#721c24', 'border': 1, 'bold': True})
        styles['orange_bg'] = workbook.add_format({'bg_color': '#fff3cd', 'font_color': '#856404', 'border': 1})
        styles['green_bg'] = workbook.add_format({'bg_color': '#d4edda', 'font_color': '#155724', 'border': 1})
        styles['date'] = workbook.add_format({'border': 1, 'num_format': 'dd/mm/yyyy', 'align': 'center'})
        return styles

    # ─────────────────────────────────────────────────────────────
    # EXPORT 1 : Inventaire complet
    # ─────────────────────────────────────────────────────────────
    @http.route('/it_parc/export/inventaire', type='http', auth='user')
    def export_inventaire(self, **kwargs):
        if not xlsxwriter:
            return request.make_response("Bibliothèque xlsxwriter non disponible.", headers=[('Content-Type', 'text/plain')])

        equipements = request.env['it.equipement'].search_read(
            [], ['name', 'serial_number', 'category_id', 'location_id', 'employee_id',
                 'department_id', 'purchase_value', 'purchase_date', 'warranty_date', 'state', 'description']
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet("Inventaire")
        styles = self._get_workbook_styles(workbook)

        ws.write(0, 0, "INVENTAIRE DU PARC INFORMATIQUE - TECHPARK CI", styles['title'])
        ws.write(1, 0, f"Généré le {date.today().strftime('%d/%m/%Y')}", styles['subtitle'])
        ws.write(2, 0, f"Nombre total d'équipements : {len(equipements)}", styles['subtitle'])

        headers = ['#', 'Désignation', 'N° Série', 'Catégorie', 'Site/Localisation',
                   'Employé', 'Département', "Valeur d'achat (FCFA)", "Date d'achat",
                   'Fin de Garantie', 'État', 'Description']
        col_widths = [5, 30, 20, 20, 20, 25, 20, 20, 15, 15, 15, 40]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ws.write(4, col, header, styles['header'])
            ws.set_column(col, col, width)

        state_labels = {
            'draft': 'Brouillon', 'assigned': 'Affecté',
            'maintenance': 'En maintenance', 'retired': 'Retiré'
        }
        total_value = 0
        for i, eq in enumerate(equipements):
            row = 5 + i
            total_value += eq.get('purchase_value', 0) or 0
            ws.write(row, 0, i + 1, styles['normal_center'])
            ws.write(row, 1, eq.get('name', ''), styles['normal'])
            ws.write(row, 2, eq.get('serial_number', ''), styles['normal'])
            ws.write(row, 3, eq['category_id'][1] if eq.get('category_id') else '—', styles['normal'])
            ws.write(row, 4, eq['location_id'][1] if eq.get('location_id') else '—', styles['normal'])
            ws.write(row, 5, eq['employee_id'][1] if eq.get('employee_id') else '—', styles['normal'])
            ws.write(row, 6, eq['department_id'][1] if eq.get('department_id') else '—', styles['normal'])
            ws.write(row, 7, eq.get('purchase_value', 0) or 0, styles['number'])
            ws.write(row, 8, str(eq['purchase_date']) if eq.get('purchase_date') else '—', styles['normal_center'])
            ws.write(row, 9, str(eq['warranty_date']) if eq.get('warranty_date') else '—', styles['normal_center'])
            ws.write(row, 10, state_labels.get(eq.get('state', ''), eq.get('state', '')), styles['normal_center'])
            ws.write(row, 11, eq.get('description', '') or '', styles['normal'])

        total_row = 5 + len(equipements)
        ws.write(total_row, 6, "VALEUR TOTALE DU PARC :", styles['total_label'])
        ws.write(total_row, 7, total_value, styles['total'])

        workbook.close()
        output.seek(0)
        filename = f"inventaire_parc_{date.today().strftime('%Y%m%d')}.xlsx"
        headers_list = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', content_disposition(filename)),
        ]
        return request.make_response(output.read(), headers=headers_list)

    # ─────────────────────────────────────────────────────────────
    # EXPORT 2 : Coûts de maintenance par équipement et par mois
    # ─────────────────────────────────────────────────────────────
    @http.route('/it_parc/export/couts_maintenance', type='http', auth='user')
    def export_couts_maintenance(self, **kwargs):
        if not xlsxwriter:
            return request.make_response("xlsxwriter non disponible.", headers=[('Content-Type', 'text/plain')])

        interventions = request.env['it.intervention'].search([], order='equipement_id, date_start')

        from collections import defaultdict
        costs_by_equip_month = defaultdict(lambda: defaultdict(float))
        months_set = set()
        equip_names = {}

        for interv in interventions:
            if interv.equipement_id and interv.date_start:
                eq_id = interv.equipement_id.id
                equip_names[eq_id] = interv.equipement_id.name
                month_key = interv.date_start.strftime('%Y-%m')
                months_set.add(month_key)
                costs_by_equip_month[eq_id][month_key] += interv.cost

        months = sorted(list(months_set))
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet("Coûts Maintenance")
        styles = self._get_workbook_styles(workbook)

        ws.write(0, 0, "SYNTHÈSE DES COÛTS DE MAINTENANCE PAR ÉQUIPEMENT ET PAR MOIS", styles['title'])
        ws.write(1, 0, f"Généré le {date.today().strftime('%d/%m/%Y')}", styles['subtitle'])

        ws.write(3, 0, "Équipement", styles['header'])
        ws.set_column(0, 0, 35)
        for j, month in enumerate(months):
            ws.write(3, 1 + j, month, styles['header'])
            ws.set_column(1 + j, 1 + j, 16)
        ws.write(3, 1 + len(months), "TOTAL (FCFA)", styles['header'])
        ws.set_column(1 + len(months), 1 + len(months), 18)

        for i, (eq_id, eq_name) in enumerate(equip_names.items()):
            row = 4 + i
            ws.write(row, 0, eq_name, styles['normal'])
            row_total = 0
            for j, month in enumerate(months):
                cost = costs_by_equip_month[eq_id].get(month, 0)
                row_total += cost
                ws.write(row, 1 + j, cost, styles['number'])
            ws.write(row, 1 + len(months), row_total, styles['total'])

        total_row = 4 + len(equip_names)
        ws.write(total_row, 0, "TOTAL PAR MOIS", styles['total_label'])
        grand_total = 0
        for j, month in enumerate(months):
            col_total = sum(costs_by_equip_month[eq_id].get(month, 0) for eq_id in equip_names)
            grand_total += col_total
            ws.write(total_row, 1 + j, col_total, styles['total'])
        ws.write(total_row, 1 + len(months), grand_total, styles['total'])

        workbook.close()
        output.seek(0)
        filename = f"couts_maintenance_{date.today().strftime('%Y%m%d')}.xlsx"
        headers_list = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', content_disposition(filename)),
        ]
        return request.make_response(output.read(), headers=headers_list)

    # ─────────────────────────────────────────────────────────────
    # EXPORT 3 : Contrats expirant dans 60 jours (couleurs cond.)
    # ─────────────────────────────────────────────────────────────
    @http.route('/it_parc/export/contrats_expirant', type='http', auth='user')
    def export_contrats_expirant(self, **kwargs):
        if not xlsxwriter:
            return request.make_response("xlsxwriter non disponible.", headers=[('Content-Type', 'text/plain')])

        today = date.today()
        limit = today + timedelta(days=60)
        contrats = request.env['it.contrat'].search([('date_end', '<=', limit)])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        ws = workbook.add_worksheet("Contrats expirant")
        styles = self._get_workbook_styles(workbook)

        ws.write(0, 0, "CONTRATS EXPIRANT DANS LES 60 PROCHAINS JOURS", styles['title'])
        ws.write(1, 0, f"Généré le {today.strftime('%d/%m/%Y')}", styles['subtitle'])

        headers = ['Référence', 'Fournisseur', 'Date début', 'Date fin', 'Montant (FCFA)', 'Jours restants', 'Statut']
        col_widths = [30, 30, 15, 15, 20, 16, 20]
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ws.write(3, col, header, styles['header'])
            ws.set_column(col, col, width)

        for i, contrat in enumerate(contrats):
            row = 4 + i
            days_left = (contrat.date_end - today).days
            if days_left < 0:
                row_style = styles['red_bg']
                status = "EXPIRÉ"
            elif days_left <= 30:
                row_style = styles['red_bg']
                status = "URGENT (< 30j)"
            elif days_left <= 60:
                row_style = styles['orange_bg']
                status = "Bientôt (< 60j)"
            else:
                row_style = styles['green_bg']
                status = "OK"

            ws.write(row, 0, contrat.name, row_style)
            ws.write(row, 1, contrat.partner_id.name if contrat.partner_id else '—', row_style)
            ws.write(row, 2, str(contrat.date_start), row_style)
            ws.write(row, 3, str(contrat.date_end), row_style)
            ws.write(row, 4, contrat.amount, row_style)
            ws.write(row, 5, days_left, row_style)
            ws.write(row, 6, status, row_style)

        workbook.close()
        output.seek(0)
        filename = f"contrats_expirant_{today.strftime('%Y%m%d')}.xlsx"
        headers_list = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', content_disposition(filename)),
        ]
        return request.make_response(output.read(), headers=headers_list)

    # ─────────────────────────────────────────────────────────────
    # EXPORT 4 : Fichier CSV modèle pour l'import
    # ─────────────────────────────────────────────────────────────
    @http.route('/it_parc/export/sample_csv', type='http', auth='user')
    def export_sample_csv(self, **kwargs):
        import csv
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(['Nom', 'Numero de Serie', 'Categorie', 'Valeur',
                         'Date Achat', 'Garantie', 'Localisation', 'Etat', 'Employe', 'Departement'])
        writer.writerow(['Ordinateur Dell G15', 'SN123456', 'Ordinateur portable', '450000',
                         '2026-01-15', '2028-01-15', 'Abidjan-Cocody', 'Affecte', 'Konan Boh Christ', 'IT'])
        writer.writerow(['Ecran Dell 27"', 'SN789012', 'Ecran', '250000',
                         '2025-06-01', '2027-06-01', 'Abidjan-Cocody', 'Affecte', 'Konan Boh Christ', 'IT'])
        writer.writerow(['Imprimante HP LaserJet', 'SN345678', 'Imprimante', '350000',
                         '2024-03-15', '2026-03-15', 'Abidjan-Treichville', 'Brouillon', '', ''])
        output.seek(0)
        filename = "modele_import_equipements.csv"
        headers_list = [
            ('Content-Type', 'text/csv; charset=utf-8'),
            ('Content-Disposition', content_disposition(filename)),
        ]
        return request.make_response(output.getvalue(), headers=headers_list)
