#!/usr/bin/env python3
"""Собирает docs/ — сайт из четырёх исследовательских документов.

Источник правды остаётся в my-project/research/*.html: скрипт вынимает из каждого
файла заголовок, стили и содержимое и заворачивает их в общую оболочку.
Запуск: python3 my-project/research/_build-site.py
"""
import re, shutil
from pathlib import Path
from html import escape

SRC = Path(__file__).resolve().parent
OUT = SRC.parents[1] / "docs"

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
    'family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&'
    'family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">'
)

# Экранный слой для документов, свёрстанных под A4: лист на фоне приложения,
# пропорциональное укрупнение pt-шрифтов и горизонтальная прокрутка таблиц.
ADAPT_PRINT = """
@media screen{
  html,body{ background:var(--app-bg) }
  .doc{ zoom:1.2 }
  .paper{ max-width:196mm; margin:0 auto; padding:16mm 15mm 20mm;
    background:var(--paper); border:1px solid var(--app-rule); box-shadow:var(--app-shadow) }
  .tbl{ overflow-x:auto; margin:0 0 1mm }
  .tbl table{ min-width:34rem }
  .srclist a{ overflow-wrap:anywhere }
}
@media screen and (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ink:#E6EAE7; --ink-2:#A8B2AD; --ink-3:#7B8580;
    --paper:#161B19; --tint:#1E2523; --rule:#2A322E; --rule-2:#3C4641;
    --accent:#8FBFAF; --warn:#D9A63C; --neg:#E0796A;
  }
}
@media screen and (max-width:820px){
  .doc{ zoom:1.08 }
  .paper{ padding:22px 16px 36px; border-left:0; border-right:0; box-shadow:none }
  .meta{ grid-template-columns:repeat(2,1fr) }
  .meta div:nth-child(2n){ border-right:0 }
  .split,.spec{ grid-template-columns:1fr }
  .card-top{ flex-direction:column; align-items:flex-start; gap:6px }
  .card-top .who{ text-align:left; white-space:normal }
  .legend-row{ gap:3mm }
}
"""

# Экранные документы отзывчивы сами; поправка нужна только под фиксированную шапку.
ADAPT_SCREEN = """
@media screen{
  thead th{ top:var(--app-bar-h) }
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
        body = f'<div class="paper">{wrap_tables(body)}</div>'
        adapt = ADAPT_PRINT
    else:
        adapt = ADAPT_SCREEN
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
body{ font-family:var(--app-sans); background:var(--app-bg); color:var(--app-ink);
  margin:0; line-height:1.6; -webkit-font-smoothing:antialiased }
.shell{ max-width:940px; margin:0 auto; padding:0 28px }
.hero{ padding:72px 0 44px; border-bottom:1px solid var(--app-rule) }
.hero .eyebrow{ font:500 10px/1 var(--app-mono); letter-spacing:.18em; text-transform:uppercase;
  color:var(--app-accent); display:block; margin-bottom:22px }
.hero h1{ font:600 clamp(30px,5.4vw,46px)/1.1 var(--app-serif); letter-spacing:-.015em;
  margin:0 0 20px; text-wrap:balance; max-width:20ch }
.hero p{ font-size:18px; color:var(--app-ink-2); margin:0; max-width:62ch }
.facts{ display:flex; flex-wrap:wrap; gap:0; margin-top:36px;
  border:1px solid var(--app-rule); background:var(--app-surface) }
.facts div{ flex:1 1 150px; padding:14px 18px; border-right:1px solid var(--app-rule) }
.facts div:last-child{ border-right:0 }
.facts dt{ font:500 9.5px/1 var(--app-mono); letter-spacing:.14em; text-transform:uppercase;
  color:var(--app-ink-3); margin-bottom:7px }
.facts dd{ margin:0; font-size:14px; font-weight:600 }

.path{ padding:12px 0 8px }
.step{ display:grid; grid-template-columns:64px 1fr; gap:0 26px; position:relative;
  padding:38px 0 34px; border-bottom:1px solid var(--app-rule) }
.step:last-of-type{ border-bottom:0 }
.step .n{ font:500 12px/1 var(--app-mono); letter-spacing:.12em; color:var(--app-ink-3);
  padding-top:9px; position:relative }
.step .n::after{ content:""; position:absolute; left:5px; top:34px; bottom:-52px;
  width:1px; background:var(--app-rule) }
.step:last-of-type .n::after{ display:none }
.step h2{ font:600 25px/1.2 var(--app-serif); margin:0 0 4px; letter-spacing:-.01em }
.step h2 a{ color:var(--app-ink); text-decoration:none }
.step h2 a:hover{ color:var(--app-accent) }
.step .sub{ font-size:15px; color:var(--app-ink-3); margin:0 0 14px }
.step .desc{ margin:0 0 18px; color:var(--app-ink-2); max-width:60ch }
.chips{ display:flex; flex-wrap:wrap; gap:6px; margin:0 0 20px; padding:0; list-style:none }
.chips li{ font:400 11px/1 var(--app-mono); color:var(--app-ink-2);
  border:1px solid var(--app-rule); padding:6px 9px; background:var(--app-surface) }
.acts{ display:flex; flex-wrap:wrap; align-items:center; gap:10px }
.acts a{ text-decoration:none; font:500 13px/1 var(--app-sans); padding:11px 18px;
  border:1px solid var(--app-accent); border-radius:2px }
.acts a.go{ background:var(--app-accent); color:var(--app-accent-fg) }
.acts a.alt{ color:var(--app-accent); background:transparent }
.acts a:hover{ opacity:.85 }
.acts .size{ font:400 12px/1 var(--app-mono); color:var(--app-ink-3); margin-left:4px }

.note{ border-top:1px solid var(--app-rule); margin-top:8px; padding:38px 0 0 }
.note h3{ font:600 17px/1.3 var(--app-serif); margin:0 0 10px }
.note p{ margin:0 0 12px; color:var(--app-ink-2); max-width:62ch }
.archive{ margin:30px 0 0; padding:16px 18px; border:1px solid var(--app-rule);
  background:var(--app-surface); font-size:13px; color:var(--app-ink-3) }
.archive a{ color:var(--app-ink-2) }
footer.site{ margin-top:56px; padding:26px 0 70px; border-top:1px solid var(--app-rule);
  color:var(--app-ink-3); font-size:13px }
a{ color:var(--app-accent) }
@media (max-width:640px){
  .shell{ padding:0 18px }
  .hero{ padding:44px 0 32px }
  .step{ grid-template-columns:1fr; gap:10px; padding:30px 0 26px }
  .step .n::after{ display:none }
  .step .n{ padding-top:0 }
  .acts a{ flex:1 1 auto; text-align:center }
}
"""


def build_index():
    steps = []
    for d in DOCS:
        chips = "".join(f"<li>{escape(c)}</li>" for c in d["chips"])
        pdf = (f'<a class="alt" href="pdf/{d["pdf"]}">PDF</a>' if d["pdf"]
               else '<span class="size">только веб-версия</span>')
        steps.append(f"""<article class="step">
  <div class="n">{d['num']}</div>
  <div>
    <h2><a href="{d['slug']}.html">{escape(d['title'])}</a></h2>
    <p class="sub">{escape(d['sub'])}</p>
    <p class="desc">{escape(d['desc'])}</p>
    <ul class="chips">{chips}</ul>
    <div class="acts">
      <a class="go" href="{d['slug']}.html">Читать</a>{pdf}
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
<a class="app-skip" href="#path">К списку документов</a>
{topbar('index', None)}

<div class="shell">
  <header class="hero">
    <span class="eyebrow">Animaccord · AI-девайс · исследование</span>
    <h1>Детский AI-девайс: рынок, платформы и предмет разработки</h1>
    <p>Четыре документа, которые читаются подряд. Первый описывает рынок как он есть,
      второй разбирает, из чего такие устройства собирают, третий предлагает предмет
      разработки, четвёртый готовит цифры к разговору с инвестором.</p>
    <dl class="facts">
      <div><dt>Дата</dt><dd>Август 2026</dd></div>
      <div><dt>Документов</dt><dd>4</dd></div>
      <div><dt>Источники</dt><dd>Открытые, со ссылками</dd></div>
      <div><dt>Формат</dt><dd>Веб и PDF</dd></div>
    </dl>
  </header>

  <main id="path" class="path">
{"".join(steps)}
  </main>

  <section class="note">
    <h3>Как этим пользоваться</h3>
    <p>Порядок задан по нарастанию: от того, что уже существует на рынке, к тому,
      что предлагается построить. Каждый следующий документ опирается на цифры предыдущего
      и ссылается на них по номерам разделов.</p>
    <p>Веб-версия и PDF собираются из одного источника, поэтому расходиться они не могут.
      PDF удобен для пересылки и печати, веб — для чтения с телефона.</p>
    <div class="archive">
      Архив: <a href="pdf/animaccord-business-model-v1.pdf">первая версия отчёта</a> —
      та, что с выводами, до переработки в проектный документ. Оставлена для истории.
    </div>
  </section>

  <footer class="site">
    Исследование подготовлено разработчиком для Animaccord. Август 2026.
  </footer>
</div>
<script src="assets/app.js"></script>
</body>
</html>
"""
    (OUT / "index.html").write_text(page, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "pdf").mkdir(exist_ok=True)
    (OUT / ".nojekyll").touch()
    for i, d in enumerate(DOCS):
        build_doc(i, d)
    build_index()
    for name in [d["pdf"] for d in DOCS if d["pdf"]] + ["animaccord-business-model-v1.pdf"]:
        shutil.copy2(SRC / name, OUT / "pdf" / name)
    print("собрано:", ", ".join(p.name for p in sorted(OUT.glob("*.html"))))


if __name__ == "__main__":
    main()
