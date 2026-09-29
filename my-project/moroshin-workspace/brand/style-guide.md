# Стилистика «чертёжный лист»

Визуальная система страниц Константина Морошина. Основана на дизайн-системе HALFSTEEL: инженерный чертёж / синька. Документ описывает, как воспроизвести стиль в других артефактах — на сайте, в презентации, в PDF.

Живые примеры:
- https://komoroshin.github.io/research/ — для агентств и консалтинга
- https://komoroshin.github.io/directresearch/ — для конечных заказчиков

---

## 1. Идея

Страница — это **чертёжный лист**, лежащий на столе. Отсюда всё остальное:

- лист бумаги светлее фона стола, у листа есть край — рамка в 1px;
- по листу идёт миллиметровка — еле заметная сетка 64px;
- разделы разграничены линиями, а не воздухом и не карточками с тенями;
- служебные подписи набраны моноширинным шрифтом капслоком, как на чертеже;
- один сигнальный цвет — синий, им отмечено только важное.

**Главное правило:** эстетику чертежа держат сетка, линии и моноширинные подписи — **а не слова**. Никаких декоративных псевдотехнических надписей ради вида («SHEET 01 OF 01», «REV. A», «PROJECT KM-001», «СТАТУС: ОТКРЫТ»). Каждое слово на листе должно что-то значить, иначе его нет.

---

## 2. Цвета

| Токен | HEX | Роль |
|---|---|---|
| `--desk` | `#E7E3D7` | фон страницы (стол под листом) |
| `--paper` | `#F3F0E8` | фон листа и всех карточек |
| `--ink` | `#111111` | текст, основные рамки и линии |
| `--steel` | `#6B7075` | вторичный текст, моно-подписи |
| `--steel-08` | `rgba(107,112,117,.08)` | миллиметровая сетка |
| `--steel-16` | `rgba(107,112,117,.16)` | тонкие линии внутри блоков |
| `--steel-32` | `rgba(107,112,117,.32)` | линии между разделами и ячейками |
| `--signal` | `#245BFF` | акцент |

**Куда идёт акцент и только туда:** номера разделов, ссылки, буллеты списков, верхняя рамка и подпись блока «Результат», заливка главной кнопки, выделение текста (`::selection`).

Фон блока «Результат» — тот же синий с прозрачностью 5%: `rgba(36,91,255,.05)`.

---

## 3. Шрифты

**IBM Plex Sans** (400/500/600/700) — всё, что читают.
**IBM Plex Mono** (400/500/600) — всё, что маркирует: подписи, номера, цифры в плитках, кнопки, футер.

```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&subset=cyrillic&display=swap" rel="stylesheet">
```

Шкала:

| Роль | Размер | Начертание | Особенности |
|---|---|---|---|
| H1 | `clamp(34px, 6vw, 64px)` | 600 | капслок, трекинг +.04em, интерлиньяж 1.05 |
| Подзаголовок-роль | `clamp(18px, 2.6vw, 24px)` | 500 | часть фразы — синим |
| Лид | 17px | 400 | ширина не больше 620px |
| H2 раздела | 24px | 600 | — |
| H3 карточки / кейса | 17–20px | 600 | — |
| Основной текст | 16px | 400 | интерлиньяж 1.55 |
| Текст в карточках | 15px | 400 | — |
| Моно-подписи | 10px | 400 | капслок, трекинг +.14em, цвет steel |
| Моно-кнопки | 13px | 500 | капслок, трекинг +.1em |
| Цифры в плитках | 30px | 600 | моно, плюсик — синим и надстрочным |

Капслок допустим ровно в трёх местах: H1, моно-подписи, кнопки. В обычном тексте — никогда.

---

## 4. Сетка и ритм

- Лист: `max-width: 1040px`, поля страницы 40px сверху и 64px снизу.
- Внутренние отступы листа: **40px** по горизонтали, **56px** вертикально в разделах.
- Шаг сетки-миллиметровки: **64px**.
- На ширине **≤760px** лист занимает всю ширину, поля падают до 20px, все двухколонники схлопываются в один, лист теряет боковые рамки.
- Углы всегда прямые. Радиусов нет нигде.
- Теней внутри листа нет. Тень есть только у самого листа — она отделяет его от стола.

---

## 5. Компоненты

### Шапка
Двухколонник: слева текст (имя → роль → два абзаца лида), справа фото в рамке 1px с внутренним полем 8px — как вклеенная в чертёж карточка. Колонка фото 280px. Снизу шапка отбита сплошной линией `--ink`.

### Заголовок раздела
Моно-номер синим (`01`, `02`…) + H2 в одну строку по базовой линии, под ними — сплошная линия `--ink` на всю ширину, которая при появлении «прочерчивается» слева направо.

### Таблица-сетка карточек
Приём, который держит весь стиль: контейнер с фоном `--steel-32` и `gap: 1px`, карточки с фоном `--paper`. Промежутки в 1px читаются как расчерченная таблица, а не как отступы между плашками. Так собраны блоки задач, ценностей и плитки с цифрами.

### Карточка кейса
Рамка 1px `--ink`. Внутри: заголовок → строка клиента моно-капслоком → блок «Результат» на синей подложке 5% с верхней рамкой синим и подписью с буллетом `●`.

Развёрнутый вариант (для агентств) добавляет между ними сетку ячеек «Задача / Что делали / Моя часть» с моно-подписями.

### Шаги процесса
Двухколоночный список: слева моно-номер синим в колонке 44px, справа заголовок и текст. Между шагами — линия `--steel-16`.

### Список принципов
Маркер `⌖` (перекрестие прицела) синим, отступ 36px, между пунктами линия `--steel-16`. У последнего пункта линии нет.

### Кнопки
Прямоугольные, моно, капслок, паддинг 14/26.
- Главная: заливка `--signal`, текст цвета бумаги; на ховере становится чёрной.
- Вторая: прозрачная, рамка `--ink`; на ховере рамка и текст синеют.

### Футер
Полоса поверх линии `--ink`, моно 10px капслоком: слева — кто это, справа — год.

---

## 6. Движение

Сдержанное. Ничего не мигает, не прыгает, не выезжает сбоку.

- При загрузке шапка проявляется по элементам: `opacity 0 → 1` плюс подъём на 8px, задержки 0.05 / 0.15 / 0.25 / 0.32с.
- При скролле блоки проявляются так же — через `IntersectionObserver`, класс `.reveal` → `.on`, порог 0.12.
- Линии разделов прочерчиваются через `transform: scaleX(0 → 1)` за 0.8с.
- Все переходы обязаны отключаться при `prefers-reduced-motion: reduce`.

---

## 7. Готовый CSS

Токены и каркас — вставляются как есть.

```css
* { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --paper: #F3F0E8;
  --desk: #E7E3D7;
  --ink: #111111;
  --steel: #6B7075;
  --steel-16: rgba(107,112,117,.16);
  --steel-32: rgba(107,112,117,.32);
  --steel-08: rgba(107,112,117,.08);
  --signal: #245BFF;
  --sans: 'IBM Plex Sans', sans-serif;
  --mono: 'IBM Plex Mono', monospace;
}

body {
  background: var(--desk);
  color: var(--ink);
  font-family: var(--sans);
  font-size: 16px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}

::selection { background: var(--signal); color: var(--paper); }

a {
  color: var(--signal);
  text-decoration: none;
  border-bottom: 1px solid rgba(36,91,255,.35);
  transition: border-color .15s ease, color .15s ease;
}
a:hover { border-bottom-color: var(--signal); }

/* лист */
.sheet {
  max-width: 1040px;
  margin: 40px auto 64px;
  background: var(--paper);
  border: 1px solid var(--ink);
  box-shadow: 0 1px 0 rgba(17,17,17,.2), 0 24px 60px -30px rgba(17,17,17,.35);
  background-image:
    linear-gradient(var(--steel-08) 1px, transparent 1px),
    linear-gradient(90deg, var(--steel-08) 1px, transparent 1px);
  background-size: 64px 64px;
}

/* моно-подпись */
.tag {
  font-family: var(--mono);
  font-size: 10px;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: var(--steel);
}

/* раздел */
section { padding: 56px 40px; border-bottom: 1px solid var(--steel-32); }
section:last-of-type { border-bottom: none; }

.sec-head { display: flex; align-items: baseline; gap: 16px; margin-bottom: 32px; }
.sec-num {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--signal);
  letter-spacing: .1em;
}
h2 { font-size: 24px; font-weight: 600; letter-spacing: .01em; }
.rule {
  height: 1px;
  background: var(--ink);
  margin-bottom: 32px;
  transform-origin: left center;
}

/* таблица-сетка карточек */
.cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--steel-32);
  border: 1px solid var(--ink);
}
.card { background: var(--paper); padding: 22px 24px 24px; }
.card h3 { font-size: 17px; font-weight: 600; line-height: 1.3; margin-bottom: 8px; }
.card p { font-size: 15px; }

/* блок результата */
.case-result {
  padding: 20px 24px 22px;
  background: rgba(36,91,255,.05);
  border-top: 1px solid var(--signal);
}

/* кнопки */
.btn {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: .1em;
  text-transform: uppercase;
  padding: 14px 26px;
  border: 1px solid var(--ink);
  color: var(--ink);
  background: var(--paper);
  transition: all .15s ease;
}
.btn:hover { border-color: var(--signal); color: var(--signal); }
.btn.primary { background: var(--signal); border-color: var(--signal); color: var(--paper); }
.btn.primary:hover { background: var(--ink); border-color: var(--ink); }

/* движение */
@keyframes hs-fadein { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
.reveal { opacity: 0; transform: translateY(10px); transition: opacity .55s ease, transform .55s ease; }
.reveal.on { opacity: 1; transform: none; }
.rule.reveal { transform: scaleX(0); transition: transform .8s ease; }
.rule.reveal.on { transform: scaleX(1); }

@media (prefers-reduced-motion: reduce) {
  .reveal, .rule.reveal { animation: none !important; transition: none !important; opacity: 1 !important; transform: none !important; }
}

/* мобильная */
@media (max-width: 760px) {
  .sheet { margin: 0; border-left: none; border-right: none; }
  section { padding: 40px 20px; }
  .cards { grid-template-columns: 1fr; }
}
```

Скрипт проявления при скролле:

```html
<script>
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); }
    }
  }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
</script>
```

Каркас разметки:

```html
<div class="sheet">
  <header class="titleblock">…</header>

  <section>
    <div class="sec-head reveal">
      <span class="sec-num">01</span>
      <h2>Название раздела</h2>
    </div>
    <div class="rule reveal"></div>
    …содержание…
  </section>

  <footer>
    <span>КТО ЭТО</span>
    <span>2026</span>
  </footer>
</div>
```

---

## 8. Чего не делать

- Не добавлять декоративные технические надписи, которые ничего не значат.
- Не использовать акцентный синий как фон крупных блоков — только тонкие рамки, текст и одна кнопка.
- Не набирать моношрифтом абзацы: он только для подписей, номеров и кнопок.
- Не заводить второй акцентный цвет и не вводить градиенты.
- Не скруглять углы и не класть тени внутри листа.
- Не разделять блоки пустотой там, где по логике нужна линия: стиль держится на линиях.
- Не заменять линии `--steel-32` на серые заливки — исчезает ощущение чертежа.

---

## 9. Перенос на другие носители

**Презентация.** Слайд = лист: те же поля 40px, миллиметровка, моно-номер раздела в углу, заголовок и линия под ним. Один акцент на слайд.

**PDF и документы.** Лист без тени, фон белее (`--paper` на белом), линии те же. Колонтитул — моно 10px капслоком.

**Соцсети и превью.** Квадрат с миллиметровкой, крупный H1 капслоком, одна синяя линия или подпись. Фото — всегда в рамке 1px с полем 8px.

**Тон текста.** Стиль визуально сухой, поэтому и текст должен быть сухим: конкретика, цифры, никаких «мы предлагаем комплексные решения». Вежливые обороты вроде «чем могу быть полезен» и слова-вставки вроде «Внутри:» ломают стиль сильнее, чем неверный оттенок синего.
