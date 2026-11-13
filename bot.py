import os

# អាប់ដេត yt-dlp ស្វ័យប្រវត្តិពេល Start
os.system("pip install --upgrade yt-dlp")

import telebot
from flask import Flask, request
import yt_dlp
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

RENDER_URL = "https://badking-bot.onrender.com"  # ដាក់ URL Render របស់អ្នកឱ្យត្រូវ
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
  if (
      "tiktok.com" in text
      or "vt.tiktok.com" in text
      or "facebook.com" in text
      or "fb.watch" in text
  ):
    sent_msg = bot.reply_to(
        message, "⏳ កំពុងពិនិត្យ និងទាញយក... សូមរង់ចាំបន្តិច!"
    )

    try:
      headers = {
          "User-Agent": (
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
              " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
          )
      }

      # ដោះស្រាយ Facebook Share Link
      target_url = text
      if "facebook.com/share" in text or "fb.watch" in text:
        try:
          resp = requests.head(
              text, headers=headers, allow_redirects=True, timeout=5
          )
          target_url = resp.url
        except Exception:
          pass

      # ១. ករណីជា Link TikTok
      if "tiktok.com" in target_url or "vt.tiktok.com" in target_url:
        api_res = requests.get(
            f"https://www.tikwm.com/api/?url={target_url}", headers=headers
        ).json()

        if (
            "data" in api_res
            and "images" in api_res["data"]
            and api_res["data"]["images"]
        ):
          image_urls = api_res["data"]["images"]
          bot.edit_message_text(
              "📸 កំពុងផ្ញើរូបភាព TikTok ជាអាល់ប៊ុម...",
              message.chat.id,
              sent_msg.message_id,
          )

          media_group = []
          for i, img_url in enumerate(image_urls[:10]):
            if i == 0:
              media_group.append(
                  telebot.types.InputMediaPhoto(
                      img_url, caption="✅ រូបភាព TikTok មកហើយ!"
                  )
              )
            else:
              media_group.append(telebot.types.InputMediaPhoto(img_url))

          bot.send_media_group(message.chat.id, media_group)
          bot.delete_message(message.chat.id, sent_msg.message_id)
          return

      # ២. ករណី Facebook Video / Reels ឬ វីដេអូ TikTok ធម្មតា
      ydl_opts_video = {
          "format": "mp4/best",
          "outtmpl": "video.mp4",
          "quiet": True,
          "http_headers": headers,
      }
      with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([target_url])

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
        message,
        "📌 សូមផ្ញើ Link TikTok (វីដេអូ/រូបថត) ឬ Link Facebook (Video/Reels) មកទីនេះ!",
    )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
