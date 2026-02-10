import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# Base de datos temporal
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = {
            "money": 100
        }
    return users[user_id]

@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message,
        "🪙 Bienvenido al sistema económico de rol\n"
        f"Dinero inicial: ${user['money']}\n\n"
        "Comandos disponibles:\n"
        "/balance – ver saldo\n"
        "/work – trabajar"
    )

@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message,
        f"💰 Tu saldo actual es: ${user['money']}"
    )

@bot.message_handler(commands=["work"])
def work(message):
    user = get_user(message.from_user.id)
    user["money"] += 20
    bot.reply_to(
        message,
        "🛠 Trabajaste y ganaste $20"
    )

print("Sistema económico activo y escuchando...")

bot.infinity_polling()
