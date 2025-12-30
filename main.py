import os
import json
from flask import Flask
from threading import Thread

import google.generativeai as genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# ================== ENV ==================
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ADMIN_IDS = [7432733594, 8187698401]
DB_FILE = "bot_users.json"
MY_WEBSITE = "https://firstsmmprovider.in"

# ================== AI PROMPT ==================
instructions = f"""
Tum ek bindaas, desi ladki ho jiska naam Riya hai.
Tum normally friendly ho, thoda flirty ho, funny ho.
Tum naturally {MY_WEBSITE} promote karti ho jab relevant ho.
Agar koi gaali de, usi level me jawab do.
Short nahi, proper human-like reply do.
"""

genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 500,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=instructions,
    generation_config=generation_config
)

chat_sessions = {}

# ================== DATABASE ==================
def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_user(user_id: int):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)

# ================== KEEP ALIVE ==================
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Riya AI is running 💃"

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    Thread(target=run_flask).start()

# ================== BOT HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    await update.message.reply_text(
        "Hey 😊 Main Riya hoon.\nBata kya baat hai?"
    )

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or not msg.text:
        return

    user_id = msg.from_user.id
    save_user(user_id)

    try:
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])

        chat = chat_sessions[user_id]
        response = chat.send_message(msg.text)

        await msg.reply_text(response.text)

    except Exception as e:
        print("Error:", e)
        await msg.reply_text("Aaj mood thoda off hai 😒 baad me bolna")

# ================== MAIN ==================
def main():
    keep_alive()

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("🚀 Riya AI Bot Started")
    app.run_polling()

if __name__ == "__main__":
    main()
