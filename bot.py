import os
import threading
import telebot
from flask import Flask
import yt_dlp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


@app.route("/")
def index():
  return "Bot is running!"


@bot.message_handler(func=lambda message: True)
def handle_message(message):
  text = message.text
  if "tiktok.com" in text or "vt.tiktok.com" in text:
    sent_msg = bot.reply_to(
        message, "⏳ កំពុងទាញយកវីដេអូ... សូមរង់ចាំបន្តិច!"
    )

    try:
      ydl_opts = {
          "format": "mp4",
          "outtmpl": "video.mp4",
          "quiet": True,
          "http_headers": {
              "User-Agent": (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
              )
          },
      }

      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([text])

      with open("video.mp4", "rb") as video:
        bot.send_video(
            message.chat.id, video, caption="✅ វីដេអូរបស់អ្នកមកហើយ!"
        )

      if os.path.exists("video.mp4"):
        os.remove("video.mp4")

      bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
      bot.edit_message_text(
          f"❌ មានបញ្ហាในการดาวน์โหลด: {str(e)}",
          message.chat.id,
          sent_msg.message_id,
      )
  else:
    bot.reply_to(
        message,
        "📌 សូមផ្ញើ Link TikTok មកទីនេះដើម្បីទាញយកវីដេអូគ្មាន Watermark!",
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
