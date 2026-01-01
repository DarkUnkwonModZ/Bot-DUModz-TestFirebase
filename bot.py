import telebot
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

# GitHub Secrets থেকে ডেটা নেওয়া
BOT_TOKEN = "8202203049:AAFoR-vtoNYZ2efSJBFb_Wb2VukWCXdRciA"
FIREBASE_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT") # গিটহাব সিক্রেট থেকে আসবে

# Firebase ইনিশিয়ালাইজেশন
if FIREBASE_JSON:
    cred_dict = json.loads(FIREBASE_JSON)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Error: Firebase JSON not found in Secrets!")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)
ADMIN_ID = 8504263842

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    user_id = str(user.id)
    
    user_ref = db.collection('users').document(user_id)
    doc = user_ref.get()

    if doc.exists:
        data = doc.to_dict()
        bot.reply_to(message, f"স্বাগতম বন্ধু {user.first_name}! তোমার তথ্য আগে থেকেই সেভ আছে।")
    else:
        user_data = {
            'id': user.id,
            'name': user.first_name,
            'username': user.username,
            'joined_at': datetime.now()
        }
        user_ref.set(user_data)
        bot.reply_to(message, "তুমি আমাদের বটে নতুন! তোমার তথ্য Firebase-এ স্থায়ীভাবে সেভ করা হলো।")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "হ্যালো এডমিন Dark Unknown! বট সচল আছে।")
    else:
        bot.reply_to(message, "দুঃখিত, এটি শুধুমাত্র এডমিনের জন্য।")

print("বট চলছে...")
bot.infinity_polling()
