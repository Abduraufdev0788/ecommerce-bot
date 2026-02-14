from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    async with db.pool.acquire() as conn:

        user = await conn.fetchrow(
            "SELECT id FROM users WHERE telegram_id=$1",
            telegram_id
        )

        if not user:
            await update.message.reply_text("Buyurtmalar topilmadi.")
            return

        user_id = user["id"]

        orders = await conn.fetch("""
            SELECT id, total_price, status, payment_status, created_at
            FROM orders
            WHERE user_id=$1
            ORDER BY id DESC
        """, user_id)

    if not orders:
        await update.message.reply_text("📦 Sizda hali buyurtma yo‘q.")
        return

    for order in orders:

        text = (
            f"🆔 Order ID: {order['id']}\n"
            f"💰 Summa: {order['total_price']}\n"
            f"📌 Status: {order['status']}\n"
            f"💳 To‘lov: {order['payment_status']}\n"
            f"🕒 Sana: {order['created_at']}\n"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📦 Batafsil",
                    callback_data=f"order_detail:{order['id']}"
                )
            ]
        ])

        await update.message.reply_text(text, reply_markup=keyboard)


async def order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])

    async with db.pool.acquire() as conn:

        items = await conn.fetch("""
            SELECT p.name, p.price, oi.count
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id=$1
        """, order_id)

    text = f"📦 Order ID: {order_id}\n\n"

    total = 0

    for item in items:
        subtotal = item["price"] * item["count"]
        total += subtotal
        text += f"{item['name']} x {item['count']} = {subtotal}\n"

    text += f"\n💰 Umumiy: {total}"

    await query.message.reply_text(text)
