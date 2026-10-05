# João Francisco Shida — academic website

Personal research website for **https://jfshida.github.io/**. Plain HTML, CSS, and JavaScript: no framework, package installation, or paid hosting required.

## Content

- Biography and affiliation: [Peng Lab team](https://www.sampenglab.org/team).
- Publications: [ORCID 0000-0002-7333-3274](https://orcid.org/0000-0002-7333-3274).
- Front-page microscopy video and U2OS microtubule image supplied by João Francisco Shida. The video is presented in its original aspect ratio with its 2 μm scale bar, muted playback, and player controls. The image caption records AF647–anti-α-tubulin labeling and a FWHM of 100 nm.
- Contact links: ORCID, GitHub, and the public LinkedIn profile. No inferred email address is used.

## Updating the website

Edit `index.html` to change the biography, research descriptions, or links. Edit `styles.css` to change the appearance. Keep the HTML comments around generated publication fields intact.

Run `python scripts/sync_orcid.py` to refresh publications from your public ORCID record. This updates `data/publications.json`, the publication section in `index.html`, and `publications.bib`. ORCID work groups and DOI identifiers prevent duplicate records. Only public data is accessed; no ORCID credentials are needed.

The GitHub Pages workflow refreshes ORCID on every push and each Monday at 09:17 UTC, then publishes the resulting static page. If ORCID is temporarily unavailable, the last committed publication list remains available. Scheduled workflows may be delayed or disabled by GitHub after repository inactivity; a push or manual workflow run refreshes the site again. New works must be made public in ORCID to appear here. Affiliation and biography are intentionally edited manually.

## Preview and validation

Run `python -m http.server 8765` in this directory, then visit `http://localhost:8765`. Run `python scripts/validate.py` to check publication coverage and local links. Search and year filters use JavaScript; all papers and links remain readable with JavaScript disabled. Citation buttons copy BibTeX, with a copyable dialog if clipboard permission is unavailable.

## GitHub Pages

The repository must be named `jfshida.github.io` under the `jfshida` GitHub account. In **Settings → Pages**, choose **GitHub Actions** as the source. The included workflow publishes the site after a push to `main`.
