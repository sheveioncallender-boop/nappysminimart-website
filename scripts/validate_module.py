#!/usr/bin/env python3
"""Offline structural checks; Odoo HTTP tests live in nappys_website/tests."""
import ast
from pathlib import Path
from lxml import etree

root = Path(__file__).resolve().parents[1]
module = root / 'nappys_website'
manifest = ast.literal_eval((module / '__manifest__.py').read_text())
assert manifest['version'].startswith('19.0.')
assert manifest['depends'] == ['website_sale', 'point_of_sale']
for path in module.rglob('*.py'):
    ast.parse(path.read_text(), filename=str(path))
for path in module.rglob('*.xml'):
    tree = etree.parse(str(path))
    for value in tree.xpath('//@src | //@file'):
        if value.startswith('/nappys_website/'):
            assert (root / value.lstrip('/')).is_file(), (path, value)
        elif value.startswith('nappys_website/'):
            assert (root / value).is_file(), (path, value)
for value in manifest['data']:
    assert (module / value).is_file(), value
for bundle in manifest['assets'].values():
    for value in bundle:
        path = value[-1] if isinstance(value, tuple) else value
        assert (root / path).is_file(), path
try:
    import sass
except ImportError:
    print('SCSS compilation skipped: libsass is not installed in this interpreter.')
else:
    for path in (module / 'static/src/css').glob('*.scss'):
        sass.compile(filename=str(path))
    print('SCSS compilation passed.')
print('Python, XML, local asset paths and Odoo 19 manifest checks passed.')
