import os
import telebot
from flask import Flask, request
import yt_dlp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# ប្រើប្រាស់ Webhook ជំនួស Polling ដើម្បីការពារបញ្ហា Conflict 409 នៅលើ Render
RENDER_URL = "https://badking-bot.onrender.com"  # URL របស់ Render អ្នក
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

# កំណត់ Webhook ពេលចាប់ផ្ដើម
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)


@app.route("/")
def index():
  return "Bot is running!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
  if request.headers.get("content-type") == "application/json":
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "", 200
  else:
    return "Forbidden", 403


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
          f"❌ មានបញ្ហាក្នុងការดาวน์โหลด: {str(e)}",
          message.chat.id,
          sent_msg.message_id,
      )
  else:
    bot.reply_to(
        message, "📌 សូមផ្ញើ Link TikTok មកទីនេះដើម្បីទាញយកវីដេអូគ្មាន Watermark!"
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
