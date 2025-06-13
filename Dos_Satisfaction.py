import telebot
from telebot import types
import pandas as pd
import requests
import random
import time
from os import getenv
from dotenv import load_dotenv
load_dotenv()

TOKEN = getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)


form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdv-p1UCSlH0c9RrZRnKzMOmi742qS63lLehLdTaLOF-1r_zg/formResponse"
teacher = "Sevinch | Integro A"

comments = [
    "Absolutely wonderful lessons!",
    "Inspiring teaching style 👏",
    "Super clear and engaging!",
    "Top-tier education! ⭐",
    "Always helpful and kind",
    "Explains really well!",
    "Makes everything easier ✨",
    "Really enjoyed the class",
    "Very professional teacher",
    "Would love to learn again!",
    "Learned a lot 🙌",
    "Crystal clear explanations!",
    "Best teacher ever 💯",
    "Very supportive mentor",
    "Respect for your work 🙏",
    "Brilliant sessions!",
    "Always encouraging 💪",
    "Best of the bests 🏆",
    "Interactive and fun class",
    "Appreciated every lesson!",
    "Really dedicated teacher 👌",
    "Knowledge + passion = 🔥",
    "Clear and effective teaching",
    "Loved the environment!",
    "Perfect pace and clarity",
    "Consistently excellent",
    "Highly recommended 💫",
    "Great experience!",
    "10/10 teacher!",
    "Made complex things simple 😊",
    "Excellent communication 🗣️",
    "Strong teaching method",
    "Patient and professional",
    "Always answers questions",
    "Very responsive 💡",
    "Much respect 🙏",
    "True education 💥",
    "Can’t ask for more!",
    "Truly thankful 💖",
    "Respect for her patience 🙌",
    "On another level!",
    "Legendary educator 👑",
    "Focused and clear!",
    "Absolutely 💎 quality",
    "Such a warm person 🫶",
    "Total gamechanger",
    "Teaching goals 🎯",
    "Genius-level class",
    "Will never forget her lessons 💭"
]

df = pd.read_excel("data.xlsx")

stop_requested = False  # глобальный флаг остановки

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Send requests")
    bot.send_message(message.chat.id, "Hi! 👋, Click the button below to start sending:", reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text == "🚀 Send requests")
def ask_request_amount(message):
    bot.send_message(message.chat.id, "🔢 How many requests do I need to send?")
    bot.register_next_step_handler(message, process_requests)

@bot.message_handler(func=lambda msg: msg.text == "⛔ Terminate")
def stop_sending(message):
    global stop_requested
    stop_requested = True
    bot.send_message(message.chat.id, "🛑 Process is terminating.")

def process_requests(message):
    global stop_requested
    stop_requested = False

    try:
        count = int(message.text)
        sample = df.sample(n=min(count, len(df)))
        bot.send_message(message.chat.id, f"🚀 Sending {len(sample)} requests...")

        # Показываем кнопку "⛔ Остановить"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("⛔ Terminate")
        bot.send_message(message.chat.id, "Press the ⛔ button to stop the process", reply_markup=markup)

        for _, row in sample.iterrows():
            if stop_requested:
                bot.send_message(message.chat.id, "🛑 The process is stopped.")
                break

            form_data = {
                "entry.1767106711": row["name"],
                "entry.791639384": row["phone"],
                "entry.10629657": random.choice(comments),
                "entry.1888807124": teacher,
                "entry.282949261": "5"
            }

            response = requests.post(form_url, data=form_data)
            status = "✅ Success" if response.status_code in [200, 302] else f"❌ Error {response.status_code}"
            bot.send_message(message.chat.id, f"{status}: {row['name']}")

            pause = random.randint(2, 5)
            bot.send_message(message.chat.id, f"⏳ Waiting {pause} sec...")
            time.sleep(pause)

        # Возврат к обычной клавиатуре
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🚀 Send requests")
        bot.send_message(message.chat.id, "✅ Ready for the next launch", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

bot.polling()
