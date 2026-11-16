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

            # ដោះស្រាយ Link Facebook Share ឱ្យវាទាញយក URL ពិតប្រាកដ (Expand Redirect Link)
            target_url = text
            if "facebook.com/share" in text or "fb.watch" in text:
                try:
                    resp = requests.get(text, headers=headers, allow_redirects=True, timeout=5)
                    target_url = resp.url
                except Exception:
                    pass

            # ១. ករណីជា Link TikTok
            if "tiktok.com" in target_url or "vt.tiktok.com" in target_url:
                api_res = requests.get(
                    f"https://www.tikwm.com/api/?url={target_url}", headers=headers
                ).json()

                if "data" in api_res:
                    data = api_res["data"]
                    
                    # ករណីជា Photo Album (ຫຼາຍរូប)
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

                    # ករណីទាញយកវីដេអូ TikTok
                    elif "play" in data:
                        video_url = data["play"]
                        music_url = data.get("music", "")

                        markup = None
                        if music_url:
                            markup = telebot.types.InlineKeyboardMarkup()
                            markup.add(telebot.types.InlineKeyboardButton("🎵 MUSIC", callback_data="get_music"))

                        global temp_music_storage
                        if 'temp_music_storage' not in globals():
                            temp_music_storage = {}
                        
                        sent_video = bot.send_video(
                            message.chat.id,
                            video_url,
                            supports_streaming=True,
                            caption=(
                                "✅ វីដេអូរបស់អ្នកមកហើយ!\n\n"
                                "Downloaded via: @badking_downloader_bot"
                            ),
                            reply_markup=markup
                        )
                        
                        temp_music_storage[sent_video.message_id] = music_url
                        bot.delete_message(message.chat.id, sent_msg.message_id)
                        return

            # ២. ករណី Facebook Video / Reels / Posts
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
                    message.chat.id,
                    video,
                    supports_streaming=True,
                    caption=(
                        "✅ វីដេអូរបស់អ្នកមកហើយ!\n\n"
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
            "📌 សូមផ្ញើ Link TikTok (វីដេអូ/រូបថត) ឬ Link Facebook (Video/Reels) មកទីនេះ!",
        )
