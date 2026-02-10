import os
import json
import telebot

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"

# Cargar datos
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            "money": 1000
        }
        save_users()
    return users[user_id]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message,
        "🪙 Gracias por unirse a Lust Tower\n"
        f"aqui tiene algunas monedas de cortesia: ${user['money']}\n\n"
        "Comandos disponibles:\n"
        "/balance – ver saldo\n"
        "/work – trabajar"
    )

@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message, f"💰 Tu saldo actual es: ${user['money']}"
    )

@bot.message_handler(commands=["work"])
def work(message):
    user = get_user(message.from_user.id)
    user["money"] += 20
    save_users()
    bot.reply_to(
        message, "🛠 Trabajaste y ganaste $20"
    )

print("Sistema económico activo y persistente...")
bot.infinity_polling()
