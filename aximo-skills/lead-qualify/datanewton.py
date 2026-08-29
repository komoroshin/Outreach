#!/usr/bin/env python3
"""Обогащает российскую компанию по ИНН через DataNewton API (counterparty + finance)."""

import json
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import certifi

API_HOST = "https://api.datanewton.ru/v1"


def load_key(env_path: Path) -> str:
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATANEWTON_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("DATANEWTON_KEY не найден в .env")


def fetch(endpoint: str, key: str, inn: str, filters: str | None = None) -> dict:
    params = {"key": key, "inn": inn}
    if filters:
        params["filters"] = filters
    url = f"{API_HOST}/{endpoint}?{urllib.parse.urlencode(params)}"
    ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(url, context=ctx, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    if len(sys.argv) != 2:
        print("Использование: python3 datanewton.py <ИНН>")
        sys.exit(1)

    inn = sys.argv[1]
    env_path = Path(__file__).resolve().parents[2] / ".env"
    key = load_key(env_path)

    counterparty = fetch("counterparty", key, inn, filters="OWNER_BLOCK,WORKERS_COUNT_BLOCK")
    finance = fetch("finance", key, inn)

    company = counterparty.get("company", {})
    names = company.get("company_names", {})
    workers = company.get("workers_count") or {}
    last_year = max(workers, default=None)

    revenue_rows = (finance.get("fin_results") or {}).get("indicators") or []
    revenue_row = next((r for r in revenue_rows if r.get("code") == "2110"), None)
    revenue_sum = revenue_row.get("sum") if revenue_row else {}
    revenue_last_year = max(revenue_sum, default=None) if revenue_sum else None

    result = {
        "inn": inn,
        "name": names.get("short_name") or names.get("full_name"),
        "status": company.get("status", {}).get("status_rus_short"),
        "owners_individuals": [o.get("name") for o in company.get("owners", {}).get("fl", [])],
        "owners_companies": [o.get("name") for o in company.get("owners", {}).get("ul_rus", [])],
        "employees_count_latest": workers.get(last_year) if last_year else None,
        "employees_count_year": last_year,
        "revenue_thousand_rub_latest": revenue_sum.get(revenue_last_year) if revenue_last_year else None,
        "revenue_year": revenue_last_year,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
