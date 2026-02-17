import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data/master_index.json"

# ==========================
# Load Data
# ==========================

def load_items():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("items", [])

def format_items(items, limit=5):
    if not items:
        return "No items found."
    text = ""
    for it in items[:limit]:
        text += f"• {it['title']}\n"
    return text

# ==========================
# Telegram Handler
# ==========================

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    # If message is structured STORE payload from Bot 1
    if text.startswith("STORE||"):
        parts = text.split("||")
        if len(parts) == 3:
            title = parts[1]
            url = parts[2]

            items = load_items()

            new_item = {
                "title": title,
                "url": url
            }

            items.insert(0, new_item)

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"items": items}, f, indent=2)

        return

    # Normal query handling
    query = text.lower()
    items = load_items()

    if query == "latest":
        results = items

    elif query == "india":
        results = [x for x in items if "india" in x["title"].lower()]

    elif query == "solar":
        results = [x for x in items if "solar" in x["title"].lower()]

    elif query == "battery":
        results = [x for x in items if "battery" in x["title"].lower()]

    elif query == "flexibility":
        results = [
            x for x in items
            if "flexibility" in x["title"].lower()
            or "demand response" in x["title"].lower()
        ]

    else:
        await update.message.reply_text("Try: latest, india, solar, battery, flexibility")
        return

    await update.message.reply_text(format_items(results))


# ==========================
# Main
# ==========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("Energy Intelligence Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
