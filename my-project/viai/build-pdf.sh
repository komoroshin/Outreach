#!/usr/bin/env bash
# Rebuild deck.pdf from deck.html with headless Chromium.
set -euo pipefail
cd "$(dirname "$0")"
CH="${CHROME:-$(command -v chromium || command -v google-chrome || echo /opt/pw-browsers/chromium-1194/chrome-linux/chrome)}"
"$CH" --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=4000 --print-to-pdf="$PWD/deck.pdf" "file://$PWD/deck.html"
echo "deck.pdf written"
