const tools = document.querySelector('.publication-tools');
const search = document.getElementById('paper-search');
const year = document.getElementById('paper-year');
const papers = [...document.querySelectorAll('.publication')];
const status = document.getElementById('filter-status');
const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function filterPapers() {
  const words = normalize(search.value.trim()).split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const paper of papers) {
    const matches = (year.value === 'all' || paper.dataset.year === year.value) && words.every(word => normalize(paper.dataset.search).includes(word));
    paper.hidden = !matches;
    if (matches) visible++;
  }
  document.getElementById('no-results').hidden = visible !== 0;
  status.textContent = `${visible} ${visible === 1 ? 'publication' : 'publications'} shown.`;
}
tools.hidden = false;
search.addEventListener('input', filterPapers);
year.addEventListener('change', filterPapers);
document.getElementById('clear-filters').addEventListener('click', () => {
  search.value = ''; year.value = 'all'; filterPapers(); search.focus();
});
let toastTimer;
function toast(message) {
  const element = document.getElementById('toast');
  clearTimeout(toastTimer);
  element.textContent = message;
  element.classList.add('visible');
  toastTimer = setTimeout(() => element.classList.remove('visible'), 3500);
}
document.querySelectorAll('.copy-citation').forEach(button => {
  button.addEventListener('click', async () => {
    const citation = button.dataset.citation;
    try {
      await navigator.clipboard.writeText(citation);
      toast('BibTeX citation copied.');
    } catch {
      const dialog = document.getElementById('citation-dialog');
      const field = document.getElementById('citation-text');
      field.value = citation;
      dialog.showModal();
      field.focus(); field.select();
    }
  });
});
document.getElementById('copyright-year').textContent = new Date().getFullYear();
const heroVideo = document.querySelector('.hero-video');
if (heroVideo && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  heroVideo.autoplay = false;
  heroVideo.pause();
}
