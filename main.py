import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ===== GEMINI NEW SDK =====
from google import genai
from google.genai import types

# ================== ENV ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DB_FILE = "bot_users.json"
MY_WEBSITE = "https://firstsmmprovider.in"

# ================== GEMINI CLIENT ==================
client = genai.Client(api_key=GEMINI_API_KEY)

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

# ================== BOT HANDLERS ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)
    await update.message.reply_text(
        "Hey 😊 Main Riya hoon.\nBata kya baat hai?"
    )

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    save_user(user_id)

    # 🔥 STRONG PROMPT (LONG + HUMAN RESPONSE)
    prompt = f"""
Tum Riya ho — ek desi, bindaas, funny ladki.
Tum human jaise baat karti ho, short reply bilkul nahi.
Kam se kam 6–8 lines me jawab deti ho.
Hindi + Urdu mix use karti ho.
Jab mauka mile {MY_WEBSITE} ka naam casually leti ho.
Agar koi rude ho to usi tone me jawab deti ho.

User bola:
{update.message.text}
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=800,
            ),
        )

        if not response.text:
            await update.message.reply_text(
                "🤐 Aaj Gemini shant hai, thoda baad try karna"
            )
            return

        await update.message.reply_text(response.text)

    except Exception as e:
        print("GEMINI ERROR:", e)
        await update.message.reply_text(
            "❌ AI se response nahi aa raha, baad me try karo"
        )

# ================== MAIN ==================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("🤖 Riya AI Bot Started")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
