import logging
import sqlite3
import re
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# 🔴 PASTE YOUR SECOND BOT TOKEN HERE
BOT_TOKEN = "8551777477:AAH6fQv6APhQ3DFyhx5LpUaB__IA21LIS14"

logging.basicConfig(level=logging.INFO)

# ==========================
# DATABASE
# ==========================

conn = sqlite3.connect("intelligence.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    title TEXT,
    topic TEXT,
    timestamp TEXT
)
""")
conn.commit()

# ==========================
# SIMPLE TOPIC CLASSIFIER
# ==========================

def classify_topic(text):
    text = text.lower()

    if "nuclear" in text:
        return "nuclear"
    if "battery" in text or "storage" in text:
        return "storage"
    if "renewable" in text or "solar" in text or "wind" in text:
        return "renewables"
    if "suryaghar" in text:
        return "suryaghar"
    if "energy stack" in text:
        return "energy_stack"

    return "general"

# ==========================
# HANDLER
# ==========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""

    urls = re.findall(r'(https?://\S+)', text)

    if not urls:
        await update.message.reply_text(
            "Send or forward a message containing a link to save it."
        )
        return

    link = urls[0]

    # Dedup check
    cursor.execute("SELECT 1 FROM items WHERE url=?", (link,))
    if cursor.fetchone():
        await update.message.reply_text("Already saved.")
        return

    words = text.lower().split()

    if words and words[0] == "save" and len(words) > 1:
        topic = words[1]
    else:
        topic = classify_topic(text)

    title = text[:200]

    cursor.execute(
        "INSERT INTO items (url, title, topic, timestamp) VALUES (?, ?, ?, ?)",
        (link, title, topic, datetime.utcnow().isoformat())
    )
    conn.commit()

    await update.message.reply_text(f"Saved under topic: {topic}")

# ==========================
# MAIN
# ==========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.ALL, handle_message)
    )

    print("Intelligence bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
