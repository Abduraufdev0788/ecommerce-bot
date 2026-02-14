from telegram import Update
from telegram.ext import ContextTypes
from database import db


async def admin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])

    async with db.pool.acquire() as conn:

        await conn.execute("""
            UPDATE orders
            SET payment_status='paid',
                status='confirmed'
            WHERE id=$1
        """, order_id)

        items = await conn.fetch("""
            SELECT product_id, count
            FROM order_items
            WHERE order_id=$1
        """, order_id)

        for item in items:
            await conn.execute("""
                UPDATE products
                SET quantity = quantity - $1
                WHERE id=$2
            """, item["count"], item["product_id"])

        user = await conn.fetchrow("""
            SELECT u.telegram_id
            FROM users u
            JOIN orders o ON o.user_id = u.id
            WHERE o.id=$1
        """, order_id)

    await query.message.edit_caption("✅ To‘lov tasdiqlandi.")

    await context.bot.send_message(
        chat_id=user["telegram_id"],
        text=f"🎉 Buyurtmangiz tasdiqlandi!\nOrder ID: {order_id}"
    )


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])

    async with db.pool.acquire() as conn:
        await conn.execute("""
            UPDATE orders
            SET payment_status='cancelled',
                status='cancelled'
            WHERE id=$1
        """, order_id)

        user = await conn.fetchrow("""
            SELECT u.telegram_id
            FROM users u
            JOIN orders o ON o.user_id = u.id
            WHERE o.id=$1
        """, order_id)

    await query.message.edit_caption("❌ To‘lov bekor qilindi.")

    await context.bot.send_message(
        chat_id=user["telegram_id"],
        text=f"❌ Buyurtmangiz bekor qilindi.\nOrder ID: {order_id}"
    )
