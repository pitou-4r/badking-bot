import os
import telebot
from flask import Flask, request
import yt_dlp
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

RENDER_URL = "https://badking-bot.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

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
        message, "⏳ កំពុងពិនិត្យ និងទាញយក... សូមរង់ចាំបន្តិច!"
    )

    try:
      # ឆែកមើលមុនសិន ប្រសិនបើមានคำថា photo ក្នុង URL ឬជា Link រូបថត ប្រើ API ផ្ទាល់
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
          )
      }
      api_res = requests.get(
          f"https://www.tikwm.com/api/?url={text}", headers=headers
      ).json()

      # ពិនិត្យថាតើក្នុង API មាន images (Photo slide) ដែរឬទេ
      if "data" in api_res and "images" in api_res["data"] and api_res["data"]["images"]:
        image_urls = api_res["data"]["images"]
        bot.edit_message_text(
            "📸 កំពុងផ្ញើរូបភាពជាអាល់ប៊ុម...",
            message.chat.id,
            sent_msg.message_id,
        )

        media_group = []
        for i, img_url in enumerate(image_urls[:10]):
          if i == 0:
            media_group.append(
                telebot.types.InputMediaPhoto(
                    img_url, caption="✅ រូបភាពរបស់អ្នកមកហើយ!"
                )
            )
          else:
            media_group.append(telebot.types.InputMediaPhoto(img_url))

        bot.send_media_group(message.chat.id, media_group)
        bot.delete_message(message.chat.id, sent_msg.message_id)

      else:
        # បើមិនមែនជារូបថត គឺទាញយកជាវីដេអូធម្មតាជាមួយ yt-dlp
        ydl_opts_video = {
            "format": "mp4",
            "outtmpl": "video.mp4",
            "quiet": True,
            "http_headers": headers,
        }
        with yt_dlp.YoutubeDL(ydl_opts_video) as ydl_v:
          ydl_v.download([text])

        with open("video.mp4", "rb") as video:
          bot.send_video(
              message.chat.id, video, caption="✅ វីដេអូរបស់អ្នកមកហើយ!"
          )

        if os.path.exists("video.mp4"):
          os.remove("video.mp4")

        bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
      bot.edit_message_text(
          f"❌ មានបញ្ហា: {str(e)}", message.chat.id, sent_msg.message_id
      )
  else:
    bot.reply_to(
        message, "📌 សូមផ្ញើ Link TikTok (វីដេអូ ឬ រូបថត) មកទីនេះដើម្បីទាញយក!"
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
