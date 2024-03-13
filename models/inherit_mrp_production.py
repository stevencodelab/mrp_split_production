from odoo import _, models, fields
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_capacity = fields.Float(compute='_compute_production_capacity', help="Quantity that can be produced with the current stock of components")

    def action_open_workorder_split(self):
        # Lakukan logika apa pun yang diperlukan sebelum membuka form pemisahan work order
        # Misalnya, Anda dapat memvalidasi apakah produksi memiliki work order yang bisa dipecah
        # Jika validasi berhasil, buka form pemisahan work order
        return {
            'name': 'Split Work Order',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.workorder.split',
            'view_mode': 'form',
            'target': 'new',
        }