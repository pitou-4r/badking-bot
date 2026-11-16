import os
import shutil

os.system("pip install --upgrade yt-dlp")
os.system("yt-dlp -U")

# ចម្លង Cookie សម្រាប់ Facebook ពេល Bot ចាប់ផ្តើម
try:
    if os.path.exists("/etc/secrets/cookies.txt"):
        shutil.copy("/etc/secrets/cookies.txt", "/tmp/cookies.txt")
    elif os.path.exists("cookies.txt"):
        shutil.copy("cookies.txt", "/tmp/cookies.txt")
except Exception as e:
    print(f"Cookie copy error: {e}")

import telebot
from flask import Flask, request
import yt_dlp

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


@app.message_handler(func=lambda message: True)
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
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            target_url = text

            # ១. ករណីជា Link TikTok
            if "tiktok.com" in target_url or "vt.tiktok.com" in target_url:
                ydl_opts_tiktok = {
                    "format": "best[filesize<50M]/best",
                    "outtmpl": "tiktok_video.mp4",
                    "quiet": True,
                    "nocheckcertificate": True,
                    "http_headers": headers,
                }
                with yt_dlp.YoutubeDL(ydl_opts_tiktok) as ydl:
                    ydl.download([target_url])

                with open("tiktok_video.mp4", "rb") as video:
                    bot.send_video(
                        message.chat.id,
                        video,
                        supports_streaming=True,
                        caption=(
                            "✅ វីដេអូ TikTok មកហើយ!\n\n"
                            "Downloaded via: @badking_downloader_bot"
                        ),
                    )

                if os.path.exists("tiktok_video.mp4"):
                    os.remove("tiktok_video.mp4")

                bot.delete_message(message.chat.id, sent_msg.message_id)
                return

            # ២. ករណី Facebook Video / Reels (บังคับ format ឱ្យស្របតាម Telegram Mobile Player)
            elif "facebook.com" in target_url or "fb.watch" in target_url:
                cookie_file_path = "/tmp/cookies.txt" if os.path.exists("/tmp/cookies.txt") else None

                ydl_opts_video = {
                    "format": "bestvideo[ext=mp4][filesize<40M]+bestaudio[ext=m4a]/best[ext=mp4][filesize<50M]/best",
                    "outtmpl": "video.mp4",
                    "quiet": True,
                    "nocheckcertificate": True,
                    "cookiefile": cookie_file_path,
                    "http_headers": headers,
                }
                with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
                    ydl.download([target_url])

                with open("video.mp4", "rb") as video:
                    bot.send_video(
                        message.chat.id,
                        video,
                        supports_streaming=True,
                        caption=(
                            "✅ វីដេអូ Facebook មកហើយ!\n\n"
                            "Downloaded via: @badking_downloader_bot"
                        ),
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
            "📌 សូមផ្ញើ Link TikTok ឬ Link Facebook (Video/Reels) មកទីនេះ!",
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
