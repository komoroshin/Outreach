# Откуда навыки better-* и инструменты интерфейса

Источник: https://github.com/jakubkrehel/skills (пакет «interfaces»)
Автор: Jakub Krehel · лицензия MIT (см. interfaces-LICENSE)
Версия: 1.6.3, коммит 267330e
Установлен: 2026-09-09

Навыки, которые Claude подхватывает сам по контексту:
better-accessibility, better-colors, better-layout, better-typography,
better-ui, better-writing, better-interface (сводный обзор по всем сразу).

Инструменты, которые запускаются только по прямой просьбе:
break (прогон компонента по всем состояниям), explain-interface (как это
сделано на чужом сайте), interface-review (обзор правок по категориям),
variant (несколько вариантов компонента на выбор).

Не переносились: agents/openai.yaml в каждом навыке (конфиг под OpenAI),
CLAUDE.md, AGENTS.md и opencode.json репозитория-источника.

Обновить — заново скопировать содержимое skills/ из репозитория-источника.
