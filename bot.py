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
FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT")

# --- ২. Firebase সেটআপ (নিশ্চিত করা হয়েছে) ---
db = None
try:
    if FIREBASE_JSON:
        # JSON লোড করার সময় এরর এড়াতে টাইট হ্যান্ডলিং
        cred_info = json.loads(FIREBASE_JSON)
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase Connected Successfully!")
    else:
        print("❌ Error: Firebase Secret Not Found in GitHub!")
        exit(1)
except Exception as e:
    print(f"❌ Firebase Initialization Failed: {e}")
    exit(1)

# বট অবজেক্ট (পার্স মোড সহ)
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# চ্যানেলে লগ পাঠানোর ফাংশন
def log_to_channel(text):
    try:
        bot.send_message(LOG_CHANNEL, f"🚀 **Bot Log:**\n\n{text}")
    except Exception as e:
        print(f"Log Error: {e}")

# --- ৩. কমান্ড হ্যান্ডলারস ---

@bot.message_handler(commands=['ping'])
def ping(message):
    bot.reply_to(message, "🏓 **Pong!**\nবট একদম ঠিকঠাক কাজ করছে বন্ধু।")

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)
    
    # প্রাথমিক মেসেজ
    sent_msg = bot.reply_to(message, "🔍 তোমার তথ্য ডাটাবেজে চেক করছি, একটু দাড়াও বন্ধু...")
    
    try:
        # ফায়ারবেস থেকে ডেটা খোঁজা (টাইমআউট ফিক্স)
        user_ref = db.collection('users').document(user_id)
        doc = user_ref.get(timeout=15) # ১৫ সেকেন্ডের মধ্যে রেসপন্স না আসলে এরর দিবে

        if doc.exists:
            # যদি ইউজার থাকে
            data = doc.to_dict()
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                text=f"সালাম বন্ধু *{user.first_name}*!\n\nতুমি আমাদের ডাটাবেজে আগে থেকেই আছো। তোমার তথ্য নিরাপদ। তুমি বটটি নিশ্চিন্তে ব্যবহার করতে পারো! 😊"
            )
        else:
            # নতুন ইউজার হলে সেভ করা
            new_data = {
                'id': user.id,
                'name': user.first_name,
                'last_name': user.last_name or "",
                'username': f"@{user.username}" if user.username else "N/A",
                'joined_at': datetime.now(),
                'status': 'active'
            }
            user_ref.set(new_data)
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=sent_msg.message_id,
                text=f"স্বাগতম বন্ধু *{user.first_name}*! 👋\n\nতোমাকে প্রথমবারের মতো আমাদের সিস্টেমে যুক্ত করা হলো। এখন থেকে তোমার ডেটা Firebase-এ স্থায়ীভাবে থাকবে। ✅"
            )
            
            # লগ চ্যানেলে জানানো
            log_to_channel(f"👤 **নতুন ইউজার যুক্ত হয়েছে!**\nনাম: {user.first_name}\nআইডি: `{user.id}`\nইউজারনেম: @{user.username if user.username else 'N/A'}")

    except Exception as e:
        # যদি কোনো এরর হয় তা সরাসরি ইউজারকে দেখানো (ডিবাগিং এর জন্য)
        error_msg = f"❌ **Firebase Error:** `{str(e)}`"
        bot.edit_message_text(chat_id=message.chat.id, message_id=sent_msg.message_id, text=error_msg)
        log_to_channel(f"⚠️ **Runtime Error:**\nUser: {user.first_name}\nError: `{str(e)}`")

@bot.message_handler(commands=['admin'])
def admin_info(message):
    if message.from_user.id == ADMIN_ID:
        try:
            # মোট ইউজারের সংখ্যা বের করা
            users_count = len(list(db.collection('users').list_documents()))
            bot.reply_to(message, f"📊 **বট পরিসংখ্যান:**\n\nমোট ইউজার: `{users_count}`\nসার্ভার: GitHub Actions\nডাটাবেজ: Firestore")
        except:
            bot.reply_to(message, "তথ্য আনতে সমস্যা হচ্ছে।")
    else:
        bot.reply_to(message, "❌ এই কমান্ডটি শুধু এডমিনের জন্য।")

# --- ৪. বট চালানো ---
if __name__ == "__main__":
    print("Bot is running...")
    log_to_channel("✅ **বট সফলভাবে রিস্টার্ট হয়েছে!**\nএখন ১০০% সচল।")
    
    while True:
        try:
            # skip_pending=True দিলে বন্ধ থাকা অবস্থায় আসা মেসেজগুলো ইগনোর করবে
            bot.polling(none_stop=True, interval=0, timeout=40)
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(5)
