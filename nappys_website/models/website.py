from urllib.parse import urlencode
from odoo import fields, models
from odoo.fields import Domain


class Website(models.Model):
    _inherit = 'website'

    nappys_brand_enabled = fields.Boolean('Nappy’s Minimart storefront', default=False)
    nappys_phone = fields.Char('Store telephone')
    nappys_address = fields.Text('Store address')
    nappys_hours = fields.Text('Opening hours', translate=True)
    nappys_whatsapp = fields.Char('WhatsApp number', help='Full international number, e.g. 18684888332.')

    def _nappys_phone_url(self):
        self.ensure_one()
        return 'tel:' + ''.join(c for c in (self.nappys_phone or '') if c.isdigit() or c == '+')

    def _nappys_whatsapp_url(self):
        self.ensure_one()
        number = ''.join(c for c in (self.nappys_whatsapp or '') if c.isdigit())
        return 'https://wa.me/' + number if number else False

    def _nappys_directions_url(self):
        self.ensure_one()
        return 'https://www.google.com/maps/dir/?' + urlencode({
            'api': '1', 'destination': (self.nappys_address or 'La Romaine, Trinidad and Tobago').replace('\n', ', '),
        })

    def _nappys_map_url(self):
        self.ensure_one()
        return 'https://maps.google.com/maps?' + urlencode({
            'q': (self.nappys_address or 'La Romaine, Trinidad and Tobago').replace('\n', ', '),
            'output': 'embed',
        })

    def _nappys_products(self):
        self.ensure_one()
        Product = self.env['product.template'].with_context(website_id=self.id)
        if not self.nappys_brand_enabled or not self.has_ecommerce_access():
            return Product.browse()
        # Match native shop/company/website rules; never elevate catalogue access.
        return Product.search(Domain.AND([
            self.sale_product_domain(),
            [('active', '=', True), ('is_published', '=', True)],
        ]), order='nappys_featured desc, website_sequence, id desc', limit=8)

    def _nappys_categories(self):
        self.ensure_one()
        Category = self.env['product.public.category'].with_context(website_id=self.id)
        if not self.nappys_brand_enabled or not self.has_ecommerce_access():
            return Category.browse()
        return Category.search(Domain.AND([
            self.website_domain(), [('has_published_products', '=', True)],
        ]), order='sequence, name, id', limit=8)

    def _nappys_category_url(self, xmlid):
        self.ensure_one()
        category = self.env.ref('nappys_website.' + xmlid, raise_if_not_found=False)
        if category:
            # Public record rules hide empty categories. Search before reading fields.
            category = self.env['product.public.category'].with_context(website_id=self.id).search(
                Domain.AND([self.website_domain(), [('id', '=', category.id)]]), limit=1)
        if category:
            return '/shop/category/' + self.env['ir.http']._slug(category)
        return '/shop'
