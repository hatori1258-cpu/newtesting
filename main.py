import os
import json
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================== ENV ==================
TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_FILE = "bot_users.json"
MY_WEBSITE = "https://firstsmmprovider.in"

# ================== AI PROMPT ==================
instructions = f"""
Tum ek bindaas desi ladki ho jiska naam Riya hai.
Tum friendly, funny aur thodi flirty ho.
Tum naturally {MY_WEBSITE} promote karti ho.
Agar koi gaali de, usi tone me jawab do.
Hamesha detailed human-like reply do.
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

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(DB_FILE, "w") as f:
            json.dump(users, f)

# ================== HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text("Hey 😊 Main Riya hoon. Bata kya scene hai?")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    save_user(user_id)

    try:
        if user_id not in chat_sessions:
            chat_sessions[user_id] = model.start_chat(history=[])

        chat = chat_sessions[user_id]
        response = chat.send_message(update.message.text)

        await update.message.reply_text(response.text)

    except Exception as e:
        print("ERROR:", e)
        await update.message.reply_text("Aaj mood off hai 😒 thoda baad bolna")

# ================== MAIN ==================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("🤖 Riya AI Bot Running")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
