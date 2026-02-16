from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from config import ADMIN_ID
from handlers.admin_panel import admin_panel


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # 🧑‍💼 ADMIN
    if update.effective_user.id == ADMIN_ID:

        # Agar oldin reply keyboard bo‘lgan bo‘lsa o‘chirib tashlaymiz
        await update.message.reply_text(
            "🧑‍💼 Admin panelga xush kelibsiz",
            reply_markup=ReplyKeyboardRemove()
        )

        # Inline dashboard ochamiz
        await admin_panel(update, context)
        return

    # 👤 USER
    keyboard = [
        ["📦 Mahsulotlar", "🛒 Savatcham"],
        ["📦 Buyurtmalarim", "ℹ️ Yordam"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Xush kelibsiz!",
        reply_markup=reply_markup
    )
