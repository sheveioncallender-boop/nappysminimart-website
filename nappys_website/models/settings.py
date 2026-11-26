from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    nappys_brand_enabled = fields.Boolean(related='website_id.nappys_brand_enabled', readonly=False)
    nappys_phone = fields.Char(related='website_id.nappys_phone', readonly=False)
    nappys_address = fields.Text(related='website_id.nappys_address', readonly=False)
    nappys_hours = fields.Text(related='website_id.nappys_hours', readonly=False)
    nappys_whatsapp = fields.Char(related='website_id.nappys_whatsapp', readonly=False)
