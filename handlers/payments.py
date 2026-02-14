from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from config import ADMIN_ID


async def receive_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Admin yuborsa ignore
    if update.effective_user.id == ADMIN_ID:
        return

    if not update.message.photo:
        return

    photo_id = update.message.photo[-1].file_id
    telegram_id = update.effective_user.id

    async with db.pool.acquire() as conn:

        # Eng oxirgi pending orderni topamiz
        order = await conn.fetchrow("""
            SELECT o.id
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE u.telegram_id=$1
            AND o.payment_status='pending'
            ORDER BY o.id DESC
            LIMIT 1
        """, telegram_id)

        if not order:
            await update.message.reply_text("❗ Pending buyurtma topilmadi.")
            return

        order_id = order["id"]

        await conn.execute("""
            UPDATE orders
            SET payment_screenshot=$1
            WHERE id=$2
        """, photo_id, order_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_confirm:{order_id}"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"admin_cancel:{order_id}")
        ]
    ])

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=f"💰 Yangi to‘lov!\n\nOrder ID: {order_id}",
        reply_markup=keyboard
    )

    await update.message.reply_text("📤 Screenshot yuborildi. Admin tasdiqlashini kuting.")
