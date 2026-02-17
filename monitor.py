import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText

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
r = requests.get(page, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
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
email = os.environ["EMAIL"]
password = os.environ["EMAIL_PASS"]
to = os.environ["TO_EMAIL"]

```
body = "\n\n".join(changes)
msg = MIMEText(body)
msg["Subject"] = "Kanan H1 Changes Detected"
msg["From"] = email
msg["To"] = to

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(email, password)
    server.send_message(msg)
```

def main():
urls = get_urls()
old_data = load_old()
new_data = {}
changes = []

```
for url in urls:
    h1 = get_h1(url)
    new_data[url] = h1

    if url in old_data 
```
