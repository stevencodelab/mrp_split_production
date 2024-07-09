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
    # quantity_to_split = fields.Integer(string='Split Quantity ??', compute="_compute_counter",store=True, readonly=False)
    production_detailed_vals_ids = fields.One2many('mrp.production.split.line', 'mrp_production_split_id','Split Details', compute="_compute_details", store=True, readonly=False)
    valid_details = fields.Boolean("Valid", compute="_compute_valid_details")
    quantity_per_workorder = fields.Float(string='Quantity per Work Order', required=True)
        
    """  action_split_workorder :
        1. Initialization:
            a. Inisialisasi list kosong new_workorders untuk menyimpan ID dari work order baru yang dibuat.

        2. Splitting Work Orders:
            a. Melakukan iterasi melalui self.production_detailed_vals_ids.
            b. Untuk setiap baris detail, membuat nama baru untuk work order yang dipisah dengan menambahkan indeks ke nama produksi asli.
            c. Membuat work order baru dengan menyalin self.production_id, tetapi dengan nama baru dan kuantitas produksi sesuai dengan detail yang dihitung.
            d. Menambahkan ID work order baru ke list new_workorders.
        
        3. Adjusting Original Production:
            a. Membatalkan production order asli dengan memanggil self.production_id.action_cancel().
        
        4. Returning Result:
            a. Mengembalikan action untuk menampilkan tree view dari work order baru yang dibuat.
            b. Domain diatur untuk hanya menampilkan work order baru (menggunakan ID dalam new_workorders).

    Perubahan utama pada function ini adalah sebagai berikut :
    - Tidak lagi menggunakan self.quantity_to_split untuk menentukan jumlah iterasi.
    - Kuantitas untuk setiap work order baru diambil dari production_detailed_vals_ids, yang dihitung berdasarkan quantity_per_workorder.
    - Production order asli dibatalkan setelah pemisahan, bukan hanya mengurangi kuantitasnya.
    - Tidak ada lagi perhitungan qty_per_workorder di dalam method ini, karena sudah dihitung di _compute_details.
    """
    
    def action_split_workorder(self):
        new_workorders = []
        for line in self.production_detailed_vals_ids:
            new_name = f"{self.production_id.name} - {len(new_workorders) + 1:04d}"
            new_workorder = self.production_id.copy(default={
                'name': new_name,
                'product_qty': line.quantity,
                'qty_producing': 0,
            })
            new_workorders.append(new_workorder.id)
        
        self.production_id.action_cancel()
        
        return {
            'name': 'Manufacturing Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', new_workorders)],
            'target': 'current',
        }
    
    # Action Counter Split Number
    @api.depends('production_detailed_vals_ids')
    def _compute_counter(self):
        for wizard in self:
            wizard.quantity_to_split = len(wizard.production_detailed_vals_ids)

            
    @api.depends('product_qty', 'quantity_per_workorder')
    def _compute_details(self):
        for wizard in self:
            commands = []
            if wizard.quantity_per_workorder <= 0 or not wizard.production_id:
                wizard.production_detailed_vals_ids = commands
                continue
            
            full_workorders = int(wizard.product_qty // wizard.quantity_per_workorder)
            remaining_quantity = wizard.product_qty % wizard.quantity_per_workorder
            
            for _ in range(full_workorders):
                commands.append((0, 0, {
                    'quantity': wizard.quantity_per_workorder,
                    'user_id': wizard.production_id.user_id.id,
                    'date': wizard.production_id.date_start,
                }))
            
            if remaining_quantity > 0:
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
    production_id=fields.Many2one('mrp.production', 'Manufacturing Order')
    product_id=fields.Many2one(related='production_id.product_id')