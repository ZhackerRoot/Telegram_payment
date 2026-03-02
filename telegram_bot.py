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


# ================= CONFIG =================

BOT_TOKEN = "8601257275:AAEBS7NISCf9MggiBcxTeMWFwR-P2Y8Nqeg"

SERVER_URL = "https://skynet-skynet.up.railway.app/create_user_request"

BOT_KEY = "skynet_super_secret_777"


# ================= STATES =================

PLAN, PAYMENT, UID = range(3)


# ================= PAYMENT DATA =================

PAYMENTS = {
    "Visa / Mastercard": "💳 Card Payment\n4231 2000 0247 1018",
    "Payme / Click": "🇺🇿 Payme / Click\n9860 1666 0357 4780",
    "Crypto BTC": "BTC Wallet:\nbc1qhxf7gq9cgk5k5ejuysna4zr4vge24ql3n2xypn",
    "Crypto USDT": "USDT TRC20:\nTQbARHTRWmeA42tAbJxNVPsAKCTVBhio57",
    "Crypto Ethereum": "ETH Wallet:\n0xCa85fdd381705CaC40301bC462FD59889e3d3672",
}


# ================= UID VALIDATOR =================

def valid_uid(uid: str):
    return uid.isdigit() and len(uid) >= 5


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

🆔 Now send your PocketOption UID:
""",
        reply_markup=ReplyKeyboardRemove(),
    )

    return UID


# ================= UID =================

async def save_uid(update: Update, context):

    uid = update.message.text.strip()

    if not valid_uid(uid):
        await update.message.reply_text("❌ Invalid UID. Send numbers only.")
        return UID

    plan = context.user_data["plan"]
    payment = context.user_data["payment"]

    try:
        requests.post(
            SERVER_URL,
            headers={"x-bot-key": BOT_KEY},
            json={
                "uid": uid,
                "plan": plan,
                "payment_method": payment,
            },
            timeout=10,
        )

    except Exception as e:
        print(e)
        await update.message.reply_text("⚠ Server error. Try later.")
        return ConversationHandler.END

    await update.message.reply_text(
        """
✅ Request submitted successfully!

⏳ Your payment request will be reviewed within 24 hours.

After approval, your robot will unlock automatically.

Thank you!
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
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("🚀 SkyNet Telegram Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
