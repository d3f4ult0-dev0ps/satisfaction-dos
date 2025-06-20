import telebot
from telebot import types
import pandas as pd
import requests
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdv-p1UCSlH0c9RrZRnKzMOmi742qS63lLehLdTaLOF-1r_zg/formResponse"
teacher = "Sevinch | Integro A"

# Подгружаем комментарии из файла
with open("new_comments.txt", "r", encoding="utf-8") as f:
    comments = [line.strip() for line in f if line.strip()]

df = pd.read_excel("cleaned_data.xlsx")
log_file = "sent_log.txt"
names_log_file = "names_only_log.txt"
stop_requested = False

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚀 Send requests")
    bot.send_message(message.chat.id, "Hi! 👋 Click the button below to start sending:", reply_markup=markup)

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

        # Очищаем старые логи
        open(log_file, "w", encoding="utf-8").close()
        open(names_log_file, "w", encoding="utf-8").close()

        bot.send_message(message.chat.id, f"🚀 Sending {len(sample)} requests...")

        # Кнопка остановки
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("⛔ Terminate")
        bot.send_message(message.chat.id, "Press ⛔ to stop the process", reply_markup=markup)

        for idx, (_, row) in enumerate(sample.iterrows(), start=1):
            if stop_requested:
                bot.send_message(message.chat.id, "🛑 Sending stopped.")
                break

            name = row["name"]
            phone = row["phone"]
            comment = random.choice(comments)

            form_data = {
                "entry.1767106711": name,
                "entry.791639384": phone,
                "entry.10629657": comment,
                "entry.1888807124": teacher,
                "entry.282949261": "5"
            }

            response = requests.post(form_url, data=form_data)
            status = "✅ Success" if response.status_code in [200, 302] else f"❌ Error {response.status_code}"

            # Лог с полными данными
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"{idx}. {name} | {phone} | {comment}\n")

            # Лог только с именами
            with open(names_log_file, "a", encoding="utf-8") as name_log:
                name_log.write(f"{idx}. {name}\n")

            bot.send_message(message.chat.id, f"{status}: {name} — \"{comment}\"")

            pause = random.uniform(0.5, 2.0)
            bot.send_message(message.chat.id, f"⏳ Waiting {round(pause, 2)} sec...")
            time.sleep(pause)

        # Отправляем оба лога
        if not stop_requested:
            with open(log_file, "rb") as log:
                bot.send_document(message.chat.id, log)
            with open(names_log_file, "rb") as log2:
                bot.send_document(message.chat.id, log2)

        # Кнопка запуска заново
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("🚀 Send requests")
        bot.send_message(message.chat.id, "✅ Done! Ready for next round.", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")

bot.polling()
