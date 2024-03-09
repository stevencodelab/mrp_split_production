from odoo import _, models, fields
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    production_capacity = fields.Float(compute='_compute_production_capacity', help="Quantity that can be produced with the current stock of components")

    def action_split(self):
        productions = self.production_id._split_productions({self.production_id: [detail.quantity for detail in self.production_detailed_vals_ids]})
        for production, detail in zip(productions, self.production_detailed_vals_ids):
            production.user_id = detail.user_id
            production.date_start = detail.date
        if self.production_split_multi_id:
            saved_production_split_multi_id = self.production_split_multi_id.id
            self.production_split_multi_id.production_ids = [Command.unlink(self.id)]
            action = self.env['ir.actions.actions']._for_xml_id('mrp.action_mrp_production_split_multi')
            action['res_id'] = saved_production_split_multi_id
            return action

    def _pre_action_split_merge_hook(self, merge=False, split=False):
        if not merge and not split:
            return True
        ope_str = merge and _('merged') or _('split')
        if any(production.state not in ('draft', 'confirmed') for production in self):
            raise UserError(_("Only manufacturing orders in either a draft or confirmed state can be %s.", ope_str))
        if any(not production.bom_id for production in self):
            raise UserError(_("Only manufacturing orders with a Bill of Materials can be %s.", ope_str))
        if split:
            return True

        if len(self) < 2:
            raise UserError(_("You need at least two production orders to merge them."))
        products = set([(production.product_id, production.bom_id) for production in self])
        if len(products) > 1:
            raise UserError(_('You can only merge manufacturing orders of identical products with same BoM.'))
        additional_raw_ids = self.mapped("move_raw_ids").filtered(lambda move: not move.bom_line_id)
        additional_byproduct_ids = self.mapped('move_byproduct_ids').filtered(lambda move: not move.byproduct_id)
        if additional_raw_ids or additional_byproduct_ids:
            raise UserError(_("You can only merge manufacturing orders with no additional components or by-products."))
        if len(set(self.mapped('state'))) > 1:
            raise UserError(_("You can only merge manufacturing with the same state."))
        if len(set(self.mapped('picking_type_id'))) > 1:
            raise UserError(_('You can only merge manufacturing with the same operation type'))
        # TODO explode and check no quantity has been edited
        return True        