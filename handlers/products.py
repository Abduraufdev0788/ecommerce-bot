from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from handlers.ads import send_random_ad


async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with db.pool.acquire() as conn:
        products = await conn.fetch("SELECT * FROM products")

    if not products:
        await update.message.reply_text("❗ Hozircha mahsulot yo‘q.")
        return

    for product in products:

        caption = (
            f"📦 {product['name']}\n"
            f"📝 {product['description']}\n"
            f"💰 Narxi: {product['price']}\n"
            f"📦 Qolgan: {product['quantity']}"
        )

        # 🔒 Stock protection
        if product["quantity"] > 0:
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🛒 Savatchaga qo‘shish",
                        callback_data=f"add:{product['id']}"
                    ),
                    InlineKeyboardButton(
                        "💳 Hozir sotib olish",
                        callback_data=f"buy:{product['id']}"
                    )
                ]
            ])
        else:
            caption += "\n\n❌ Sotuvda yo‘q"
            reply_markup = None  # 🔥 tugma chiqmaydi

        await update.message.reply_photo(
            photo=product["image"],
            caption=caption,
            reply_markup=reply_markup
        )
        await send_random_ad(update, context)




async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])
    telegram_id = query.from_user.id

    async with db.pool.acquire() as conn:

        user = await conn.fetchrow(
            "SELECT id FROM users WHERE telegram_id=$1",
            telegram_id
        )

        if not user:
            await query.message.reply_text("User topilmadi.")
            return

        user_id = user["id"]

        cart_item = await conn.fetchrow("""
            SELECT * FROM cart
            WHERE user_id=$1 AND product_id=$2
        """, user_id, product_id)

        if cart_item:
            await conn.execute("""
                UPDATE cart
                SET count = count + 1
                WHERE user_id=$1 AND product_id=$2
            """, user_id, product_id)
        else:
            await conn.execute("""
                INSERT INTO cart (user_id, product_id, count)
                VALUES ($1, $2, 1)
            """, user_id, product_id)

    await query.message.reply_text("🛒 Savatchaga qo‘shildi!")
