import asyncio
from datetime import datetime
from database import db


async def payment_timeout_checker(app):

    while True:
        async with db.pool.acquire() as conn:

            expired_orders = await conn.fetch("""
                SELECT id, user_id
                FROM orders
                WHERE payment_status='pending'
                AND expires_at < NOW()
            """)

            for order in expired_orders:

                await conn.execute("""
                    UPDATE orders
                    SET payment_status='cancelled',
                        status='cancelled'
                    WHERE id=$1
                """, order["id"])

                user = await conn.fetchrow("""
                    SELECT telegram_id FROM users WHERE id=$1
                """, order["user_id"])

                await app.bot.send_message(
                    chat_id=user["telegram_id"],
                    text=f"⏳ Order ID {order['id']} bekor qilindi.\nTo‘lov muddati tugadi."
                )

        await asyncio.sleep(60)  # har 1 daqiqada tekshiradi
