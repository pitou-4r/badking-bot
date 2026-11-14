import os
import telebot
import yt_dlp

TELEBOT_TOKEN = "9191000315:AAGAXNtVEVit336LhjHbSsVuyF0VpawLMw"  # ដាក់ Token របស់អ្នកនៅទីនេះ
bot = telebot.TeleBot(TELEBOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "សួស្តី! ខ្ញុំគឺ Badking Downloader Bot 🤖\nសូមផ្ញើ Link TikTok ឬ Facebook មកដើម្បីទាញយក!")

@bot.message_handler(func=lambda message: True)
def download_content(message):
    url = message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "❌ សូមផ្ញើ Link ឱ្យបានត្រឹមត្រូវ!")
        return

    sent_msg = bot.reply_to(message, "⏳ កំពុងទាញយកទិន្នន័យ សូមរង់ចាំបន្តិច...")

    # កំណត់ Configuration សម្រាប់ yt-dlp ឱ្យទាញយករូបភាព ឬ វីដេអូ
    ydl_opts = {
        'outtmpl': 'downloaded_media',
        'format': 'best',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        caption_text = "Downloaded via: @badking_downloader_bot"

        # ตรวจสอบប្រភេទไฟล์ដើម្បីផ្ញើជា Video ឬ Photo
        if filename.endswith(('.mp4', '.mkv', '.webm', '.mov', '.webp', '.gif')):
            # បើជាប្រភេទមានចលនា ឬ វីដេអូ/GIF
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption=caption_text)
        else:
            # បើជាប្រភេទរូបភាពធម្មតា ឬ Slide
            with open(filename, 'rb') as f:
                bot.send_photo(message.chat.id, f, caption=caption_text)

        bot.delete_message(message.chat.id, sent_msg.message_id)

        # លុបឯកសារចេញពី Server ក្រោយពេលផ្ញើរួច
        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        bot.edit_message_text(f"❌ កើតកំហុសក្នុងការទាញយក៖ {str(e)}", message.chat.id, sent_msg.message_id)

print("Badking Downloader Bot is running...")
bot.infinity_polling()
