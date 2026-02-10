import os
import json
import telebot
import random
import time

# =========================
# CONFIGURACIÓN BOT
# =========================
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"
COOLDOWN_WORK = 86400  # 24 horas

# =========================
# BASE DE DATOS
# =========================
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            "money": 1000,
            "profesion": None,
            "ultimo_work": 0
        }
        save_users()
    return users[user_id]

# =========================
# PROFESIONES
# =========================
PROFESIONES = {
    "medico": {"salario": 30, "bonus_chance": 0.30, "bonus": 70},
    "programador": {"salario": 60, "bonus_chance": 0.10, "bonus": -20},
    "policia": {"salario": 75, "bonus_chance": 0.20, "bonus": 100},
    "inversionista": {"salario": 100, "bonus_chance": 0.05, "bonus": -100},
    "mecanico": {"salario": 50, "bonus_chance": 0, "bonus": 0},
    "chofer": {"salario": 50, "bonus_chance": 0, "bonus": 0},
    "artista": {"salario": 30, "bonus_chance": 0.20, "bonus": 100},
    "streamer": {"salario": 30, "bonus_chance": 0.15, "bonus": 70},
    "mercenario": {"salario": 100, "bonus_chance": 0.50, "bonus": -100},
    "mafioso": {"salario": 20, "bonus_chance": 0.50, "bonus": 200}
}

# =========================
# COMANDOS
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    bot.reply_to(
        message,
        "🪙 Bienvenido al sistema económico de rol\n\n"
        f"💰 Dinero inicial: ${user['money']}\n\n"
        "Comandos:\n"
        "/profesion nombre\n"
        "/work\n"
        "/balance\n"
        "/pay @usuario monto"
    )

@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user.id)
    bot.reply_to(message, f"💰 Tu saldo actual: ${user['money']}")

# =========================
# PROFESIÓN
# =========================
@bot.message_handler(commands=["profesion"])
def profesion(message):
    user = get_user(message.from_user.id)
    args = message.text.split()

    if user["profesion"]:
        bot.reply_to(message, f"❌ Ya tienes profesión: {user['profesion'].capitalize()}")
        return

    if len(args) < 2:
        bot.reply_to(message, "Uso correcto:\n/profesion medico")
        return

    nombre = args[1].lower()

    if nombre not in PROFESIONES:
        bot.reply_to(message, "❌ Profesión inválida")
        return

    user["profesion"] = nombre
    save_users()

    bot.reply_to(
        message,
        f"✅ Profesión asignada: {nombre.capitalize()}\n"
        "⚠️ Esta elección es permanente"
    )

# =========================
# WORK (24H)
# =========================
@bot.message_handler(commands=["work"])
def work(message):
    user = get_user(message.from_user.id)

    if not user["profesion"]:
        bot.reply_to(message, "❌ Debes elegir una profesión primero")
        return

    ahora = time.time()
    restante = COOLDOWN_WORK - (ahora - user["ultimo_work"])

    if restante > 0:
        horas = int(restante // 3600)
        bot.reply_to(message, f"⏳ Debes esperar {horas} horas para trabajar otra vez")
        return

    datos = PROFESIONES[user["profesion"]]
    ganancia = datos["salario"]
    texto = f"💼 Profesión: {user['profesion'].capitalize()}\n💵 Base: ${ganancia}\n"

    if random.random() < datos["bonus_chance"]:
        ganancia += datos["bonus"]
        if datos["bonus"] > 0:
            texto += f"🎉 Evento especial: +${datos['bonus']}\n"
        else:
            texto += f"💥 Mal día: ${datos['bonus']}\n"

    user["money"] += ganancia
    user["ultimo_work"] = ahora
    save_users()

    texto += f"💰 Ganancia total: ${ganancia}"
    bot.reply_to(message, texto)

# =========================
# PAY
# =========================
@bot.message_handler(commands=["pay"])
def pay(message):
    args = message.text.split()

    if len(args) < 3 or not message.entities:
        bot.reply_to(message, "Uso:\n/pay @usuario monto")
        return

    try:
        monto = int(args[2])
    except:
        bot.reply_to(message, "❌ Monto inválido")
        return

    if monto <= 0:
        bot.reply_to(message, "❌ El monto debe ser positivo")
        return

    sender = get_user(message.from_user.id)

    if sender["money"] < monto:
        bot.reply_to(message, "❌ No tienes suficiente dinero")
        return

    for ent in message.entities:
        if ent.type == "mention":
            username = message.text[ent.offset:ent.offset + ent.length].replace("@", "")
            break
    else:
        bot.reply_to(message, "❌ Debes mencionar a un usuario")
        return

    recipient_id = None
    for uid, data in users.items():
        if data.get("username") == username:
            recipient_id = uid
            break

    if recipient_id is None:
        bot.reply_to(message, "❌ Usuario no encontrado en el sistema")
        return

    sender["money"] -= monto
    users[recipient_id]["money"] += monto
    save_users()

    bot.reply_to(
        message,
        f"💸 Transferencia exitosa\n"
        f"Enviado: ${monto}"
    )

# =========================
print("Sistema económico activo y completo...")
bot.infinity_polling()
