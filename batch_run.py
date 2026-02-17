# batch_run.py
import json
import os
import re
import time
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs, unquote

import feedparser
import requests

DATA_DIR = "data"
INBOX_PATH = os.path.join(DATA_DIR, "inbox.json")
SEEN_PATH = os.path.join(DATA_DIR, "seen.json")

# Keep it simple + low-noise
KEYWORDS = [
    "solar",
    "rooftop solar",
    "battery",
    "battery storage",
    "storage",
    "flexibility",
    "demand flexibility",
    "grid flexibility",
    "demand response",
    "india",
]

# Google News RSS search feeds (last 1 day). Add/remove freely.
# Tip: keep query focused; Google News can be noisy otherwise.
GOOGLE_NEWS_FEEDS = [
    "https://news.google.com/rss/search?q=solar+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=rooftop+solar+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=battery+storage+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=demand+response+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=grid+flexibility+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
    "https://news.google.com/rss/search?q=demand+flexibility+india+when:1d&hl=en-IN&gl=IN&ceid=IN:en",
]

UA = os.getenv("USER_AGENT", "Mozilla/5.0 (energy-intel-bot)")


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(INBOX_PATH):
        with open(INBOX_PATH, "w", encoding="utf-8") as f:
            f.write("[]")
    if not os.path.exists(SEEN_PATH):
        with open(SEEN_PATH, "w", encoding="utf-8") as f:
            f.write("{}")


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def clean_title(title: str) -> str:
    if not title:
        return ""
    t = re.sub(r"\s+", " ", title).strip()
    return t


def keyword_match(title: str) -> bool:
    t = (title or "").lower()
    return any(k in t for k in KEYWORDS)


def extract_real_url(url: str) -> str:
    """
    Google News RSS items often have URLs like:
    https://news.google.com/rss/articles/... ?oc=5&...
    We try to resolve redirects to get the publisher URL.
    """
    if not url:
        return url

    # If it's already not google, keep it.
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return url

    if "news.google.com" not in host:
        return url

    try:
        # HEAD may fail on some sources; GET with small timeout works better.
        r = requests.get(url, allow_redirects=True, timeout=12, headers={"User-Agent": UA})
        final = r.url
        return final or url
    except Exception:
        return url


def stable_id(title: str, url: str) -> str:
    raw = (clean_title(title) + "|" + (url or "")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def main():
    ensure_data_files()
    inbox = load_json(INBOX_PATH, [])
    seen = load_json(SEEN_PATH, {})  # id -> first_seen_ts

    new_items = []
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    for feed_url in GOOGLE_NEWS_FEEDS:
        d = feedparser.parse(feed_url)
        for e in d.entries:
            title = clean_title(getattr(e, "title", "") or "")
            link = getattr(e, "link", "") or ""
            if not title or not link:
                continue

            # Filter noise early
            if not keyword_match(title):
                continue

            real_url = extract_real_url(link)

            item_id = stable_id(title, real_url)

            if item_id in seen:
                continue

            item = {
                "id": item_id,
                "title": title,
                "url": real_url,
                "source_type": "web",
                "domain": urlparse(real_url).netloc.lower() if real_url else "",
                "date_detected": now_iso(),
                "keywords_hit": [k for k in KEYWORDS if k in title.lower()],
            }

            seen[item_id] = item["date_detected"]
            new_items.append(item)

    # Prepend newest items to inbox
    if new_items:
        inbox = new_items + inbox
        # Keep inbox bounded
        inbox = inbox[:500]

    save_json(INBOX_PATH, inbox)
    save_json(SEEN_PATH, seen)

    print(f"New items: {len(new_items)}")
    print(f"Inbox total: {len(inbox)}")


if __name__ == "__main__":
    main()
