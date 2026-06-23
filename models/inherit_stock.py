from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    it_equipement_ids = fields.One2many('it.equipement', 'product_id', string='Équipements IT')
    it_equipement_count = fields.Integer(string="Nombre d'équipements", compute='_compute_it_equipement_count')

    @api.depends('it_equipement_ids')
    def _compute_it_equipement_count(self):
        for rec in self:
            rec.it_equipement_count = len(rec.it_equipement_ids)

    def action_open_it_equipements(self):
        self.ensure_one()
        product_ids = self.env['product.product'].search([('product_tmpl_id', '=', self.id)]).ids
        equipements = self.env['it.equipement'].search([('product_id', 'in', product_ids)])
        return {
            'name': f'Équipements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'it.equipement',
            'view_mode': 'list,form',
            'domain': [('id', 'in', equipements.ids)],
            'context': {'default_product_id': product_ids[0] if product_ids else False},
        }
