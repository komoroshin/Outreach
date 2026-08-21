import { chromium } from 'playwright';
const PRINT = `
@page { size: A4; margin: 14mm 12mm 16mm; }
html,body{ background:#fff !important; }
body{ font-size:9pt !important; line-height:1.5 !important; }
.wrap{ max-width:none !important; padding:0 !important; }
.col,.wide{ max-width:none !important; }
/* scroll containers clip in print — must be visible */
.tscroll{ overflow:visible !important; border:.6pt solid var(--rule) !important; margin:4mm 0 !important; }
table{ min-width:0 !important; width:100% !important; font-size:6.6pt !important; table-layout:auto !important; }
th,td{ padding:1.1mm 1.4mm !important; overflow-wrap:break-word; word-break:normal; hyphens:none; }
.pill{ white-space:normal !important; display:inline-block; font-size:5.9pt !important; }
.tag-d{ white-space:normal !important; }
thead th{ position:static !important; letter-spacing:.04em !important; }
caption{ font-size:6.8pt !important; padding:1.6mm !important; }
h1{ font-size:21pt !important; }
h2{ font-size:13.5pt !important; }
h3{ font-size:10.5pt !important; }
section{ padding:5mm 0 !important; break-inside:auto; }
.masthead{ padding:0 0 5mm !important; }
.sec-head{ margin-bottom:3.5mm !important; break-after:avoid; }
.thesis{ padding:6mm 5mm !important; margin:4mm 0 !important; break-inside:avoid; }
.thesis-a{ font-size:13pt !important; }
.thesis-q{ font-size:10pt !important; }
.finding,.callout,.viz,.scen-card,.check,.factgrid,.toc{ break-inside:avoid; }
.finding{ padding:3.5mm 4mm !important; }
.callout{ padding:3mm 3.5mm !important; margin:3.5mm 0 !important; }
.viz{ padding:4mm !important; margin:4mm 0 !important; }
.scen-card{ padding:4mm !important; }
.scen-formula{ white-space:normal !important; font-size:7.6pt !important; }
.meta div,.toc a{ padding:2.4mm 2.8mm !important; }
.bar-row{ margin-bottom:2mm !important; }
.bar-track{ height:7mm !important; }
p{ margin-bottom:2.4mm !important; }
/* gap+background grids bleed their fill to the page bottom when items paginate */
.findings,.scen{ background:transparent !important; border:none !important; gap:0 !important; }
.finding,.scen-card{ border:.6pt solid var(--rule) !important; margin-bottom:3mm !important; }
`;
const b = await chromium.launch({ executablePath:'/opt/pw-browsers/chromium' });
const p = await b.newPage({ colorScheme:'light' });
await p.goto('file:///home/user/Outreach/my-project/research/animaccord-business-model-v2.html', { waitUntil:'networkidle' });
await p.addStyleTag({ content: PRINT });
await p.waitForTimeout(2500);
console.log((await p.evaluate(async()=>{await document.fonts.ready;
  return ['Newsreader','IBM Plex Sans','IBM Plex Mono'].map(f=>`${f}:${document.fonts.check(`12px "${f}"`)}`)})).join(' '));
await p.pdf({
  path:'/home/user/Outreach/my-project/research/animaccord-business-model-v2.pdf',
  format:'A4', printBackground:true, displayHeaderFooter:true,
  headerTemplate:'<div></div>',
  footerTemplate:`<div style="width:100%;font-family:'IBM Plex Mono',monospace;font-size:7pt;color:#767F7A;padding:0 12mm;display:flex;justify-content:space-between;">
    <span>Лицензируемый слой персонажа · v2 · Animaccord · август 2026</span>
    <span class="pageNumber"></span></div>`,
  margin:{ top:'14mm', bottom:'16mm', left:'12mm', right:'12mm' }
});
await b.close();
