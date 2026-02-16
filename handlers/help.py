from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_USERNAME


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "📞 Yordam bo‘limi\n\n"
        "🕒 Ish vaqti: 09:00 - 21:00\n"
        "🚚 Yetkazib berish: 1-2 kun\n"
        "💳 To‘lov: Bank karta orqali\n\n"
        f"👤 Admin bilan bog‘lanish: @{ADMIN_USERNAME}"
    )

    await update.message.reply_text(text)
