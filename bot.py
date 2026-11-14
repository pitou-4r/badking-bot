# ១. ករណីជា Link TikTok (Photo Album ឬ Live Photo / Video)
      if "tiktok.com" in target_url or "vt.tiktok.com" in target_url:
        api_res = requests.get(
            f"https://www.tikwm.com/api/?url={target_url}", headers=headers
        ).json()

        if "data" in api_res:
          data = api_res["data"]
          
          # ពិនិត្យមើលថាតើវាជា Photo Album (ຫຼາຍរូប) ឬអត់
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
                            "✅ រូបភាព TikTok មកហើយ!\n\nDownloaded via:"
                            " @badking_downloader_bot"
                        ),
                    )
                )
              else:
                media_group.append(telebot.types.InputMediaPhoto(img_url))

            bot.send_media_group(message.chat.id, media_group)
            bot.delete_message(message.chat.id, sent_msg.message_id)
            return

          elif "play" in data:
            # បើជាវីដេអូ ឬ Live Photo (ទម្រង់មានចលនា)
            video_url = data["play"]
            video_resp = requests.get(video_url, headers=headers)
            with open("live_photo.mp4", "wb") as f:
              f.write(video_resp.content)

            with open("live_photo.mp4", "rb") as video:
              bot.send_video(
                  message.chat.id,
                  video,
                  caption=(
                      "✅ Live Photo / វីដេអូ TikTok មកហើយ!\n\nDownloaded via:"
                      " @badking_downloader_bot"
                  ),
              )

            if os.path.exists("live_photo.mp4"):
              os.remove("live_photo.mp4")

            bot.delete_message(message.chat.id, sent_msg.message_id)
            return
