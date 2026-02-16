from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from config import ADMIN_ID
from handlers.admin_panel import admin_panel
from database import db


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    telegram_id = update.effective_user.id

    # 🔥 USERNI DB GA SAQLAYMIZ
    async with db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id)
            VALUES ($1)
            ON CONFLICT (telegram_id) DO NOTHING
        """, telegram_id)

    # 🧑‍💼 ADMIN
    if telegram_id == ADMIN_ID:

        await update.message.reply_text(
            "🧑‍💼 Admin panelga xush kelibsiz",
            reply_markup=ReplyKeyboardRemove()
        )

        await admin_panel(update, context)
        return

    # 👤 USER MENU
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
