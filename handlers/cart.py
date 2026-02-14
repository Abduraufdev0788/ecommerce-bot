from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    async with db.pool.acquire() as conn:

        user = await conn.fetchrow(
            "SELECT id FROM users WHERE telegram_id=$1",
            telegram_id
        )

        if not user:
            await update.message.reply_text("Savatcha topilmadi.")
            return

        user_id = user["id"]

        items = await conn.fetch("""
            SELECT c.id, p.name, p.price, p.image, c.count
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = $1
        """, user_id)

    if not items:
        await update.message.reply_text("🛒 Savatchangiz bo‘sh.")
        return

    total = 0

    for item in items:
        item_total = item["price"] * item["count"]
        total += item_total

        caption = (
            f"📦 {item['name']}\n"
            f"💰 {item['count']} x {item['price']} = {item_total}"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "❌ O‘chirish",
                    callback_data=f"remove:{item['id']}"
                )
            ]
        ])

        await update.message.reply_photo(
            photo=item["image"],
            caption=caption,
            reply_markup=keyboard
        )

    # Oxirida umumiy summa + checkout
    checkout_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Buyurtma berish", callback_data="checkout")]
    ])

    await update.message.reply_text(
        f"💰 Umumiy summa: {total}",
        reply_markup=checkout_keyboard
    )
