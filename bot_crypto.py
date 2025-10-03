import os
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from telegram.ext import Updater, CommandHandler
from flask import Flask
import threading
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8281238133:AAHCc2ue2frmgLXvLEG_CQl61NkRS8dikC4"
NEWS_URL = "https://cointelegraph.com/rss"

def get_latest_news(limit=5):
    try:
        res = requests.get(NEWS_URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as e:
        logger.exception("Gagal fetch RSS: %s", e)
        return []
    soup = BeautifulSoup(res.content, "xml")

    items = soup.find_all("item")[:limit]
    news_list = []

    for item in items:
        title = item.title.text.strip() if item.title else "Berita crypto terbaru"
        link = item.link.text.strip() if item.link else ""
        desc = item.description.text.strip() if item.description else ""

        
        img_url = ""
        if "<img" in desc:
            soup_desc = BeautifulSoup(desc, "html.parser")
            img_tag = soup_desc.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag["src"]

        NEWS_URL = "https://cointelegraph.com/rss"
        try:
            translated = GoogleTranslator(source="auto", target="id").translate(title)
        except Exception:
            translated = title

        if len(translated) > 100:
            translated = translated[:97] + "..."

        caption = f"{translated}\n\n#UTASOCT25_4549325\n{link}"
        news_list.append((img_url, caption))

    return news_list

def start(update, context):
    update.message.reply_text(
        "👋 Halo! Selamat datang di Bot Crypto.\n"
        "Ketik /berita untuk melihat 5 berita crypto terbaru 🚀"
    )

def berita(update, context):
    news_items = get_latest_news(limit=5)
    if not news_items:
        update.message.reply_text("❌ Tidak ada berita terbaru.")
        return
    for img, cap in news_items:
        try:
            if img:
                context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=cap)
            else:
                update.message.reply_text(cap)
            time.sleep(0.5)
        except Exception as e:
            logger.exception("Gagal kirim berita: %s", e)
           
            try:
                update.message.reply_text(cap)
            except Exception:
                pass

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("berita", berita))
    logger.info("Starting Telegram updater...")
    updater.start_polling()
    updater.idle()

app = Flask(__name__)

@app.route('/')
def home():
    return "Crypto Bot is running!"

if __name__ == '__main__':
    
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get('PORT', 10000))
    logger.info("Starting Flask on port %s", port)
    app.run(host='0.0.0.0', port=port)
