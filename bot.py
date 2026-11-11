import os
import logging
import requests
import telebot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN. Add it in Replit Secrets.")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "សួស្តី! Bot ត្រៀមរួចរាល់ហើយ។ សូមផ្ញើ Link TikTok មកបាន!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    if not text.startswith("http"):
        bot.reply_to(message, "សូមផ្ញើ Link វីដេអូឱ្យបានត្រឹមត្រូវ (មាន http:// ឬ https://)")
        return

    processing_msg = bot.reply_to(message, "⏳ កំពុងទាញយកទិន្នន័យ...")

    try:
        if "tiktok.com" in text or "vt.tiktok.com" in text:
            api_url = f"https://www.tikwm.com/api/?url={text}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(api_url, headers=headers, timeout=15)

            # ពិនិត្យមើល Status Code
            if response.status_code != 200:
                raise Exception(f"API HTTP Error: {response.status_code}")

            res_data = response.json()
            print("API Response:", res_data) # បង្ហាញទិន្នន័យក្នុង Console ដើម្បីងាយស្រួលដឹងមូលហេតុ

            if res_data.get("code") == 0:
                data = res_data.get("data", {})

                # ទាញយក Link វីដេអូគ្មាន Watermark
                video_url = data.get("play") or data.get("wmplay")
                title = data.get("title", "TikTok Video")

                if video_url:
                    bot.send_video(message.chat.id, video_url, caption=f"✅ {title}")
                else:
                    raise Exception("រកមិនឃើញតំណភ្ជាប់វីដេអូនៅក្នុង API ទេ។")
            else:
                raise Exception(f"TikWM API Error code: {res_data.get('code')}")
        else:
            # សម្រាប់ Link YouTube ឬផ្សេងៗ
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text="ℹ️ បច្ចុប្បន្ន Bot កំពុងផ្តោតលើការទាញយក TikTok ។ សូមផ្ញើ Link TikTok មកកាន់ទីនេះ!"
            )
            return

        try:
            bot.delete_message(message.chat.id, processing_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        logger.error(f"Detailed Error: {e}")
        print(f"ERROR OCCURRED: {e}") # បោះពុម្ព Error ចេញមកក្រៅ Console ឱ្យច្បាស់
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            text=f"❌ មានបញ្ហា៖ {str(e)[:100]}\nសូមពិនិត្យ Link ឡើងវិញ ឬลองផ្ញើ Video ផ្ទាល់មកកាន់ទីនេះ។"
        )

if __name__ == "__main__":
    print("Bot is running and listening for links...")
    bot.infinity_polling()