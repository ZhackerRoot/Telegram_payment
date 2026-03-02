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

DOWNLOAD_LINK = "https://yourdomain.com/download/skynet"

PLAN, PAYMENT, UID, EMAIL = range(4)

# ================= PAYMENT DATA =================

PAYMENTS = {
    "Visa / Mastercard": "💳 Card Payment\nContact admin",
    "Payme / Click": "🇺🇿 Payme / Click\n+998XXXXXXXX",
    "Crypto BTC": "BTC Wallet:\n1ABCXXXX",
    "Crypto USDT": "USDT TRC20:\nTXXXX",
    "Crypto Ethereum": "ETH Wallet:\n0xXXXX",
}

# ================= VALIDATORS =================

def valid_uid(uid):
    return uid.isdigit() and len(uid) >= 5


def valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Welcome to *SkyNet Premium*\n\nChoose your plan:",
        parse_mode="Markdown"
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

    keyboard = list(PAYMENTS.keys())

    await update.message.reply_text(
        "💳 Choose payment method:",
        reply_markup=ReplyKeyboardMarkup(
            [[k] for k in keyboard], resize_keyboard=True
        ),
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

🆔 Send your PocketOption UID:
""",
        reply_markup=ReplyKeyboardRemove(),
    )

    return UID


# ================= UID =================

async def save_uid(update: Update, context):

    uid = update.message.text.strip()

    if not valid_uid(uid):
        await update.message.reply_text("❌ Invalid UID.")
        return UID

    context.user_data["uid"] = uid

    await update.message.reply_text(
        "📧 Now send your Email (for activation notification):"
    )

    return EMAIL


# ================= EMAIL =================

async def save_email(update: Update, context):

    email = update.message.text.strip()

    if not valid_email(email):
        await update.message.reply_text("❌ Invalid email.")
        return EMAIL

    plan = context.user_data["plan"]
    payment = context.user_data["payment"]
    uid = context.user_data["uid"]

    try:
        requests.post(
            SERVER_URL,
            headers={"x-bot-key": BOT_KEY},
            json={
                "uid": uid,
                "email": email,
                "plan": plan,
                "payment_method": payment,
            },
            timeout=10,
        )
    except Exception as e:
        print(e)
        await update.message.reply_text("⚠ Server error.")
        return ConversationHandler.END

    await update.message.reply_text(
        f"""
✅ Request submitted!

⏳ Admin will review payment within 24 hours.

📥 Download robot:
{DOWNLOAD_LINK}

After approval robot unlocks automatically.
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
            UID: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_uid)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("🚀 SkyNet Bot Running")
    app.run_polling()


if __name__ == "__main__":
    main()
