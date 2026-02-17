# intelligence_processor.py
import json
import os
from datetime import datetime

DATA_DIR = "data"
INBOX_PATH = os.path.join(DATA_DIR, "inbox.json")
MASTER_PATH = os.path.join(DATA_DIR, "master_index.json")

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

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    inbox = load_json(INBOX_PATH, [])

    # For now master_index = inbox (later we’ll add embeddings/LLM)
    # Sort newest-first by date_detected
    def key(item):
        return item.get("date_detected", "")
    inbox_sorted = sorted(inbox, key=key, reverse=True)

    payload = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(inbox_sorted),
        "items": inbox_sorted,
    }
    save_json(MASTER_PATH, payload)
    print(f"Master index written: {MASTER_PATH} ({len(inbox_sorted)} items)")

if __name__ == "__main__":
    main()
