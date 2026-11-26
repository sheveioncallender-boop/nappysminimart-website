from lxml import html
from odoo.tests import HttpCase, tagged
from odoo.addons.website_sale.tests.common import MockRequest
from ..hooks import post_init_hook


@tagged('post_install', '-at_install', 'nappys_website')
class TestNappysWebsite(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env.ref('website.default_website')
        cls.website.write({'domain': False, 'ecommerce_access': 'everyone'})
        cls.category = cls.env.ref('nappys_website.category_pantry')
        cls.product = cls.env['product.template'].create({
            'name': 'TEST Pantry Rice 1kg', 'type': 'consu', 'list_price': 125,
            'sale_ok': True, 'is_published': True, 'website_id': cls.website.id,
            'taxes_id': [(5, 0, 0)],
            'public_categ_ids': [(6, 0, [cls.category.id])],
        })

    def home(self):
        response = self.url_open('/', timeout=90)
        self.assertEqual(response.status_code, 200, response.text[:1000])
        return html.fromstring(response.content)

    def test_publication_and_private_catalogue(self):
        self.env['product.template'].search([('is_published', '=', True)]).write({'is_published': False})
        self.assertFalse(self.home().xpath('//article[@class="nm-product"]'))
        self.product.is_published = True
        cards = self.home().xpath('//article[@class="nm-product"]')
        self.assertEqual(len(cards), 1)
        self.assertIn(self.product.name, cards[0].text_content())
        self.product.is_published = False
        self.assertFalse(self.home().xpath('//article[@class="nm-product"]'))
        self.product.is_published = True
        self.website.ecommerce_access = 'logged_in'
        self.assertFalse(self.home().xpath('//article[@class="nm-product"]'))

    def test_pages_contact_and_native_shop(self):
        for route in ['/', '/departments', '/about-nappys', '/visit-nappys', '/contactus', '/shop', self.product.website_url]:
            with self.subTest(route=route):
                response = self.url_open(route, timeout=90)
                self.assertEqual(response.status_code, 200, response.text[:1000])
                document = html.fromstring(response.content)
                self.assertEqual(len(document.xpath('//header[@id="top"]')), 1)
                self.assertTrue(document.xpath('//header//a[@href="/shop/cart"]'))
                self.assertTrue(document.xpath('//header//a[@href="tel:+18684888332"]'))
                self.assertIn('Developed by Spxcorp Limited.', document.text_content())
                self.assertTrue(document.xpath('//footer//img[contains(@src,"nappys-logo.png")]'))
        contact = html.fromstring(self.url_open('/visit-nappys').content)
        self.assertTrue(contact.xpath('//a[@href="https://wa.me/18684888332"]'))
        self.assertTrue(contact.xpath('//iframe[contains(@src,"La+Romaine")]'))
        self.assertTrue(contact.xpath('//a[contains(@href,"maps/dir/")]'))

    def test_native_cart_and_checkout(self):
        self.url_open('/')
        cart = self.make_jsonrpc_request('/shop/cart/add', {
            'product_template_id': self.product.id,
            'product_id': self.product.product_variant_id.id, 'quantity': 2,
        }, timeout=90)
        self.assertEqual(cart['quantity'], 2)
        response = self.url_open('/shop/cart', timeout=90)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product.name, html.fromstring(response.content).text_content())
        checkout = self.url_open('/shop/checkout', timeout=90)
        self.assertEqual(checkout.status_code, 200)
        self.assertNotIn('Traceback', checkout.text)

    def test_rules_and_archive(self):
        public = self.website.with_user(self.website.user_id).with_context(website_id=self.website.id)
        with MockRequest(public.env, website=public):
            self.assertIn(self.product, public._nappys_products())
            self.product.active = False
            self.assertNotIn(self.product, public._nappys_products())
            self.product.active = True
            self.product.sale_ok = False
            self.assertNotIn(self.product, public._nappys_products())
            self.product.sale_ok = True
        other = self.env['website'].create({'name': 'Other website', 'company_id': self.website.company_id.id, 'nappys_brand_enabled': True})
        other_public = other.with_user(other.user_id).with_context(website_id=other.id)
        with MockRequest(other_public.env, website=other_public):
            self.assertNotIn(self.product, other_public._nappys_products())
            self.assertNotIn(self.category, other_public._nappys_categories())

    def test_setup_is_idempotent_and_contact_is_editable(self):
        self.website.nappys_phone = '+1 868 555-0100'
        self.website.nappys_hours = 'Monday to Friday: 9am–5pm'
        self.product.list_price = 155
        count = self.env['website.menu'].search_count([('website_id', '=', self.website.id)])
        post_init_hook(self.env)
        self.assertEqual(self.website.nappys_phone, '+1 868 555-0100')
        self.assertEqual(self.product.list_price, 155)
        self.assertEqual(self.env['website.menu'].search_count([('website_id', '=', self.website.id)]), count)
        page = html.fromstring(self.url_open('/visit-nappys', timeout=90).content)
        self.assertTrue(page.xpath('//a[@href="tel:+18685550100"]'))
        self.assertIn('Monday to Friday', page.text_content())
