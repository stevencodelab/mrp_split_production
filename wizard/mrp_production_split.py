from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime

class MrpWorkorderSplit(models.TransientModel):
    _name = 'mrp.production.split'
    _description = 'Split Work Order'
    
    production_split_multi_id = fields.Many2one('mrp.production.split.multi', 'Split Productions')
    production_id = fields.Many2one('mrp.production', 'Manufacturing Order')
    product_id = fields.Many2one(related='production_id.product_id')
    product_qty = fields.Float(related='production_id.product_qty')
    product_uom_id = fields.Many2one(related='production_id.product_uom_id')
    production_capacity = fields.Float(related='production_id.production_capacity')
    quantity_to_split = fields.Integer(string='Split WO Into', default=0, compute="_compute_counter",store=True, readonly=False)
    production_detailed_vals_ids = fields.One2many('mrp.production.split.line', 'mrp_production_split_id','Split Details', compute="_compute_details", store=True, readonly=False)
    valid_details = fields.Boolean("Valid", compute="_compute_valid_details")

    # Action Tombol Split
    def action_split_workorder(self):
        new_workorders = []
        total_qty_to_produce = self.production_id.product_qty  # Total jumlah yang akan diproduksi
        for i in range(int(self.quantity_to_split)):
            new_name = f"{self.production_id.name} - {i + 1:04d}"
            new_workorder = self.production_id.copy(default={'name': new_name, 'qty_producing': 1})
            new_workorders.append(new_workorder.id)
        self.production_id.qty_producing -= self.quantity_to_split
        
        # Perbarui nilai product_qty pada setiap Work Order hasil split
        qty_per_workorder = total_qty_to_produce / self.quantity_to_split
        for new_workorder in self.env['mrp.production'].browse(new_workorders):
            new_workorder.product_qty = qty_per_workorder

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'res_id': new_workorders,
            'target': 'current',
        }


    # Action Counter Split Number
    @api.depends('production_detailed_vals_ids')
    def _compute_counter(self):
        for wizard in self:
            wizard.quantity_to_split = len(wizard.production_detailed_vals_ids)

    # Compute menampilkan details ke dalam notebook
    @api.depends('quantity_to_split')
    def _compute_details(self):
        for wizard in self:
            commands = []
            if wizard.quantity_to_split < 1 or not wizard.production_id:
                wizard.production_detailed_vals_ids = commands
                continue
            quantity = float_round(wizard.product_qty / wizard.quantity_to_split, precision_rounding=wizard.product_uom_id.rounding)
            remaining_quantity = wizard.product_qty
            for _ in range(wizard.quantity_to_split - 1):
                commands.append((0, 0, {
                    'quantity': quantity,
                    'user_id': wizard.production_id.user_id.id,
                    'date': wizard.production_id.date_start,
                }))
                remaining_quantity = float_round(remaining_quantity - quantity, precision_rounding=wizard.product_uom_id.rounding)
            commands.append((0, 0, {
                'quantity': remaining_quantity,
                'user_id': wizard.production_id.user_id.id,
                'date': wizard.production_id.date_start,
            }))
            wizard.production_detailed_vals_ids = commands


    @api.depends('production_detailed_vals_ids')
    def _compute_valid_details(self):
        self.valid_details = False
        for wizard in self:
            if wizard.production_detailed_vals_ids:
                wizard.valid_details = float_compare(wizard.product_qty, sum(wizard.production_detailed_vals_ids.mapped('quantity')), precision_rounding=wizard.product_uom_id.rounding) == 0   

class MrpProductionSplitMulti(models.TransientModel):
    _name = 'mrp.production.split.multi'
    _description = "Wizard to Split Multiple Productions"

    production_ids = fields.One2many('mrp.production.split', 'production_split_multi_id', 'Productions To Split')
    
class MrpProductionSplitLine(models.TransientModel):
    _name='mrp.production.split.line'
    _description='Mrp Production Split Line'    
    
    mrp_production_split_id = fields.Many2one( 'mrp.production.split', 'Split Production', required=True, ondelete="cascade")
    quantity = fields.Float('Quantity To Produce', digits='Product Unit of Measure', required=True)
    user_id = fields.Many2one('res.users', 'Responsible',domain=lambda self: [('groups_id', 'in', self.env.ref('mrp.group_mrp_user').id)])
    date = fields.Datetime('Schedule Date')
      