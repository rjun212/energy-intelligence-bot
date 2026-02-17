import json
import os
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data/master_index.json"

# ==========================
# Utility
# ==========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def filter_last_days(data, days=7):
    cutoff = datetime.utcnow() - timedelta(days=days)
    results = []
    for item in data:
        try:
            item_date = datetime.strptime(item["date_detected"], "%Y-%m-%d")
            if item_date >= cutoff:
                results.append(item)
        except:
            continue
    return results

def format_items(items, limit=5):
    if not items:
        return "No items found."
    text = ""
    for item in items[:limit]:
        text += f"• {item['title']}\n"
    return text

# ==========================
# Message Handler
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()
    data = load_data()
    recent = filter_last_days(data, 30)
if not recent:
    recent = data

    if query == "latest":
        results = sorted(recent, key=lambda x: x["relevance_score"], reverse=True)

    elif query == "india":
        results = [x for x in recent if x["geography"] == "India"]
        results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    elif query == "solar":
        results = [x for x in recent if "solar" in x.get("themes", []) or "renewables" in x.get("themes", [])]
        results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    elif query == "battery":
        results = [x for x in recent if "battery storage" in x.get("themes", [])]
        results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    elif query == "flexibility":
        results = [
            x for x in recent
            if "grid flexibility" in x.get("themes", [])
            or "demand flexibility" in x.get("themes", [])
            or "demand response" in x.get("themes", [])
        ]
        results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)

    else:
        await update.message.reply_text("Try: latest, india, solar, battery, flexibility")
        return

    response = format_items(results)
    await update.message.reply_text(response)

# ==========================
# Main
# ==========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Energy Intelligence Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
