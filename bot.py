from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import sqlite3
import random
import re

# =========================
# CONFIGURATION
# =========================

TOKEN = "8438365476:AAEv0q8nqIq-vZIBwfYo4LEaxTtQLa25GoE"

# ONLY volunteers (admins) can redeem
ADMIN_IDS = [6797155121]

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect("food.db", check_same_thread=False)
c = conn.cursor()

# =========================
# HELPER: 4-DIGIT OTP
# =========================

def generate_otp():
    return f"{random.randint(0, 9999):04d}"

# =========================
# COMMAND: /register
# =========================

def register(update, context):
    if len(context.args) != 1:
        update.message.reply_text("❗ Use: /register PHONE_NUMBER")
        return

    phone = context.args[0].strip()

    # Validate phone number (10 digits)
    if not phone.isdigit() or len(phone) != 10:
        update.message.reply_text("❗ Enter a valid 10-digit phone number")
        return

    tg_id = update.effective_user.id

    otp_day1 = generate_otp()
    otp_day2 = generate_otp()

    try:
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, 0, 0)",
            (phone, tg_id, otp_day1, otp_day2)
        )
        conn.commit()

        update.message.reply_text(
            "✅ Registration successful!\n\n"
            f"🍽 Day 1 Food OTP: {otp_day1}\n"
            f"🍽 Day 2 Food OTP: {otp_day2}\n\n"
            "📌 Show the OTP at the food counter."
        )

    except:
        update.message.reply_text("❌ This phone number is already registered.")
# =========================
# CORE REDEEM LOGIC
# =========================

def redeem_otp(update, otp):
    user_id = update.effective_user.id

    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 UNAUTHORIZED")
        return

    # Day 1 check
    c.execute(
        "SELECT reg_id, day1 FROM users WHERE code_day1=?",
        (otp,)
    )
    row = c.fetchone()

    if row:
        reg_id, used = row
        if used == 0:
            c.execute(
                "UPDATE users SET day1=1 WHERE code_day1=?",
                (otp,)
            )
            conn.commit()
            update.message.reply_text(
                f"🟢 VALID – SERVE FOOD\nReg ID: {reg_id}"
            )
        else:
            update.message.reply_text("🔴 USED – DO NOT SERVE")
        return

    # Day 2 check
    c.execute(
        "SELECT reg_id, day2 FROM users WHERE code_day2=?",
        (otp,)
    )
    row = c.fetchone()

    if row:
        reg_id, used = row
        if used == 0:
            c.execute(
                "UPDATE users SET day2=1 WHERE code_day2=?",
                (otp,)
            )
            conn.commit()
            update.message.reply_text(
                f"🟢 VALID – SERVE FOOD\nReg ID: {reg_id}"
            )
        else:
            update.message.reply_text("🔴 USED – DO NOT SERVE")
        return

    update.message.reply_text("❌ INVALID OTP")

# =========================
# COMMAND: /redeem (OPTIONAL)
# =========================

def redeem_command(update, context):
    if len(context.args) != 1:
        update.message.reply_text("❗ Use: /redeem OTP")
        return

    redeem_otp(update, context.args[0])

# =========================
# MESSAGE HANDLER: PLAIN OTP
# =========================

def otp_message_handler(update, context):
    text = update.message.text.strip()

    # Accept ONLY exactly 4 digits
    if re.fullmatch(r"\d{4}", text):
        redeem_otp(update, text)

# =========================
# BOT STARTUP
# =========================

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("register", register))
dp.add_handler(CommandHandler("redeem", redeem_command))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, otp_message_handler))

updater.start_polling()
print("🤖 Bot is running (FAST MODE)...")
updater.idle()
