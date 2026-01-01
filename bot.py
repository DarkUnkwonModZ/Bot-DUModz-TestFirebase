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
LOG_CHANNEL = "@dumodzbotmanager" 
FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")

# --- Firebase সেটআপ ---
try:
    if FIREBASE_JSON:
        cred_dict = json.loads(FIREBASE_JSON)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase Connected!")
    else:
        print("Error: Firebase Secret Not Found!")
        exit(1)
except Exception as e:
    print(f"Firebase Error: {e}")
    exit(1)

# বট অবজেক্ট তৈরি (Threaded=False দিলে অনেক সময় স্ট্যাবিলিটি বাড়ে)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown", threaded=True)

def log_to_channel(text):
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 **Bot Update:**\n\n{text}")
    except Exception as e:
        print(f"Log Error: {e}")

# --- ১. পিং কমান্ড (টেস্ট করার জন্য) ---
@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "Pong! 🏓 বট সচল আছে বন্ধু।")

# --- ২. মেইন স্টার্ট কমান্ড ---
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    # সাথে সাথে একটি রিপ্লাই দেওয়া যাতে ইউজার বুঝতে পারে বট কাজ করছে
    sent_msg = bot.reply_to(message, "একটু অপেক্ষা করো বন্ধু, তোমার তথ্য চেক করছি... 🔍")
    
    try:
        user_id = str(user.id)
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get()

        if doc.exists:
            bot.edit_message_text(f"সালাম বন্ধু *{user.first_name}*! তুমি অলরেডি আমাদের ডাটাবেজে আছো। স্বাগতম! 😊", 
                                  chat_id=message.chat.id, 
                                  message_id=sent_msg.message_id)
        else:
            user_data = {
                'id': user.id,
                'name': user.first_name,
                'username': f"@{user.username}" if user.username else "N/A",
                'joined_at': datetime.now()
            }
            user_ref.set(user_data)
            bot.edit_message_text(f"স্বাগতম বন্ধু *{user.first_name}*! তোমার তথ্য Firebase-এ স্থায়ীভাবে সেভ করা হলো। ✅", 
                                  chat_id=message.chat.id, 
                                  message_id=sent_msg.message_id)
            
            log_to_channel(f"👤 **নতুন ইউজার!**\nনাম: {user.first_name}\nআইডি: `{user.id}`")

    except Exception as e:
        bot.reply_to(message, "দুঃখিত বন্ধু, ডেটাবেজ কানেকশনে সমস্যা হচ্ছে। একটু পরে চেষ্টা করো।")
        log_to_channel(f"❌ **Error:** `{str(e)}` \nUser: {user.first_name}")

# --- ৩. বট রান করা ---
if __name__ == "__main__":
    print("বট চলছে...")
    # শুরুতে চ্যানেলে মেসেজ
    log_to_channel("✅ **বট রিস্টার্ট হয়েছে এবং এখন ১০০% রেসপন্স মুডে আছে!**")
    
    while True:
        try:
            # আগের সব পেন্ডিং মেসেজ ক্লিয়ার করার জন্য skip_pending=True
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
