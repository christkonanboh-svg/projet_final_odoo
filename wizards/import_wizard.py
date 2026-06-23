import io
import csv
import base64
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError


class ItImportWizard(models.TransientModel):
    _name = 'it.import.wizard'
    _description = "Assistant d'importation CSV d'équipements"

    csv_file = fields.Binary(string='Fichier CSV', required=True)
    csv_filename = fields.Char(string='Nom du fichier')
    report_text = fields.Text(string="Rapport d'importation", readonly=True)

    @staticmethod
    def _parse_date(value):
        """Parse a date string handling multiple formats."""
        if not value or not value.strip():
            return False
        value = value.strip()
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'):
            try:
                return datetime.strptime(value, fmt).date()
            except (ValueError, TypeError):
                continue
        return False

    @staticmethod
    def _detect_delimiter(sample):
        """Auto-detect CSV delimiter using csv.Sniffer, fallback to ';'."""
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=';,|\t')
            return dialect.delimiter
        except csv.Error:
            return ';'

    def action_import(self):
        self.ensure_one()
        if not self.csv_file:
            raise UserError("Veuillez sélectionner un fichier CSV.")

        csv_data = base64.b64decode(self.csv_file)
        try:
            try:
                csv_string = csv_data.decode('utf-8')
            except UnicodeDecodeError:
                csv_string = csv_data.decode('iso-8859-1')
        except Exception as e:
            raise UserError(f"Erreur lors du décodage du fichier : {str(e)}")

        delimiter = self._detect_delimiter(csv_string[:4096])
        reader = csv.reader(io.StringIO(csv_string), delimiter=delimiter)
        header = next(reader, None)
        if not header:
            raise UserError("Le fichier CSV est vide.")
        header_cleaned = [col.strip().lower() for col in header]

        col_name_idx = -1
        col_sn_idx = -1
        col_category_idx = -1
        col_value_idx = -1
        col_date_idx = -1
        col_warranty_idx = -1
        col_location_idx = -1
        col_state_idx = -1
        col_employee_idx = -1
        col_dept_idx = -1

        for idx, col in enumerate(header_cleaned):
            if 'nom' in col or 'designation' in col or 'désignation' in col:
                col_name_idx = idx
            elif 'série' in col or 'serie' in col or 'sn' in col or 'seria' in col:
                col_sn_idx = idx
            elif 'catégorie' in col or 'categorie' in col or 'category' in col:
                col_category_idx = idx
            elif 'valeur' in col or 'prix' in col or 'value' in col or 'price' in col:
                col_value_idx = idx
            elif 'achat' in col or 'purchase' in col:
                col_date_idx = idx
            elif 'garantie' in col or 'warranty' in col:
                col_warranty_idx = idx
            elif 'localisation' in col or 'site' in col or 'location' in col:
                col_location_idx = idx
            elif 'état' in col or 'etat' in col or 'state' in col or 'status' in col:
                col_state_idx = idx
            elif 'employé' in col or 'employe' in col or 'employee' in col:
                col_employee_idx = idx
            elif 'département' in col or 'departement' in col or 'department' in col or 'dept' in col:
                col_dept_idx = idx

        if col_name_idx == -1 or col_sn_idx == -1 or col_category_idx == -1:
            col_name_idx = 0
            col_sn_idx = 1
            col_category_idx = 2
            col_value_idx = 3
            col_date_idx = 4
            col_warranty_idx = 5
            col_location_idx = 6
            col_state_idx = 7
            col_employee_idx = 8
            col_dept_idx = 9

        created_count = 0
        ignored_count = 0
        error_count = 0
        log_lines = []

        row_num = 1
        for row in reader:
            row_num += 1
            if not row or len(row) <= max(col_name_idx, col_sn_idx, col_category_idx):
                continue

            try:
                name = row[col_name_idx].strip() if col_name_idx < len(row) else ''
                sn = row[col_sn_idx].strip() if col_sn_idx < len(row) else ''
                category_name = row[col_category_idx].strip() if col_category_idx < len(row) else ''

                if not name or not sn or not category_name:
                    log_lines.append(f"Ligne {row_num} ignorée : Champs obligatoires manquants (Nom/SN/Catégorie)")
                    error_count += 1
                    continue

                existing = self.env['it.equipement'].search([('serial_number', '=', sn)])
                if existing:
                    log_lines.append(f"Ligne {row_num} ignorée : Équipement avec le S/N '{sn}' existe déjà.")
                    ignored_count += 1
                    continue

                category = self.env['it.equipement.category'].search([('name', '=ilike', category_name)], limit=1)
                if not category:
                    category = self.env['it.equipement.category'].create({'name': category_name})

                purchase_val = 0.0
                if col_value_idx < len(row) and row[col_value_idx].strip():
                    try:
                        purchase_val = float(row[col_value_idx].strip().replace(' ', '').replace(',', '.'))
                    except ValueError:
                        pass

                purchase_date = self._parse_date(row[col_date_idx] if col_date_idx < len(row) else '')
                warranty_date = self._parse_date(row[col_warranty_idx] if col_warranty_idx < len(row) else '')

                location = False
                if col_location_idx < len(row) and row[col_location_idx].strip():
                    loc_name = row[col_location_idx].strip()
                    location = self.env['it.location'].search([('name', '=ilike', loc_name)], limit=1)
                    if not location:
                        location = self.env['it.location'].create({'name': loc_name})

                state_val = 'draft'
                if col_state_idx < len(row) and row[col_state_idx].strip():
                    st = row[col_state_idx].strip().lower()
                    if st in ('affecté', 'affecte', 'assigned', 'affect'):
                        state_val = 'assigned'
                    elif st in ('en maintenance', 'maintenance', 'panne'):
                        state_val = 'maintenance'
                    elif st in ('retiré', 'retire', 'retired', 'rebut'):
                        state_val = 'retired'

                employee = False
                if col_employee_idx < len(row) and row[col_employee_idx].strip():
                    emp_name = row[col_employee_idx].strip()
                    employee = self.env['hr.employee'].search([('name', '=ilike', emp_name)], limit=1)

                department = False
                if col_dept_idx < len(row) and row[col_dept_idx].strip():
                    dept_name = row[col_dept_idx].strip()
                    department = self.env['hr.department'].search([('name', '=ilike', dept_name)], limit=1)

                if employee and not department:
                    department = employee.department_id

                vals = {
                    'name': name,
                    'serial_number': sn,
                    'category_id': category.id,
                    'purchase_value': purchase_val,
                    'purchase_date': purchase_date,
                    'warranty_date': warranty_date,
                    'location_id': location.id if location else False,
                    'state': state_val,
                }

                equip = self.env['it.equipement'].create(vals)

                if employee:
                    equip.write({
                        'employee_id': employee.id,
                        'department_id': department.id if department else False,
                        'state': 'assigned',
                    })
                    self.env['it.affectation'].create({
                        'equipement_id': equip.id,
                        'employee_id': employee.id,
                        'department_id': department.id if department else False,
                        'date_start': purchase_date or fields.Date.today(),
                        'reason': "Importation initiale",
                        'state': 'active',
                    })

                created_count += 1
                log_lines.append(f"Ligne {row_num} insérée : {name} (S/N: {sn})")

            except Exception as ex:
                log_lines.append(f"Ligne {row_num} en erreur : {str(ex)}")
                error_count += 1

        summary = (
            f"--- RAPPORT D'IMPORTATION ---\n"
            f"Fichier : {self.csv_filename or 'Inconnu'}\n"
            f"Créés : {created_count}\n"
            f"Ignorés (doublons) : {ignored_count}\n"
            f"Erreurs : {error_count}\n\n"
            f"Détail du log :\n"
            + "\n".join(log_lines)
        )
        self.write({'report_text': summary})

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
