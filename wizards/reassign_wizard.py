from odoo import api, fields, models

class ItReassignWizard(models.TransientModel):
    _name = 'it.reassign.wizard'
    _description = "Assistant de réaffectation d'équipement"

    equipement_id = fields.Many2one('it.equipement', string='Équipement', required=True)
    employee_id = fields.Many2one('hr.employee', string='Nouvel Employé', required=True)
    department_id = fields.Many2one('hr.department', string='Nouveau Département', required=True)
    reason = fields.Text(string='Motif de réaffectation', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('active_model') == 'it.equipement':
            equip = self.env['it.equipement'].browse(active_id)
            res.update({
                'equipement_id': equip.id,
                'employee_id': equip.employee_id.id,
                'department_id': equip.department_id.id,
            })
        return res

    def action_confirm(self):
        self.ensure_one()
        equip = self.equipement_id
        
        # 1. Clôturer l'affectation active en cours
        active_assignments = self.env['it.affectation'].search([
            ('equipement_id', '=', equip.id),
            ('state', '=', 'active')
        ])
        active_assignments.write({
            'date_end': fields.Date.today(),
            'state': 'completed'
        })

        # 2. Créer la nouvelle affectation active
        self.env['it.affectation'].create({
            'equipement_id': equip.id,
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'date_start': fields.Date.today(),
            'reason': self.reason,
            'state': 'active'
        })

        # 3. Mettre à jour l'équipement
        equip.write({
            'employee_id': self.employee_id.id,
            'department_id': self.department_id.id,
            'state': 'assigned'
        })

        # 4. Message dans le chatter
        equip.message_post(body=f"Équipement réaffecté à <b>{self.employee_id.name}</b> (Département : {self.department_id.name}).<br/>Motif : {self.reason}")
        return {'type': 'ir.actions.act_window_close'}
