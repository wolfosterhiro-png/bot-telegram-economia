import os
import json
import telebot
import random
from datetime import datetime, timedelta

# =========================
# CONFIGURACIÓN DEL BOT
# =========================
TOKEN = os.getenv("BOT_TOKEN")  # O tu token directamente como string
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users.json"

# =========================
# BASE DE DATOS DE USUARIOS
# =========================
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
            "money": 0,
            "profesion": None,
            "last_work": None,
            "bono_inicio": False  # indica si ya recibió los $1000 iniciales
        }
        save_users()
    return users[user_id]

# =========================
# DEFINICIÓN DE PROFESIONES
# =========================
PROFESIONES = {
    "medico":      {"salario": 30,  "bono_prob": 0.30, "bono": 70,  "penal_prob":0,  "penal":0,   "bloqueo":0},
    "programador": {"salario": 60,  "bono_prob": 0,    "bono":0,    "penal_prob":0.10,"penal":20,"bloqueo":0},
    "policia":     {"salario": 75,  "bono_prob": 0.20, "bono":100, "penal_prob":0,  "penal":0,   "bloqueo":0},
    "inversionista":{"salario":100, "bono_prob": 0,    "bono":0,   "penal_prob":0.05,"penal":100,"bloqueo":0},
    "mecanico":    {"salario": 50,  "bono_prob":0,     "bono":0,   "penal_prob":0,  "penal":0,   "bloqueo":0},
    "chofer":      {"salario": 50,  "bono_prob":0,     "bono":0,   "penal_prob":0,  "penal":0,   "bloqueo":0},
    "artista":     {"salario": 30,  "bono_prob":0.20,  "bono":100,"penal_prob":0,  "penal":0,   "bloqueo":0},
    "streamer":    {"salario": 30,  "bono_prob":0.15,  "bono":70, "penal_prob":0,  "penal":0,   "bloqueo":0},
    "ts":          {"salario": 0,   "bono_prob":0,     "bono":0,   "penal_prob":0,  "penal":0,   "bloqueo":0},  # gana solo si otro usuario lo paga
    "mercenario":  {"salario":100,  "bono_prob":0,     "bono":0,   "penal_prob":0.50,"penal":0,"bloqueo":7},
    "mafioso":     {"salario":20,   "bono_prob":0.50,  "bono":200,"penal_prob":0,  "penal":0,   "bloqueo":0},
}

# =========================
# COMANDOS DE PROFESIÓN
# =========================
@bot.message_handler(commands=["profesion"])
def elegir_profesion(message):
    user = get_user(message.from_user.id)
    partes = message.text.split()

    if len(partes) < 2:
        bot.reply_to(message, "❗ Para elegir tu profesión, usa: /profesion <nombre>\nEjemplo: /profesion medico")
        return

    profesion = partes[1].lower()

    if profesion not in PROFESIONES:
        bot.reply_to(message, "❌ Profesión inválida. Revisa la lista de profesiones disponibles.")
        return

    # Si ya tiene profesión y cambia, no reinicia el dinero ni el bono inicial
    if user["profesion"] is None:
        if not user["bono_inicio"]:
            user["money"] += 1000
            user["bono_inicio"] = True
            bot.reply_to(message, f"✅ Profesión registrada como {profesion.capitalize()}. 🎁 Has recibido $1000 de cortesía por unirte!")
        else:
            bot.reply_to(message, f"✅ Profesión registrada como {profesion.capitalize()}.")
    else:
        bot.reply_to(message, f"⚠️ Has cambiado tu profesión a {profesion.capitalize()}. Tu dinero actual se mantiene.")

    user["profesion"] = profesion
    save_users()

@bot.message_handler(commands=["resetprof"])
def reset_profesion(message):
    user = get_user(message.from_user.id)
    if user["profesion"] is None:
        bot.reply_to(message, "❌ No tienes ninguna profesión asignada.")
        return
    user["profesion"] = None
    save_users()
    bot.reply_to(message, "✅ Profesión eliminada. Ahora puedes elegir otra con /profesion <nombre>.")

# =========================
# COMANDO /START
# =========================
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)
    texto = (
        f"👋 Bienvenido a Lust Tower, {message.from_user.first_name}!\n"
        "Aquí manejamos nuestra propia economía. Por favor llena la siguiente ficha para recibir tus $1000 de cortesía al elegir tu profesión.\n\n"
        "『INFORMACIÓN DEL CLIENTE』\n"
        "【NOMBRE】\n"
        "【EDAD】\n"
        "【SEXO】\n"
        "【TRABAJO】\n\n"
        "(IMPORTANTE: Elige una profesión usando /profesion <nombre>, la elección es permanente)\n\n"
        "Profesiones disponibles:\n"
        "Medico, Programador, Policia, Inversionista, Mecanico, Chofer, Artista, Streamer, TS, Mercenario, Mafioso\n\n"
        "【ALTURA】\n"
        "【ORIENTACIÓN】\n"
        "【GUSTOS】\n"
        "【DISGUSTOS】\n"
        "【HISTORIA DE VIDA】\n"
        "【APARIENCIA】\n"
        "(Adjuntar foto opcional)"
    )
    bot.reply_to(message, texto)

# =========================
# COMANDO /WORK
# =========================
@bot.message_handler(commands=["work"])
def work(message):
    user = get_user(message.from_user.id)
    if user["profesion"] is None:
        bot.reply_to(message, "❌ Debes elegir una profesión primero con /profesion <nombre>")
        return

    now = datetime.now()
    if user["last_work"]:
        last = datetime.fromisoformat(user["last_work"])
        if now - last < timedelta(hours=24):
            remaining = timedelta(hours=24) - (now - last)
            bot.reply_to(message, f"⏳ Ya trabajaste hoy. Puedes volver a trabajar en {remaining}")
            return

    prof = PROFESIONES[user["profesion"]]
    dinero_ganado = prof["salario"]

    # Verificar bono
    if prof["bono_prob"] > 0 and random.random() < prof["bono_prob"]:
        dinero_ganado += prof["bono"]
        bono_msg = f"🎉 ¡Bono recibido! +${prof['bono']}"
    else:
        bono_msg = ""

    # Verificar penalización
    if prof["penal_prob"] > 0 and random.random() < prof["penal_prob"]:
        dinero_ganado -= prof["penal"]
        penal_msg = f"⚠️ Penalización: -${prof['penal']}"
    else:
        penal_msg = ""

    user["money"] += dinero_ganado
    user["last_work"] = now.isoformat()
    save_users()

    bot.reply_to(message, f"💼 Trabajaste como {user['profesion'].capitalize()} y ganaste ${dinero_ganado}\n{bono_msg} {penal_msg}")

# =========================
# COMANDO /BALANCE
# =========================
@bot.message_handler(commands=["balance"])
def balance(message):
    user = get_user(message.from_user.id)
    bot.reply_to(message, f"💰 Tu saldo actual es: ${user['money']}")

# =========================
# COMANDO /PAY
# =========================
@bot.message_handler(commands=["pay"])
def pay(message):
    user = get_user(message.from_user.id)
    partes = message.text.split()
    if len(partes) < 3:
        bot.reply_to(message, "❗ Uso correcto: /pay @usuario <monto>")
        return
    try:
        monto = int(partes[2])
    except:
        bot.reply_to(message, "❌ Monto inválido.")
        return
    if user["money"] < monto:
        bot.reply_to(message, "❌ No tienes suficiente dinero.")
        return
    # Obtener id del usuario mencionado
    if not message.entities or message.entities[1].type != "mention":
        bot.reply_to(message, "❌ Debes mencionar a un usuario válido.")
        return
    username = partes[1].replace("@","")
    # Buscamos el id en users
    target_id = None
    for uid, u in users.items():
        if "username" in u and u["username"] == username:
            target_id = uid
            break
    if target_id is None:
        bot.reply_to(message, "❌ Usuario no encontrado.")
        return
    user["money"] -= monto
    users[target_id]["money"] += monto
    save_users()
    bot.reply_to(message, f"✅ Transferencia exitosa: ${monto} a @{username}")

# =========================
# COMANDO /REGLAS
# =========================
@bot.message_handler(commands=["reglas"])
def reglas(message):
    texto = (
        "📜 Bienvenido a The Lust Tower!\n\n"
        "Para una buena convivencia, por favor lee y respeta las reglas:\n\n"
        "[TEMAS]\nEl grupo está dividido por temas. Respeta cada uno.\n\n"
        "[EDAD]\nSolo para mayores de 18 años. Menores serán expulsados inmediatamente.\n\n"
        "[SPAM]\nSolo se permite spam en su tema correspondiente y con permiso de un administrador.\n"
        "Links no autorizados serán eliminados y su remitente podrá ser baneado.\n\n"
        "[FICHAS y PROFESIONES]\nNecesitas ficha y profesión para rolear. Sin ellas recibirás un strike y deberás registrarte en 7 días.\n\n"
        "[GALERÍA y SALA DE VIDEO]\nContenido adulto permitido, pero PROHIBIDO: pornografía infantil, zoofilia, gore, fetiches extremos, nudes de personas no verificadas, lolicon/shotacon.\n\n"
        "[ACOSO]\nNo se tolera. Acoso en privado o grupo será motivo de expulsión.\n\n"
        "[DATOS PERSONALES]\nRespeta la privacidad: no compartas datos propios o de otros.\n\n"
        "[ROL]\nMantén inmersión usando canales correctos. Usa Offrol si hablas fuera de rol.\n\n"
        "[ROL y REALIDAD]\nNo confundas el rol con la vida real.\n\n"
        "[REPORTES]\nQuejas o reportes a administradores o canal de Reportes."
    )
    bot.reply_to(message, texto)

# =========================
# COMANDO /GUIA
# =========================
@bot.message_handler(commands=["guia"])
def guia(message):
    texto = (
        "📖 **Guía de uso del Bot Lust Tower**\n\n"
        "/start - Te da la bienvenida y una ficha para llenar si eres nuevo.\n"
        "/profesion <nombre> - Te permite elegir una profesión (obligatoria, elección permanente).\n"
        "/resetprof - Quitar tu profesión y elegir otra.\n"
        "/work - Trabajar y ganar dinero (solo 1 vez cada 24 horas).\n"
        "/pay @usuario <monto> - Transferir dinero a otro usuario.\n"
        "/balance - Consultar saldo actual.\n"
        "/reglas - Mostrar las reglas del grupo.\n"
        "/guia - Mostrar esta guía de comandos.\n\n"
        "💡 Recomendaciones:\n"
        "1. Primero usa /start para registrarte y recibir tu ficha.\n"
        "2. Luego selecciona tu profesión con /profesion <nombre>.\n"
        "3. Después podrás usar /work para ganar dinero y /pay para transferirlo."

        "recuerda usar los comandos en sus respectivos temas"

        "/start y /Profesion en la recepcion"
        "/Work y /pay en el banco"        
    )
    bot.reply_to(message, texto)

# =========================
# INICIAR BOT
# =========================
print("🤖 Sistema económico activo y persistente...")
bot.infinity_polling()

