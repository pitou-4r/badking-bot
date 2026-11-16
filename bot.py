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
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

RENDER_URL = "https://badking-bot.onrender.com"
WEBHOOK_URL = f"{RENDER_URL}/{TOKEN}"

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# Global storage សម្រាប់ເກັບ Link MP3 បណ្ដោះអាសន្នតាម message_id
temp_music_storage = {}


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


@bot.callback_query_handler(func=lambda call: call.data == "get_music")
def callback_query(call):
    try:
        msg_id = call.message.message_id
        if msg_id in temp_music_storage:
            music_url = temp_music_storage[msg_id]
            
            bot.answer_callback_query(call.id, "🎵 កំពុងទាញយក MP3 សូមរង់ចាំបន្តិច...")
            
            headers = {"User-Agent": "Mozilla/5.0"}
            music_resp = requests.get(music_url, headers=headers)
            with open("music.mp3", "wb") as f:
                f.write(music_resp.content)

            with open("music.mp3", "rb") as audio:
                bot.send_audio(
                    call.message.chat.id,
                    audio,
                    caption="🎵 តន្ត្រី TikTok មកហើយ!\n\nDownloaded via: @badking_downloader_bot",
                    title="TikTok Audio"
                )

            if os.path.exists("music.mp3"):
                os.path.remove("music.mp3")
        else:
            bot.answer_callback_query(call.id, "❌ រកមិនឃើញតន្ត្រីសម្រាប់វីដេអូនេះទេ!", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ មានបញ្ហា: {str(e)}", show_alert=True)


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
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            }

            target_url = text

            # ១. ករណីជា Link TikTok (ប្រើ tikwm API ដើម្បីស្រួលទាញយកទាំង Video និង Music URL មកជាមួយគ្នា)
            if "tiktok.com" in target_url or "vt.tiktok.com" in target_url:
                api_res = requests.get(
                    f"https://www.tikwm.com/api/?url={target_url}", headers=headers
                ).json()

                if "data" in api_res:
                    data = api_res["data"]
                    
                    # ករណីជារូបភាព (Photo Slides)
                    if "images" in data and data["images"]:
                        image_urls = data["images"]
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
                                        img_url,
                                        caption=(
                                            "✅ រូបភាព TikTok មកហើយ!\n\n"
                                            "Downloaded via: @badking_downloader_bot"
                                        ),
                                    )
                                )
                            else:
                                media_group.append(telebot.types.InputMediaPhoto(img_url))

                        bot.send_media_group(message.chat.id, media_group)
                        bot.delete_message(message.chat.id, sent_msg.message_id)
                        return

                    # ករណីជាវីដេអូ TikTok
                    elif "play" in data:
                        video_download_url = data.get("hdplay") or data["play"]
                        music_url = data.get("music", "")

                        vid_resp = requests.get(video_download_url, headers=headers)
                        with open("tiktok_video.mp4", "wb") as f:
                            f.write(vid_resp.content)

                        # បង្កើតប៊ូតុង Open Music
                        markup = None
                        if music_url:
                            markup = telebot.types.InlineKeyboardMarkup()
                            markup.add(telebot.types.InlineKeyboardButton("🎵 Open Music", callback_data="get_music"))

                        with open("tiktok_video.mp4", "rb") as video:
                            sent_video = bot.send_video(
                                message.chat.id,
                                video,
                                supports_streaming=True,
                                width=720,
                                height=1280,
                                caption=(
                                    "✅ វីដេអូ TikTok មកហើយ!\n\n"
                                    "Downloaded via: @badking_downloader_bot"
                                ),
                                reply_markup=markup
                            )
                        
                        # រកទុក Link ភ្លេងភ្ជាប់នឹង message_id របស់វីដេអូ
                        temp_music_storage[sent_video.message_id] = music_url

                        if os.path.exists("tiktok_video.mp4"):
                            os.remove("tiktok_video.mp4")

                        bot.delete_message(message.chat.id, sent_msg.message_id)
                        return

            # ២. ករណី Facebook Video / Reels
            elif "facebook.com" in target_url or "fb.watch" in target_url:
                cookie_file_path = "/tmp/cookies.txt" if os.path.exists("/tmp/cookies.txt") else None

                ydl_opts_video = {
                    "format": "best[filesize<50M]/best",
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
                        width=720,
                        height=1280,
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
