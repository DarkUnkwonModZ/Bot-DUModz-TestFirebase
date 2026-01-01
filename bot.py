import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import time
from datetime import datetime

# কনফিগারেশন
BOT_TOKEN = "8202203049:AAFoR-vtoNYZ2efSJBFb_Wb2VukWCXdRciA"
FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")
ADMIN_ID = 8504263842

# Firebase সেটআপ
try:
    if FIREBASE_JSON:
        cred_dict = json.loads(FIREBASE_JSON)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        print("Firebase Secret not found!")
        exit(1)
except Exception as e:
    print(f"Firebase Init Error: {e}")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user = message.from_user
        user_id = str(user.id)
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get()

        if doc.exists:
            bot.reply_to(message, f"স্বাগতম বন্ধু {user.first_name}! তুমি অলরেডি রেজিস্টার্ড।")
        else:
            user_data = {
                'id': user.id,
                'name': user.first_name,
                'username': user.username,
                'joined_at': datetime.now()
            }
            user_ref.set(user_data)
            bot.reply_to(message, "সফলভাবে Firebase-এ তোমার তথ্য সেভ করা হয়েছে!")
    except Exception as e:
        print(f"Error in start command: {e}")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "এডমিন প্যানেল সচল আছে বন্ধু!")

# বট রান করার ফাংশন (লুপ সহ)
def run_bot():
    print("বট স্টার্ট হচ্ছে...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"বট ক্রাশ করেছে: {e}. ৫ সেকেন্ড পর আবার চেষ্টা করছি...")
            time.sleep(5)

if __name__ == "__main__":
    run_bot()
