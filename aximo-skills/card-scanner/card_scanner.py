#!/usr/bin/env python3
"""
card_scanner.py — из распознанных контактов (или фото визиток) собирает contacts.csv.

Режим без ключа (демо, используется навыком card-scanner):
    python3 card_scanner.py --from-json contacts.json --out contacts.csv
    Читает JSON-список контактов (распознанных Claude по фото) и пишет CSV.

Режим масштабирования (для больших объёмов, нужен GEMINI_API_KEY в .env):
    python3 card_scanner.py --image visitki.jpg --out contacts.csv
    Сам шлёт фото в Gemini Flash (vision), получает контакты, пишет CSV.

Колонки CSV: name, title, company, email, phone, website.
"""
import argparse
import base64
import csv
import json
import os
import sys
import urllib.request


FIELDS = ["name", "title", "company", "email", "phone", "website"]


def load_env_key(key_name):
    """Читает ключ из .env (простая построчная разборка KEY=VALUE)."""
    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        return None
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{key_name}="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def contacts_from_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    contacts = []
    for row in data:
        contacts.append({field: row.get(field, "") or "" for field in FIELDS})
    return contacts


def contacts_from_image_via_gemini(image_path, api_key):
    """Масштабирование: распознаёт визитки на фото через Gemini Flash (vision)."""
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    prompt = (
        "Extract every business card visible in this photo. "
        "Return ONLY a JSON array, each item with fields: "
        "name, title, company, email, phone, website. "
        "Leave a field empty string if not present on the card. Do not invent data."
    )
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/png", "data": image_b64}},
            ]
        }]
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-flash-latest:generateContent?key={api_key}"
    )
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    text = result["candidates"][0]["content"]["parts"][0]["text"]
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(text)
    return [{field: row.get(field, "") or "" for field in FIELDS} for row in data]


def push_to_crm(contacts):
    """Место под интеграцию с реальной CRM/Instantly. Не вызывается по умолчанию."""
    # TODO: push — здесь можно POST-ить строки в CRM/Instantly API.
    raise NotImplementedError("Пуш в CRM/Instantly подключается отдельно под конкретный сервис.")


def write_csv(contacts, out_path):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(contacts)


def print_table(contacts):
    headers = ["Имя", "Должность", "Компания", "Email", "Телефон", "Сайт"]
    widths = [len(h) for h in headers]
    for c in contacts:
        for i, field in enumerate(FIELDS):
            widths[i] = max(widths[i], len(c[field]))
    row_fmt = "  ".join(f"{{:<{w}}}" for w in widths)
    print(row_fmt.format(*headers))
    for c in contacts:
        print(row_fmt.format(*(c[field] for field in FIELDS)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-json", help="JSON-список распознанных контактов")
    parser.add_argument("--image", help="Фото визиток (режим масштабирования, нужен GEMINI_API_KEY)")
    parser.add_argument("--out", required=True, help="Куда писать CSV")
    args = parser.parse_args()

    if args.from_json:
        contacts = contacts_from_json(args.from_json)
    elif args.image:
        api_key = load_env_key("GEMINI_API_KEY")
        if not api_key:
            print("Нет GEMINI_API_KEY в .env — для демо используй --from-json.")
            sys.exit(1)
        contacts = contacts_from_image_via_gemini(args.image, api_key)
    else:
        print("Укажи --from-json или --image.")
        sys.exit(2)

    write_csv(contacts, args.out)
    print(f"Готов CSV: {os.path.abspath(args.out)}\n")
    print_table(contacts)


if __name__ == "__main__":
    main()
