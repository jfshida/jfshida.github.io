"""Check that every ORCID publication and every local asset can be reached."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

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
        self.links += [attrs[key] for key in ('href', 'src', 'poster') if key in attrs]
        if tag == 'article' and 'publication' in attrs.get('class', '').split():
            self.papers += 1

documents = {}
for path in ROOT.rglob('*.html'):
    parsed = Document()
    parsed.feed(path.read_text(encoding='utf-8'))
    assert len(parsed.ids) == len(set(parsed.ids)), f'Duplicate element IDs: {path}'
    documents[path.resolve()] = parsed
for path, parsed in documents.items():
    for link in parsed.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if target.is_dir():
            target = target / 'index.html'
        assert target.is_file(), f'Missing local target: {link} in {path.name}'
        if url.fragment and target in documents:
            assert url.fragment in documents[target].ids, f'Missing anchor: {link}'
doc = documents[(ROOT / 'index.html').resolve()]
assert doc.papers == len(data['publications']) > 0, 'Incomplete publication list'
for paper in data['publications']:
    assert paper['url'] in html, f'Missing publication: {paper["title"]}'
assert len({paper['doi'] or paper['title'] for paper in data['publications']}) == len(data['publications']), 'Duplicate publications'
assert '@article{' in (ROOT / 'publications.bib').read_text(encoding='utf-8')
print(f'Validated assets, navigation, and {doc.papers} unique publications.')
