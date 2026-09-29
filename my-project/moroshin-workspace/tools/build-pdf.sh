#!/usr/bin/env bash
# Собирает PDF (A4) из HTML-документа через headless Chrome/Chromium.
# Пример: tools/build-pdf.sh offers/universal/offer.html offers/universal/Outreach_offer_Moroshin.pdf
# Шрифты IBM Plex грузятся с Google Fonts — нужен доступ в интернет.
set -euo pipefail

in="${1:?Укажите входной HTML}"
out="${2:?Укажите выходной PDF}"

chrome=""
for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" google-chrome google-chrome-stable chromium chromium-browser; do
  if [ -x "$c" ] || command -v "$c" >/dev/null 2>&1; then chrome="$c"; break; fi
done
if [ -z "$chrome" ]; then
  echo "Не найден Chrome или Chromium. Установите, например: npx playwright install chromium" >&2
  exit 1
fi

in_abs="$(cd "$(dirname "$in")" && pwd)/$(basename "$in")"
mkdir -p "$(dirname "$out")"
out_abs="$(cd "$(dirname "$out")" && pwd)/$(basename "$out")"

"$chrome" --headless=new --disable-gpu --no-sandbox --no-pdf-header-footer \
  --virtual-time-budget=15000 --print-to-pdf="$out_abs" "file://$in_abs" 2>/dev/null

echo "Готово: $out"
