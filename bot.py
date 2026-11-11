import os
import telebot
import yt_dlp

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


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
  print("Bot is running...")
  bot.infinity_polling(skip_pending=True)
