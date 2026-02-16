from telegram import Update
from telegram.ext import ContextTypes
from database import db


async def send_random_ad(update, context):

    async with db.pool.acquire() as conn:
        ad = await conn.fetchrow("""
            SELECT * FROM ads
            WHERE is_active=TRUE
            ORDER BY RANDOM()
            LIMIT 1
        """)

    if not ad:
        return

    if ad["image"]:
        await update.message.reply_photo(
            photo=ad["image"],
            caption=f"📢 Reklama\n\n{ad['text']}"
        )
    else:
        await update.message.reply_text(
            f"📢 Reklama\n\n{ad['text']}"
        )
