from telegram import Update
from telegram.ext import ContextTypes
from database import db
from keyboards.main_menu import main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    async with db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (telegram_id, full_name)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO NOTHING
        """, user.id, user.full_name)

    await update.message.reply_text(
        f"Salom {user.full_name} 👋\n\nDo‘konimizga xush kelibsiz 🛒",
        reply_markup=main_menu()
    )
