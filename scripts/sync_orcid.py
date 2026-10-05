"""Refresh public publications from ORCID; keep the site buildless and portable."""
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ORCID = "0000-0002-7333-3274"
API = f"https://pub.orcid.org/v3.0/{ORCID}"


def fetch(path):
    for attempt in range(3):
        try:
            request = Request(API + path, headers={"Accept": "application/json", "User-Agent": "JFShidaAcademicWebsite/1.0"})
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def value(obj):
    return (obj or {}).get("value", "") or ""


def doi_from(work):
    for identifier in work.get("external-ids", {}).get("external-id", []):
        if identifier.get("external-id-type", "").lower() == "doi":
            doi = identifier.get("external-id-value", "").strip()
            doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.I)
            return doi
    return ""


def refresh():
    groups = fetch("/works").get("group", [])
    publications, seen = [], set()
    for group in groups:
        summaries = group.get("work-summary", [])
        if not summaries:
            continue
        summary = max(summaries, key=lambda item: int(item.get("display-index", 0)))
        work = fetch(f"/work/{summary['put-code']}")
        title = value(work.get("title", {}).get("title"))
        doi = doi_from(work)
        key = doi.lower() or title.casefold()
        if not title or key in seen:
            continue
        seen.add(key)
        date = work.get("publication-date") or {}
        year = value(date.get("year"))
        authors = [value(item.get("credit-name")) for item in (work.get("contributors") or {}).get("contributor", [])]
        authors = [name for name in authors if name]
        url = f"https://doi.org/{doi}" if doi else f"https://orcid.org/{ORCID}"
        publications.append({"title": title, "journal": value(work.get("journal-title")), "year": year,
                             "date": "-".join(filter(None, [year, value(date.get("month")), value(date.get("day"))])),
                             "authors": authors, "doi": doi, "url": url, "putCode": work["put-code"],
                             "type": work.get("type", "work")})
    if not publications:
        raise RuntimeError("ORCID returned no works; the existing site has been preserved.")
    publications.sort(key=lambda work: work["date"], reverse=True)
    data = {"orcid": ORCID, "source": f"https://orcid.org/{ORCID}",
            "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "publications": publications}
    render(data)
    (ROOT / "data/publications.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {len(publications)} distinct publications from ORCID.")


def author_html(name):
    escaped = escape(name)
    return f"<strong>{escaped}</strong>" if "shida" in name.casefold() else escaped


def render(data):
    publications = data["publications"]
    entries = []
    bibtex = []
    for index, paper in enumerate(publications):
        authors = "; ".join(author_html(name) for name in paper["authors"])
        if not authors:
            authors = 'Contributor details available in the <a href="https://orcid.org/' + ORCID + '">ORCID record</a>.'
        key = f"shida{paper['year']}_{index + 1}"
        bib = f"@article{{{key},\n  title = {{{paper['title']}}},\n  author = {{{' and '.join(paper['authors'])}}},\n  journal = {{{paper['journal']}}},\n  year = {{{paper['year']}}},\n  doi = {{{paper['doi']}}},\n  url = {{{paper['url']}}}\n}}"
        bibtex.append(bib)
        search = escape(" ".join([paper["title"], paper["journal"], paper["year"], " ".join(paper["authors"])]), quote=True)
        entries.append(f'''<article class="publication" data-year="{escape(paper['year'])}" data-search="{search}">
          <div class="paper-year">{escape(paper['year'] or '—')}</div>
          <div class="paper-body"><div class="paper-journal">{escape(paper['journal'] or paper['type'].replace('-', ' ').title())}</div>
          <h3><a href="{escape(paper['url'], quote=True)}">{escape(paper['title'])}<span aria-hidden="true" class="paper-arrow">↗</span></a></h3>
          <p class="authors">{authors}</p>
          <div class="paper-actions"><a href="{escape(paper['url'], quote=True)}">Read paper <span aria-hidden="true">↗</span></a>
          <a href="https://orcid.org/{ORCID}">ORCID record <span aria-hidden="true">↗</span></a>
          <button type="button" class="copy-citation" data-citation="{escape(bib, quote=True)}">Copy BibTeX</button></div></div></article>''')
    years = sorted({paper["year"] for paper in publications if paper["year"]}, reverse=True)
    options = '<option value="all">All years</option>' + ''.join(f'<option value="{escape(year)}">{escape(year)}</option>' for year in years)
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")
    replacements = {"PUBLICATIONS": "\n".join(entries), "YEAR_OPTIONS": options,
                    "PUB_COUNT": str(len(publications)), "UPDATED": data["updated"]}
    for marker, content in replacements.items():
        pattern = rf"(<!-- {marker}:START -->).*?(<!-- {marker}:END -->)"
        html, matches = re.subn(pattern, lambda match: match[1] + content + match[2], html, flags=re.S)
        if not matches:
            raise RuntimeError(f"Missing HTML marker: {marker}")
    path.write_text(html, encoding="utf-8")
    (ROOT / "publications.bib").write_text("\n\n".join(bibtex) + "\n", encoding="utf-8")


if __name__ == "__main__":
    refresh()
