"""Check that every ORCID publication and every local asset can be reached."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / 'index.html').read_text(encoding='utf-8')
data = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))

class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.papers = [], [], 0
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        self.links += [attrs[key] for key in ('href', 'src') if key in attrs]
        if tag == 'article' and 'publication' in attrs.get('class', '').split():
            self.papers += 1

doc = Document()
doc.feed(html)
assert len(doc.ids) == len(set(doc.ids)), 'Duplicate element IDs'
for link in doc.links:
    if link.startswith('#'):
        assert link[1:] in doc.ids, f'Missing anchor: {link}'
    elif not re.match(r'^[a-z]+:', link):
        assert (ROOT / link).is_file(), f'Missing file: {link}'
assert doc.papers == len(data['publications']) > 0, 'Incomplete publication list'
for paper in data['publications']:
    assert paper['url'] in html, f'Missing publication: {paper["title"]}'
assert len({paper['doi'] or paper['title'] for paper in data['publications']}) == len(data['publications']), 'Duplicate publications'
assert '@article{' in (ROOT / 'publications.bib').read_text(encoding='utf-8')
print(f'Validated assets, navigation, and {doc.papers} unique publications.')
