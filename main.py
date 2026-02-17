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
    print("----- MESSAGE RECEIVED -----")
    print("CHAT TYPE:", update.effective_chat.type)
    print("TEXT:", repr(update.message.text))
    print("----------------------------")

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
