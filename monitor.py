import requests
from bs4 import BeautifulSoup
import json
import os
import xml.etree.ElementTree as ET

SITEMAP = "https://www.kanan.co/sitemap-course-pages.xml"
DATA_FILE = "data.json"

def get_urls():
    r = requests.get(SITEMAP, timeout=30)
    root = ET.fromstring(r.content)
    urls = []
    for url in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
        urls.append(loc)
    return urls

def get_h1(page):
    try:
        r = requests.get(page, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else "NO H1 FOUND"
    except:
        return "ERROR"

def load_old():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_new(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def send_email(changes):
    api_key = os.environ["RESEND_API_KEY"]
    to_email = os.environ["TO_EMAIL"]
    content = "<br><br>".join(changes)
    requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Kanan Monitor <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "⚠️ Kanan H1 Changes Detected",
            "html": f"<p>{content}</p>",
        },
        timeout=30,
    )

def send_no_change_email():
    api_key = os.environ["RESEND_API_KEY"]
    to_email = os.environ["TO_EMAIL"]
    requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "from": "Kanan Monitor <onboarding@resend.dev>",
            "to": [to_email],
            "subject": "✅ Kanan H1 Monitor — No Changes Today",
            "html": "<p>All good! No H1 changes detected today.</p>",
        },
        timeout=30,
    )

def main():
    urls = get_urls()
    old_data = load_old()
    new_data = {}
    changes = []

    for url in urls:
        h1 = get_h1(url)
        new_data[url] = h1
        if url in old_data and old_data[url] != h1:
            changes.append(f"<b>{url}</b><br>OLD: {old_data[url]}<br>NEW: {h1}")

    save_new(new_data)
    if changes:
        send_email(changes)
    else:
        send_no_change_email()

if __name__ == "__main__":
    main()
