import { chromium } from 'playwright';

// The source document is already authored for A4 print. Injected here: pagination
// behaviour that only matters when the page actually breaks.
const PRINT = `
html,body{ background:#fff !important; }
table{ break-inside:auto !important; page-break-inside:auto !important; }
thead{ display:table-header-group; }
tr{ break-inside:avoid; page-break-inside:avoid; }
.card,.callout,.viz{ break-inside:avoid; page-break-inside:avoid; }
.split{ break-inside:avoid; }
/* keep a section heading with the text that follows it */
.sec-head, h3{ break-after:avoid !important; page-break-after:avoid !important; }
.sec-head + p, h3 + p, h3 + table{ break-before:avoid !important; page-break-before:avoid !important; }
footer{ margin-top:3mm !important; }
.srclist li{ margin-bottom:.6mm !important; }
ol,ul{ break-inside:auto; }
li{ break-inside:avoid; }
`;

const OUT = '/home/user/Outreach/my-project/research/pilot-corpus.pdf';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const p = await b.newPage({ colorScheme: 'light' });
await p.goto('file:///home/user/Outreach/my-project/research/pilot-corpus.html', { waitUntil: 'networkidle' });
await p.addStyleTag({ content: PRINT });
await p.waitForTimeout(2500);

// Chromium ignores break-before/after:avoid here, so headings are physically
// wrapped together with the block that follows them.
await p.evaluate(() => {
  const keep = (el, limit) => {
    const next = el.nextElementSibling;
    if (!next) return;
    if (el.offsetHeight + next.offsetHeight > limit) return;
    const box = document.createElement('div');
    box.style.breakInside = 'avoid';
    box.style.pageBreakInside = 'avoid';
    el.parentNode.insertBefore(box, el);
    box.appendChild(el); box.appendChild(next);
  };
  // section heading + its lead paragraph; a long table after the head keeps flowing
  document.querySelectorAll('.sec-head').forEach(el => keep(el, 320));
  // sub-heading + the table it introduces
  document.querySelectorAll('section > h3').forEach(el => keep(el, 700));
});
console.log((await p.evaluate(async () => {
  await document.fonts.ready;
  return ['Newsreader', 'IBM Plex Sans', 'IBM Plex Mono'].map(f => `${f}:${document.fonts.check(`12px "${f}"`)}`);
})).join(' '));
await p.pdf({
  path: OUT,
  format: 'A4', printBackground: true, displayHeaderFooter: true,
  headerTemplate: '<div></div>',
  footerTemplate: `<div style="width:100%;font-family:'IBM Plex Mono',monospace;font-size:7pt;color:#767F7A;padding:0 15mm;display:flex;justify-content:space-between;">
    <span>Пилот на 200 тысяч · Animaccord · август 2026</span>
    <span class="pageNumber"></span></div>`,
  margin: { top: '16mm', bottom: '18mm', left: '15mm', right: '15mm' }
});
await b.close();
