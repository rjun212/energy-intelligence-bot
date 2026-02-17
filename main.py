import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data/master_index.json"

# ==========================
# Utilities
# ==========================

def load_items():
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            payload = json.load(f)
            return payload.get("items", [])
    except:
        return []

def save_items(items):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, indent=2)

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
    print("CHAT TYPE:", update.effective_chat.type)
    print("TEXT:", update.message.text)

    text = update.message.text.strip()
    chat_type = update.effective_chat.type

    # ==========================
    # STORE messages from group
    # ==========================

    if text.startswith("STORE||"):
    try:
        # Split only first two delimiters
        _, title, url = text.split("||", 2)

        # Remove newlines from long Telegram URLs
        url = url.replace("\n", "").strip()

        items = load_items()

        new_item = {
            "title": title.strip(),
            "url": url
        }

        items.insert(0, new_item)
        save_items(items)

        print("STORE SAVED:", title)

    except Exception as e:
        print("STORE ERROR:", e)

    return


    # ==========================
    # Ignore group chatter
    # ==========================

    if chat_type != "private":
        return

    # ==========================
    # Private chat queries
    # ==========================

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
