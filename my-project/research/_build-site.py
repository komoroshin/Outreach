#!/usr/bin/env python3
"""Собирает сайт из четырёх исследовательских документов.

Источник правды остаётся здесь, в my-project/research/*.html: скрипт вынимает из
каждого файла заголовок, стили и содержимое и заворачивает их в общую оболочку
из _site-assets/.

Опубликован сайт в соседнем репозитории komoroshin/research, подпапка animaccord/,
откуда его отдаёт GitHub Pages. Туда же ведёт путь сборки по умолчанию:

    python3 my-project/research/_build-site.py

Другое место назначения — через --out; для подпапки чужого репозитория добавьте
--subdir, чтобы не создавать лишний .nojekyll:

    python3 my-project/research/_build-site.py --out /путь/site --subdir
"""
import argparse, re, shutil
from pathlib import Path
from html import escape

SRC = Path(__file__).resolve().parent
# По умолчанию — подпапка в соседнем клоне komoroshin/research.
OUT = SRC.parents[2] / "research" / "animaccord"
ROOT_SITE = False  # в корне сайта нужен .nojekyll, в подпапке — нет

# family: 'screen' — документ свёрстан под экран и уже отзывчив;
#         'print'  — документ свёрстан под A4 и требует экранного слоя.
DOCS = [
    dict(slug="01-market", src="animaccord-ai-device.html", family="screen",
         num="01", nav="Обзор рынка", title="Обзор рынка",
         sub="Каталог детских AI-девайсов",
         desc="Что есть на рынке: 33 продукта с ценами, носителями контента, подписками "
              "и механикой работы. Описание без выводов — материал, на который опираются "
              "остальные три документа.",
         chips=["Карта категорий", "Цены", "AI-компаньоны", "Раскрытая экономика", "Регуляторика"],
         size="12 разделов · 33 продукта", pdf=None),
    dict(slug="02-platform", src="platform-layer.html", family="print",
         num="02", nav="Платформы", title="Платформенный слой",
         sub="Из чего собирают такие устройства",
         desc="Восемь поставщиков, на которых держится категория: платформа, речевые модели, "
              "модули, чипы и контрактные фабрики. Что из этого берётся готовым и на каких условиях.",
         chips=["Tuya Smart", "Volcano Engine / Doubao", "Espressif", "Чиповый слой", "Контрактные фабрики"],
         size="9 страниц · 8 поставщиков", pdf="platform-layer.pdf"),
    dict(slug="03-character-layer", src="animaccord-business-model-v2.html", family="screen",
         num="03", nav="Слой персонажа", title="Лицензируемый слой персонажа",
         sub="Предмет разработки и его экономика",
         desc="Главный документ: что именно строится вокруг устройства, почему ядром становится "
              "персонаж, а не железо, как Россия работает референсной установкой и во что "
              "обходится каждая фаза.",
         chips=["Экономика категории", "Российский контур", "Сценарии", "Предмет разработки", "Гипотезы"],
         size="16 разделов · 24 страницы", pdf="animaccord-business-model-v2.pdf"),
    dict(slug="04-investor-inputs", src="investor-inputs.html", family="print",
         num="04", nav="Вводные", title="Вводные для инвестпакета",
         sub="Цифры, формы и карта ответов",
         desc="Опорные цифры под сборку инвестиционного пакета: демография, сопоставимые сделки "
              "и выходы, публичный ориентир оценки, экономика подписки. Плюс формы под то, "
              "что заполняется данными компании.",
         chips=["Демография", "Сопоставимые сделки", "Экономика подписки", "Формы", "Карта ответов"],
         size="11 разделов · 10 страниц", pdf="investor-inputs.pdf"),
]

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
    'family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600'
    '&subset=cyrillic&display=swap">'
)

# Скин: документы приносят собственную палитру, здесь она переопределяется на систему
# сайта — только для экрана, поэтому PDF собираются из исходников без изменений.
SKIN_COMMON = """
@media screen{
  h1,h2,h3,h4,.thesis-q,.thesis-a,.factgrid dd{
    font-family:'IBM Plex Sans',-apple-system,'Segoe UI',Roboto,sans-serif }
  .thesis-q{ font-style:normal }
  a{ color:var(--accent) }
  thead th{ position:static }
  /* тень на краю показывает, что таблицу можно листать вбок */
  .tscroll,.tbl{
    background:
      linear-gradient(to right, var(--app-paper), rgba(243,240,232,0)) 0 0/28px 100% no-repeat local,
      linear-gradient(to left, var(--app-paper), rgba(243,240,232,0)) 100% 0/28px 100% no-repeat local,
      radial-gradient(farthest-side at 0 50%, rgba(17,17,17,.16), rgba(17,17,17,0)) 0 0/12px 100% no-repeat scroll,
      radial-gradient(farthest-side at 100% 50%, rgba(17,17,17,.16), rgba(17,17,17,0)) 100% 0/12px 100% no-repeat scroll;
  }
}
"""

SKIN_PRINT_VARS = """
  --ink:#111111; --ink-2:#3A3E42; --ink-3:#6B7075;
  --paper:#F3F0E8; --tint:rgba(107,112,117,.08);
  --rule:rgba(107,112,117,.32); --rule-2:#111111;
  --accent:#245BFF; --warn:#8A6410; --neg:#9B2C1F;
"""

SKIN_SCREEN_VARS = """
  --paper:#E7E3D7; --surface:#F3F0E8; --surface-2:#EDE9DE;
  --ink:#111111; --ink-2:#3A3E42; --ink-3:#6B7075;
  --rule:rgba(107,112,117,.32); --rule-strong:#111111;
  --accent:#245BFF; --thesis-bg:#111111; --thesis-fg:#F3F0E8;
  --pos:#1E6B45; --warn:#8A6410; --neg:#9B2C1F;
  --pos-bg:#E6EDE7; --warn-bg:#F1EBDA; --neg-bg:#F2E5E1;
  --shadow:0 1px 0 rgba(17,17,17,.14);
"""


def skin(varblock: str) -> str:
    """Палитра сайта поверх палитры документа, в светлой и тёмной среде одинаково."""
    return (SKIN_COMMON
            + "@media screen{ :root{" + varblock + "} }\n"
            + "@media screen and (prefers-color-scheme:dark){"
            "  :root:not([data-theme=\"light\"]){" + varblock + "} }\n")


# Экранный слой для документов, свёрстанных под A4: лист на столе,
# пропорциональное укрупнение pt-шрифтов и горизонтальная прокрутка таблиц.
ADAPT_PRINT = """
@media screen{
  html,body{ background:var(--app-desk) }
  .doc{ zoom:1.2 }
  .sheet{ max-width:196mm; margin:9mm auto 17mm; padding:15mm 14mm 18mm }
  .tbl{ overflow-x:auto; margin:0 0 1mm }
  .tbl table{ min-width:34rem }
  .srclist a{ overflow-wrap:anywhere }
  .sec-num{ font-weight:600 }
  .cover{ border-bottom:1px solid var(--ink) }
}
@media screen and (max-width:820px){
  .doc{ zoom:1.06 }
  .sheet{ margin:0; padding:22px 16px 34px; border-left:0; border-right:0; box-shadow:none }
  .meta{ grid-template-columns:repeat(2,1fr) }
  .meta div:nth-child(2n){ border-right:0 }
  .split,.spec{ grid-template-columns:1fr }
  .card-top{ flex-direction:column; align-items:flex-start; gap:6px }
  .card-top .who{ text-align:left; white-space:normal }
  .legend-row{ gap:3mm }
}
"""

# Экранные документы отзывчивы сами; им нужен лист и поправка под шапку.
ADAPT_SCREEN = """
@media screen{
  html,body{ background:var(--app-desk) }
  .sheet{ max-width:1120px; margin:36px auto 60px }
  .wrap{ max-width:none; padding:0 40px }
  .masthead{ padding:48px 0 36px }
  .tscroll{ overflow-x:auto }
}
@media screen and (max-width:820px){
  .sheet{ margin:0; border-left:0; border-right:0; box-shadow:none }
  .wrap{ padding:0 18px }
}
"""


def split_source(path: Path):
    """Возвращает (title, css, body) исходного документа."""
    raw = path.read_text(encoding="utf-8")
    title = re.search(r"<title>(.*?)</title>", raw, re.S).group(1).strip()
    css = "\n".join(re.findall(r"<style>(.*?)</style>", raw, re.S))
    body = raw[raw.rindex("</style>") + len("</style>"):]
    body = re.sub(r"</body>\s*|</html>\s*", "", body).strip()
    return title, css, body


def wrap_tables(body: str) -> str:
    """Оборачивает таблицы в контейнер с горизонтальной прокруткой."""
    return re.sub(r"(<table\b.*?</table>)", r'<div class="tbl">\1</div>', body, flags=re.S)


def topbar(current_slug: str, pdf: str | None) -> str:
    links = []
    for d in DOCS:
        cur = ' aria-current="page"' if d["slug"] == current_slug else ""
        links.append(f'<a href="{d["slug"]}.html"{cur}><i>{d["num"]}</i>{escape(d["nav"])}</a>')
    pdf_link = f'<a class="pdf" href="pdf/{pdf}">PDF</a>' if pdf else ""
    return f"""<header id="appbar">
  <a class="mark" href="index.html"><b>Animaccord</b><span>AI-девайс</span></a>
  <button class="burger" type="button" aria-expanded="false" aria-controls="appnav">Разделы</button>
  <nav id="appnav" aria-label="Документы">{"".join(links)}</nav>
  {pdf_link}
</header>"""


def pager(idx: int) -> str:
    parts = []
    if idx > 0:
        p = DOCS[idx - 1]
        parts.append(f'<a class="prev" href="{p["slug"]}.html">'
                     f'<span class="dir">← {p["num"]} · назад</span>'
                     f'<span class="ttl">{escape(p["title"])}</span></a>')
    if idx < len(DOCS) - 1:
        n = DOCS[idx + 1]
        parts.append(f'<a class="next" href="{n["slug"]}.html">'
                     f'<span class="dir">{n["num"]} · дальше →</span>'
                     f'<span class="ttl">{escape(n["title"])}</span></a>')
    return f'<nav id="pager" aria-label="Соседние документы">{"".join(parts)}</nav>' if parts else ""


def foot(pdf: str | None) -> str:
    extra = f' · <a href="pdf/{pdf}">Скачать PDF</a>' if pdf else ""
    return f"""<footer id="appfoot"><hr>
  Исследование по детским AI-девайсам · Animaccord · август 2026.
  Все цифры сопровождаются источниками внутри документов.
  <a href="index.html">К оглавлению</a>{extra}
</footer>"""


def build_doc(idx: int, d: dict):
    title, css, body = split_source(SRC / d["src"])
    if d["family"] == "print":
        body = wrap_tables(body)
        adapt = skin(SKIN_PRINT_VARS) + ADAPT_PRINT
    else:
        adapt = skin(SKIN_SCREEN_VARS) + ADAPT_SCREEN
    body = f'<div class="sheet">{body}</div>' 
    page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} — Animaccord</title>
<meta name="description" content="{escape(d['desc'][:180])}">
{FONTS}
<link rel="stylesheet" href="assets/app.css">
<style>{css}</style>
<style>{adapt}</style>
</head>
<body>
<a class="app-skip" href="#doc">К содержанию документа</a>
{topbar(d['slug'], d['pdf'])}
<main id="doc" class="doc">
{body}
</main>
{pager(idx)}
{foot(d['pdf'])}
<script src="assets/app.js"></script>
</body>
</html>
"""
    (OUT / f"{d['slug']}.html").write_text(page, encoding="utf-8")


INDEX_CSS = """
*{ box-sizing:border-box; margin:0; padding:0 }
body{ background:var(--app-desk); color:var(--app-ink); font-family:var(--app-sans);
  font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased }
a{ color:var(--app-signal); text-decoration:none;
  border-bottom:1px solid rgba(36,91,255,.35); transition:border-color .15s ease, color .15s ease }
a:hover{ border-bottom-color:var(--app-signal) }
.sheet{ max-width:1040px; margin:36px auto 64px }
.tag{ font-family:var(--app-mono); font-size:10px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--app-steel) }

/* титульный блок */
.titleblock{ border-bottom:1px solid var(--app-ink); background:var(--app-paper) }
.tb-main{ padding:56px 40px 44px }
.tb-main h1{ font-size:clamp(32px,5.6vw,58px); font-weight:600; letter-spacing:.04em;
  line-height:1.05; text-transform:uppercase; margin-top:18px }
.tb-main h1 .half{ color:var(--app-steel) }
.tb-role{ margin-top:16px; font-size:clamp(17px,2.4vw,23px); font-weight:500 }
.tb-role em{ font-style:normal; color:var(--app-signal) }
.tb-lede{ margin-top:26px; max-width:640px; font-size:17px }
.stats{ display:grid; grid-template-columns:repeat(4,1fr); gap:1px;
  background:var(--app-steel-32); border-top:1px solid var(--app-steel-32) }
.stat{ background:var(--app-paper); padding:18px 20px 20px }
.stat .n{ font-family:var(--app-mono); font-size:28px; font-weight:600; letter-spacing:-.01em }
.stat .n sup{ font-size:14px; color:var(--app-signal) }
.stat .l{ margin-top:4px; font-family:var(--app-mono); font-size:10px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--app-steel) }

/* секции */
section{ padding:52px 40px; border-bottom:1px solid var(--app-steel-32) }
section:last-of-type{ border-bottom:none }
.sec-head{ display:flex; align-items:baseline; gap:16px; margin-bottom:22px }
.sec-num{ font-family:var(--app-mono); font-size:13px; font-weight:600;
  color:var(--app-signal); letter-spacing:.1em }
h2{ font-size:24px; font-weight:600; letter-spacing:.01em }
.rule{ height:1px; background:var(--app-ink); margin-bottom:30px; transform-origin:left center }
.about p{ max-width:660px; margin-bottom:14px }
.about p:last-child{ margin-bottom:0 }

/* документ как карточка */
.doc{ border:1px solid var(--app-ink); background:var(--app-paper); margin-bottom:28px }
.doc:last-child{ margin-bottom:0 }
.doc-head{ display:flex; flex-wrap:wrap; align-items:baseline; gap:6px 16px; padding:20px 24px 6px }
.doc-head .idx{ font-family:var(--app-mono); font-size:13px; font-weight:600;
  color:var(--app-signal); letter-spacing:.1em }
.doc h3{ font-size:20px; font-weight:600; line-height:1.25; flex:1 1 300px }
.doc h3 a{ color:var(--app-ink); border-bottom:0 }
.doc h3 a:hover{ color:var(--app-signal) }
.doc-sub{ width:100%; padding:0 24px 16px; border-bottom:1px solid var(--app-steel-32) }
.doc-body{ display:grid; grid-template-columns:1fr 1fr }
.doc-cell{ padding:18px 24px 20px; border-bottom:1px solid var(--app-steel-16) }
.doc-cell:nth-child(odd){ border-right:1px solid var(--app-steel-16) }
.doc-cell .k{ display:block; font-family:var(--app-mono); font-size:10px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--app-steel); margin-bottom:7px }
.doc-cell p{ font-size:15px }
.chips{ list-style:none; display:flex; flex-wrap:wrap; gap:6px }
.chips li{ font-family:var(--app-mono); font-size:10.5px; letter-spacing:.04em;
  color:var(--app-ink); border:1px solid var(--app-steel-32); padding:5px 8px }
.doc-act{ grid-column:1 / -1; padding:18px 24px 20px; background:var(--app-signal-08);
  border-top:1px solid var(--app-signal); border-bottom:none !important;
  border-right:none !important; display:flex; flex-wrap:wrap; align-items:center; gap:12px }
.btn{ font-family:var(--app-mono); font-size:12px; font-weight:500; letter-spacing:.1em;
  text-transform:uppercase; padding:12px 22px; border:1px solid var(--app-ink);
  color:var(--app-ink); background:var(--app-paper); transition:all .15s ease }
.btn.primary{ background:var(--app-signal); border-color:var(--app-signal); color:var(--app-paper) }
.btn.primary:hover{ background:var(--app-ink); border-color:var(--app-ink) }
.btn:hover{ border-color:var(--app-signal); color:var(--app-signal) }
.doc-act .size{ font-family:var(--app-mono); font-size:11px; letter-spacing:.06em;
  color:var(--app-steel); margin-left:auto }

/* как пользоваться */
.method{ list-style:none; max-width:740px }
.method li{ position:relative; padding:0 0 16px 34px; margin-bottom:16px;
  border-bottom:1px solid var(--app-steel-16); font-size:15.5px }
.method li:last-child{ border-bottom:none; margin-bottom:0; padding-bottom:0 }
.method li::before{ content:'\\2316'; position:absolute; left:0; top:1px;
  font-family:var(--app-mono); color:var(--app-signal); font-size:15px }
.archive{ margin-top:26px; padding:16px 20px; border:1px solid var(--app-steel-32);
  font-size:14px; color:var(--app-steel) }
.archive a{ color:var(--app-signal) }

footer.site{ display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px;
  padding:14px 40px; border-top:1px solid var(--app-ink); font-family:var(--app-mono);
  font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--app-steel) }

/* движение */
@keyframes fadein{ from{ opacity:0; transform:translateY(8px) } to{ opacity:1; transform:none } }
@keyframes drawx{ from{ transform:scaleX(0) } to{ transform:scaleX(1) } }
.tb-main > *{ opacity:0; animation:fadein .6s ease forwards }
.tb-main > *:nth-child(1){ animation-delay:.05s }
.tb-main > *:nth-child(2){ animation-delay:.14s }
.tb-main > *:nth-child(3){ animation-delay:.22s }
.tb-main > *:nth-child(4){ animation-delay:.3s }
.reveal{ opacity:0; transform:translateY(10px);
  transition:opacity .55s ease, transform .55s ease }
.reveal.on{ opacity:1; transform:none }
.reveal.on .rule{ animation:drawx .6s ease forwards }
@media (prefers-reduced-motion:reduce){
  .tb-main > *,.reveal,.reveal.on .rule{ animation:none !important; opacity:1 !important;
    transform:none !important; transition:none !important }
}

@media (max-width:820px){
  .sheet{ margin:0; border-left:0; border-right:0; box-shadow:none }
  .tb-main{ padding:38px 20px 30px }
  .stats{ grid-template-columns:repeat(2,1fr) }
  section{ padding:36px 20px }
  .doc-body{ grid-template-columns:1fr }
  .doc-cell:nth-child(odd){ border-right:0 }
  .doc-act .size{ margin-left:0; width:100% }
  footer.site{ padding:14px 20px }
}
"""


def build_index():
    cards = []
    for d in DOCS:
        chips = "".join(f"<li>{escape(c)}</li>" for c in d["chips"])
        pdf = (f'<a class="btn" href="pdf/{d["pdf"]}">PDF</a>' if d["pdf"] else "")
        cards.append(f"""<article class="doc reveal">
  <div class="doc-head">
    <span class="idx">{d['num']}</span>
    <h3><a href="{d['slug']}.html">{escape(d['title'])}</a></h3>
  </div>
  <div class="doc-sub tag">{escape(d['sub'])}</div>
  <div class="doc-body">
    <div class="doc-cell">
      <span class="k">О чём</span>
      <p>{escape(d['desc'])}</p>
    </div>
    <div class="doc-cell">
      <span class="k">Разделы</span>
      <ul class="chips">{chips}</ul>
    </div>
    <div class="doc-act">
      <a class="btn primary" href="{d['slug']}.html">Читать</a>{pdf}
      <span class="size">{escape(d['size'])}</span>
    </div>
  </div>
</article>""")

    page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Детский AI-девайс — исследование для Animaccord</title>
<meta name="description" content="Четыре документа: обзор рынка, платформенный слой,
 лицензируемый слой персонажа и вводные для инвестиционного пакета.">
{FONTS}
<link rel="stylesheet" href="assets/app.css">
<style>{INDEX_CSS}</style>
</head>
<body>
<a class="app-skip" href="#docs">К списку документов</a>
{topbar('index', None)}

<div class="sheet">
  <header class="titleblock">
    <div class="tb-main">
      <span class="tag">Animaccord · AI-девайс · исследование</span>
      <h1>Детский <span class="half">AI-девайс</span></h1>
      <p class="tb-role">Рынок, платформы и <em>предмет разработки</em></p>
      <p class="tb-lede">Четыре документа, которые читаются подряд. Первый описывает рынок
        как он есть, второй разбирает, из чего такие устройства собирают, третий предлагает
        предмет разработки, четвёртый готовит цифры к разговору с инвестором.</p>
    </div>
    <div class="stats">
      <div class="stat"><div class="n">4</div><div class="l">документа</div></div>
      <div class="stat"><div class="n">33</div><div class="l">продукта в обзоре</div></div>
      <div class="stat"><div class="n">8</div><div class="l">поставщиков</div></div>
      <div class="stat"><div class="n">08<sup>·26</sup></div><div class="l">дата сборки</div></div>
    </div>
  </header>

  <section class="about reveal">
    <div class="sec-head"><span class="sec-num">01</span><h2>Что это</h2></div>
    <div class="rule"></div>
    <p>Исследование под задачу: Animaccord строит детское голосовое устройство и готовится
      идти к инвесторам. Нужно было понять, что в категории уже существует, из чего такие
      устройства собирают, что имеет смысл разрабатывать самим и какими цифрами это
      подкрепляется.</p>
    <p>Каждая цифра в документах сопровождается источником или пометкой о том, что это расчёт.
      Данные взяты из открытых источников — отчётности, тарифов поставщиков, сообщений
      о сделках — и проверяются по ссылкам в конце каждого документа.</p>
  </section>

  <section id="docs">
    <div class="sec-head"><span class="sec-num">02</span><h2>Порядок чтения</h2></div>
    <div class="rule"></div>
{"".join(cards)}
  </section>

  <section class="reveal">
    <div class="sec-head"><span class="sec-num">03</span><h2>Как этим пользоваться</h2></div>
    <div class="rule"></div>
    <ul class="method">
      <li>Порядок задан по нарастанию: от того, что уже существует на рынке, к тому,
        что предлагается построить.</li>
      <li>Каждый следующий документ опирается на цифры предыдущего и ссылается на них
        по номерам разделов.</li>
      <li>Веб-версия и PDF собираются из одного источника, поэтому разойтись они не могут.
        PDF удобен для пересылки и печати, веб — для чтения с телефона.</li>
      <li>Разделы с собранными данными переносятся в презентацию как есть; формы под решения
        компании отмечены отдельно в четвёртом документе.</li>
    </ul>
    <div class="archive">
      Архив: <a href="pdf/animaccord-business-model-v1.pdf">первая версия отчёта</a> —
      та, что с выводами, до переработки в проектный документ. Оставлена для истории.
    </div>
  </section>

  <footer class="site">
    <span>Animaccord · AI-девайс · исследование</span>
    <span>Август 2026</span>
  </footer>
</div>
<script src="assets/app.js"></script>
</body>
</html>
"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "pdf").mkdir(exist_ok=True)
    if ROOT_SITE:
        (OUT / ".nojekyll").touch()
    shutil.copytree(SRC / "_site-assets", OUT / "assets", dirs_exist_ok=True)
    for i, d in enumerate(DOCS):
        build_doc(i, d)
    build_index()
    for name in [d["pdf"] for d in DOCS if d["pdf"]] + ["animaccord-business-model-v1.pdf"]:
        shutil.copy2(SRC / name, OUT / "pdf" / name)
    print("собрано:", ", ".join(p.name for p in sorted(OUT.glob("*.html"))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help=f"каталог сборки (по умолчанию {OUT})")
    ap.add_argument("--subdir", action="store_true",
                    help="сайт лежит в подпапке чужого репозитория: .nojekyll не создаётся")
    args = ap.parse_args()
    if args.out:
        OUT = Path(args.out).resolve()
    if args.subdir:
        ROOT_SITE = False
    main()
