import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import time
from datetime import datetime

# --- ১. কনফিগারেশন ---
BOT_TOKEN = "8202203049:AAFoR-vtoNYZ2efSJBFb_Wb2VukWCXdRciA"
ADMIN_ID = 8504263842
LOG_CHANNEL = "@dumodzbotmanager" 
KEY_FILE = "firebase_key.json" # ফাইলের নাম

# --- ২. Firebase সেটআপ (সরাসরি ফাইল থেকে) ---
db = None
try:
    if os.path.exists(KEY_FILE):
        # যদি ফাইলটি রিপোজিটরিতে থাকে তবে এখান থেকে লোড হবে
        cred = credentials.Certificate(KEY_FILE)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print(f"✅ Firebase Connected using {KEY_FILE}!")
    else:
        # ফাইল না থাকলে গিটহাব সিক্রেট থেকে চেষ্টা করবে
        FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if FIREBASE_JSON:
            cred_info = json.loads(FIREBASE_JSON.strip())
            cred = credentials.Certificate(cred_info)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("✅ Firebase Connected using GitHub Secrets!")
        else:
            print("❌ Error: No Firebase Key File or Secret found!")
            exit(1)
except Exception as e:
    print(f"❌ Firebase Initialization Failed: {e}")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

def log_to_channel(text):
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 **Bot Log:**\n\n{text}")
    except Exception as e:
        print(f"Log Error: {e}")

# --- ৩. কমান্ড হ্যান্ডলারস ---

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 **Pong!**\nবট এখন ফাইল থেকে ডাটা লোড করছে বন্ধু।")

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)
    sent_msg = bot.reply_to(message, "🔍 তোমার তথ্য ডাটাবেজে চেক করছি...")
    
    try:
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get(timeout=10)

        if doc.exists:
            bot.edit_message_text(f"সালাম বন্ধু *{user.first_name}*! তুমি আগে থেকেই ডাটাবেজে আছো। 😊", 
                                  message.chat.id, sent_msg.message_id)
        else:
            new_data = {
                'id': user.id,
                'name': user.first_name,
                'username': f"@{user.username}" if user.username else "N/A",
                'joined_at': datetime.now()
            }
            user_ref.set(new_data)
            bot.edit_message_text(f"স্বাগতম বন্ধু *{user.first_name}*! তোমার তথ্য সেভ করা হয়েছে। ✅", 
                                  message.chat.id, sent_msg.message_id)
            log_to_channel(f"👤 **নতুন ইউজার:** {user.first_name} (`{user.id}`)")

    except Exception as e:
        bot.edit_message_text(f"❌ Error: `{str(e)}`", message.chat.id, sent_msg.message_id)

# --- ৪. বট চালানো ---
if __name__ == "__main__":
    print("Bot is running...")
    log_to_channel("✅ **বট সফলভাবে চালু হয়েছে!**\nমোড: ফাইল-বেসড লোডিং")
    
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception as e:
            time.sleep(5)
