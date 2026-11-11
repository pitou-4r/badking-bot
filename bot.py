import os
import threading
import telebot
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def index():
  return "Bot is running!"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
  text = message.text
  if "tiktok.com" in text:
    bot.reply_to(message, "⏳ កំពុងទាញយកវីដេអូ... សូមរង់ចាំបន្តិច!")
  else:
    bot.reply_to(
        message, "📌 សូមផ្ញើ Link TikTok មកទីនេះដើម្បីទាញយកគ្មាន Watermark!"
    )


if __name__ == "__main__":
  threading.Thread(
      target=bot.infinity_polling,
      kwargs={
          "skip_pending": True,
      },
  ).start()
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
