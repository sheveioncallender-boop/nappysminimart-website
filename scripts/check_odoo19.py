#!/usr/bin/env python3
"""Validate inherited architectures using an Odoo 19 checkout (no database).
Usage: python scripts/check_odoo19.py /path/to/odoo
This does not replace installation/HTTP tests on an Odoo database.
"""
from copy import deepcopy
from pathlib import Path
import sys
from lxml import etree

source = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(source))
from odoo.tools.template_inheritance import apply_inheritance_specs
from odoo.addons.base.models import ir_ui_view  # registers Odoo XPath functions

root = Path(__file__).resolve().parents[1]
modules = [source / 'addons' / name for name in
           ['web', 'portal', 'website', 'website_sale', 'base_setup', 'product']]
modules += [source / 'odoo/addons/base', root / 'nappys_website']
views = {}
for module in modules:
    for path in (module / 'views').glob('*.xml'):
        doc = etree.parse(str(path))
        for element in doc.xpath('//template[@id] | //record[@model="ir.ui.view"]'):
            xmlid = element.get('id')
            if '.' not in xmlid:
                xmlid = module.name + '.' + xmlid
            if element.tag == 'template':
                parent = element.get('inherit_id')
                arch = etree.Element('data' if parent else 't')
                arch.extend(deepcopy(list(element)))
            else:
                parent_nodes = element.xpath('./field[@name="inherit_id"]')
                parent = parent_nodes[0].get('ref') if parent_nodes else None
                arches = element.xpath('./field[@name="arch"]')
                if not arches:
                    continue
                children = list(arches[0])
                if len(children) == 1:
                    arch = deepcopy(children[0])
                else:
                    arch = etree.Element('data'); arch.extend(deepcopy(children))
            if parent and '.' not in parent:
                parent = module.name + '.' + parent
            views[xmlid] = (parent, arch)

def resolve(xmlid):
    parent, arch = views[xmlid]
    return apply_inheritance_specs(resolve(parent), deepcopy(arch)) if parent else deepcopy(arch)

for xmlid in views:
    if xmlid.startswith('nappys_website.') and views[xmlid][0]:
        resolve(xmlid)
        print('PASS inherited view:', xmlid)
# Verify t-call targets, XML IDs and Python method names against the actual source.
known = set(views)
for path in (root/'nappys_website/data').glob('*.xml'):
    known.update('nappys_website.'+x for x in etree.parse(str(path)).xpath('//@id'))
for path in (root/'nappys_website').rglob('*.xml'):
    doc=etree.parse(str(path))
    for target in doc.xpath('//@t-call'):
        assert target in known, (path, target)
for path, method in [('website_sale/models/website.py','has_ecommerce_access'),
                     ('website_sale/models/website.py','sale_product_domain'),
                     ('website_sale/models/product_template.py','_get_sales_prices'),
                     ('website/models/website_page.py','_allow_to_use_cache'),
                     ('website/models/website_page.py','_get_page_info')]:
    assert 'def '+method+'(' in (source/'addons'/path).read_text(), method
print('PASS Odoo 19 view inheritance, template calls and commerce method references.')
