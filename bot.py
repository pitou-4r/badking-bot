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
      ydl_opts = {
          "quiet": True,
          "http_headers": {
              "User-Agent": (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
              )
          },
      }

      image_urls = []

      # ប្រើ yt-dlp ទាញយក info សិន
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(text, download=False)
        if "image_post_info" in info and info["image_post_info"]:
          for img in info["image_post_info"]:
            if "display_image" in img and "url" in img["display_image"]:
              image_urls.append(img["display_image"]["url"])

      # បើ yt-dlp រកមិនឃើញ ប្រើ TikWM API ជំនួយយក Image URLs
      if not image_urls:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(
            f"https://www.tikwm.com/api/?url={text}", headers=headers
        ).json()
        if "data" in res and "images" in res["data"]:
          image_urls = res["data"]["images"]

      # ប្រសិនបើរកឃើញរូបភាព ផ្ញើវាជា Media Group (Album)
      if image_urls:
        bot.edit_message_text(
            "📸 កំពុងផ្ញើរូបភាពជាអាល់ប៊ុម...",
            message.chat.id,
            sent_msg.message_id,
        )

        # កំណត់ទម្រង់ជា Media Group (Telegram ដាក់បានយ៉ាងច្រើន ១០ សន្លឹកក្នុងមួយសារ)
        media_group = []
        for i, img_url in enumerate(image_urls[:10]):
          if i == 0:
            # អាចដាក់ Caption នៅលើរូបដំបូងបង្អស់
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
        # ករណីជាវីដេអូធម្មតា
        ydl_opts_video = {
            "format": "mp4",
            "outtmpl": "video.mp4",
            "quiet": True,
            "http_headers": ydl_opts["http_headers"],
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
