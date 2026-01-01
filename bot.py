import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import time
from datetime import datetime

# --- কনফিগারেশন ---
BOT_TOKEN = "8202203049:AAFoR-vtoNYZ2efSJBFb_Wb2VukWCXdRciA"
ADMIN_ID = 8504263842
LOG_CHANNEL = "@dumodzbotmanager" # বটের সব আপডেট এখানে যাবে
FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")

# --- Firebase সেটআপ ---
try:
    if FIREBASE_JSON:
        cred_dict = json.loads(FIREBASE_JSON)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    else:
        print("Error: Firebase Secret Not Found!")
        exit(1)
except Exception as e:
    print(f"Firebase Error: {e}")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# --- চ্যানেল আপডেট ফাংশন ---
def log_to_channel(text):
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 **Bot Update:**\n\n{text}")
    except Exception as e:
        print(f"Channel Log Error: {e}")

# --- কমান্ড হ্যান্ডলার ---

@bot.message_handler(commands=['start'])
def start(message):
    try:
        user = message.from_user
        user_id = str(user.id)
        
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get()

        if doc.exists:
            bot.reply_to(message, f"সালাম বন্ধু *{user.first_name}*! তুমি তো আমাদের পুরনো বন্ধু। স্বাগতম ফিরে আসার জন্য! 😊")
        else:
            # নতুন ইউজার সেভ করা
            user_data = {
                'id': user.id,
                'name': user.first_name,
                'username': f"@{user.username}" if user.username else "N/A",
                'joined_at': datetime.now()
            }
            user_ref.set(user_data)
            
            bot.reply_to(message, "স্বাগতম! তোমার তথ্য আমাদের ডাটাবেজে স্থায়ীভাবে সেভ করা হয়েছে। এখন থেকে তুমি নিরাপদ। ✅")
            
            # চ্যানেলে আপডেট পাঠানো
            log_to_channel(f"👤 **নতুন ইউজার!**\nনাম: {user.first_name}\nআইডি: `{user.id}`\nইউজারনেম: @{user.username if user.username else 'N/A'}")

    except Exception as e:
        log_to_channel(f"❌ **Error in Start Command:**\n`{e}`")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        total_users = len(list(db.collection('users').get()))
        bot.reply_to(message, f"😎 **এডমিন প্যানেল**\n\nমোট ইউজার: `{total_users}`\nস্ট্যাটাস: অনলাইন ✅")
    else:
        bot.reply_to(message, "❌ তুমি এই বটের এডমিন নও বন্ধু।")

# --- বট রান করা ---
if __name__ == "__main__":
    print("বট সচল হচ্ছে...")
    log_to_channel("✅ **বট সফলভাবে চালু হয়েছে এবং কাজ করছে!**")
    
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            log_to_channel(f"⚠️ **বট সাময়িকভাবে ক্রাশ করেছে!**\nরিস্টার্ট হচ্ছে...\nError: `{e}`")
            time.sleep(5)
