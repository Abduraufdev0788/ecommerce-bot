from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from states import EDIT_CART_QTY
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
                    "✏️ Soni o‘zgartirish",
                    callback_data=f"edit_cart:{item['id']}"
                ),
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



async def edit_cart_quantity_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    cart_id = int(query.data.split(":")[1])
    context.user_data["edit_cart_id"] = cart_id

    await query.message.reply_text("✏️ Yangi sonni kiriting:")
    return EDIT_CART_QTY


async def update_cart_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_qty = int(update.message.text)
    except:
        await update.message.reply_text("❗ Raqam kiriting.")
        return EDIT_CART_QTY

    if new_qty <= 0:
        await update.message.reply_text("❗ 1 dan katta son kiriting.")
        return EDIT_CART_QTY

    cart_id = context.user_data["edit_cart_id"]

    async with db.pool.acquire() as conn:

        # mahsulotni topamiz
        cart_item = await conn.fetchrow("""
            SELECT product_id FROM cart WHERE id=$1
        """, cart_id)

        product = await conn.fetchrow("""
            SELECT quantity FROM products WHERE id=$1
        """, cart_item["product_id"])

        if new_qty > product["quantity"]:
            await update.message.reply_text(
                f"❗ Omborda faqat {product['quantity']} dona bor."
            )
            return EDIT_CART_QTY

        await conn.execute("""
            UPDATE cart
            SET count=$1
            WHERE id=$2
        """, new_qty, cart_id)

    await update.message.reply_text("✅ Savatcha yangilandi.")
    return ConversationHandler.END

