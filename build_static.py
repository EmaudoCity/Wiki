"""
Pre-renders the Django wiki into a static site under dist/.
"""
import os
import shutil
import sys

# Bootstrap Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wiki.settings")

import django
django.setup()

from django.test import Client
from encyclopedia import util

DIST = os.path.join(os.path.dirname(__file__), "dist")

# ── helpers ──────────────────────────────────────────────────────────────────

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(content if isinstance(content, bytes) else content.encode())

def fetch(client, url):
    r = client.get(url, follow=True)
    return r.content

# ── build ─────────────────────────────────────────────────────────────────────

if os.path.exists(DIST):
    shutil.rmtree(DIST)
os.makedirs(DIST)

client = Client(SERVER_NAME="localhost")
entries = util.list_entries()

# index
write(f"{DIST}/index.html", fetch(client, "/"))
print("  /  →  index.html")

# entry pages
os.makedirs(f"{DIST}/wiki", exist_ok=True)
for title in entries:
    html = fetch(client, f"/wiki/{title}")
    write(f"{DIST}/wiki/{title}/index.html", html)
    print(f"  /wiki/{title}/  →  wiki/{title}/index.html")

# search results (a representative page)
html = fetch(client, "/search?q=")
write(f"{DIST}/search/index.html", html)
print("  /search  →  search/index.html")

# new page form
html = fetch(client, "/new")
write(f"{DIST}/new/index.html", html)
print("  /new  →  new/index.html")

# 404 / error demo
html = fetch(client, "/wiki/__not_found__")
write(f"{DIST}/404.html", html)
print("  404  →  404.html")

# copy static assets
src_static = os.path.join(os.path.dirname(__file__), "staticfiles")
dst_static = os.path.join(DIST, "static")
shutil.copytree(src_static, dst_static)
print(f"  static/  →  dist/static/")

print(f"\nDone — {sum(len(fs) for _,_,fs in os.walk(DIST))} files written to dist/")
