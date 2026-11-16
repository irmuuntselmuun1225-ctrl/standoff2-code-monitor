import os
import json
import hashlib
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urlencode

SOURCES = {
    "Standoff 2 Media": "https://media.standoff2.com/48Qyrlx",
    "Standoff 2 MAX": "https://max.ru/standoff2",
}

STATE_FILE = "seen.json"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)


def fetch_page(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        html = response.read().decode("utf-8", errors="ignore")

    parser = TextExtractor()
    parser.feed(html)
    return " ".join(parser.text).strip()


def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)
    urllib.request.urlopen(request, timeout=20)


def main():
    try:
        with open(STATE_FILE, "r") as file:
            old_state = json.load(file)
    except FileNotFoundError:
        old_state = {}

    new_state = old_state.copy()

    for name, url in SOURCES.items():
        try:
            content = fetch_page(url)
            if not content:
                print(f"No readable content: {name}")
                continue

            digest = hashlib.sha256(content.encode()).hexdigest()

            if name not in old_state:
                print(f"Saved first check: {name}")
            elif old_state[name] != digest:
                send_telegram(
                    f"🔔 Standoff 2 update detected!\n\n"
                    f"Source: {name}\n"
                    f"Check the page: {url}"
                )
                print(f"Update detected: {name}")

            new_state[name] = digest

        except Exception as error:
            print(f"Could not check {name}: {error}")

    with open(STATE_FILE, "w") as file:
        json.dump(new_state, file, indent=2)
    def send_telegram(message):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode()

    request = urllib.request.Request(url, data=data)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print("TELEGRAM RESPONSE:", response.read().decode())
    except urllib.error.HTTPError as error:
        print("TELEGRAM ERROR:", error.read().decode())
        raise

if __name__ == "__main__":
    main()
