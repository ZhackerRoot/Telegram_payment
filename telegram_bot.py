from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import requests
import re


# ================= CONFIG =================

BOT_TOKEN = "8601257275:AAEBS7NISCf9MggiBcxTeMWFwR-P2Y8Nqeg"

SERVER_URL = "https://skynet-skynet.up.railway.app/create_user_request"

BOT_KEY = "skynet_super_secret_777"


PLAN, PAYMENT, EMAIL = range(3)


# ================= PAYMENT DATA =================

PAYMENTS = {
    "Visa / Mastercard": "💳 Card Payment\nContact admin",
    "Payme / Click": "🇺🇿 Payme / Click\n+998 XX XXX XX XX",
    "Crypto BTC": "BTC Wallet:\n1ABCXXXXXXX",
    "Crypto USDT": "USDT TRC20:\nTXXXXXXX",
    "Crypto Ethereum": "ETH Wallet:\n0xXXXXXXX",
}


# ================= EMAIL CHECK =================

def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Welcome to Skynet Premium version!\n\nChoose your plan:"
    )

    keyboard = [["STANDARD $249"], ["VIP $899"]]

    await update.message.reply_text(
        "Select plan:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return PLAN


# ================= PLAN =================

async def choose_plan(update: Update, context):

    text = update.message.text.lower()

    if "standard" in text:
        context.user_data["plan"] = "standard"

    elif "vip" in text:
        context.user_data["plan"] = "vip"

    else:
        return PLAN

    keyboard = [
        ["Visa / Mastercard"],
        ["Payme / Click"],
        ["Crypto BTC"],
        ["Crypto USDT"],
        ["Crypto Ethereum"],
    ]

    await update.message.reply_text(
        "💳 Choose payment method:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

    return PAYMENT


# ================= PAYMENT =================

async def choose_payment(update: Update, context):

    method = update.message.text

    if method not in PAYMENTS:
        return PAYMENT

    context.user_data["payment"] = method

    await update.message.reply_text(
        f"""
✅ Payment method selected:

{method}

{PAYMENTS[method]}

📧 Now send your PocketOption EMAIL:
""",
        reply_markup=ReplyKeyboardRemove(),
    )

    return EMAIL


# ================= EMAIL =================

async def save_email(update: Update, context):

    email = update.message.text.strip()

    if not valid_email(email):
        await update.message.reply_text("❌ Invalid email. Try again.")
        return EMAIL

    plan = context.user_data["plan"]
    payment = context.user_data["payment"]

    try:
        requests.post(
            SERVER_URL,
            headers={"x-bot-key": BOT_KEY},
            json={
                "username": email,
                "plan": plan,
                "payment_method": payment,
            },
            timeout=10,
        )
    except:
        await update.message.reply_text("⚠ Server error. Try later.")
        return ConversationHandler.END

    await update.message.reply_text(
        """
✅ To‘lov arizasi yuborildi.

⏳ Ariza 24 soat ichida ko‘rib chiqiladi.

To‘lov tasdiqlangandan so‘ng robot avtomatik unlock qilinadi.

Rahmat!
"""
    )

    return ConversationHandler.END


# ================= CANCEL =================

async def cancel(update: Update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


# ================= RUN =================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PLAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_plan)],
            PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_payment)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("SkyNet Telegram Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()