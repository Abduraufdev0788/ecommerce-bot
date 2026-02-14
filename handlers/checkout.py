from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes, ConversationHandler
from database import db
from states import FULLNAME, PHONE, LOCATION, CONFIRM, QUANTITY_SELECT
from config import CARD_NUMBER, CARD_OWNER, ADMIN_ID


# =========================
# ENTRY POINTS
# =========================

async def start_checkout_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    context.user_data["checkout_type"] = "cart"

    await query.message.reply_text("👤 Ism familiyangizni kiriting:")
    return FULLNAME


async def start_checkout_single(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split(":")[1])

    context.user_data.clear()
    context.user_data["checkout_type"] = "single"
    context.user_data["product_id"] = product_id

    await query.message.reply_text("📦 Nechta olasiz?")
    return QUANTITY_SELECT

async def get_single_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        quantity = int(update.message.text)
    except:
        await update.message.reply_text("❗ Raqam kiriting.")
        return QUANTITY_SELECT

    if quantity <= 0:
        await update.message.reply_text("❗ 1 dan katta son kiriting.")
        return QUANTITY_SELECT

    product_id = context.user_data["product_id"]

    async with db.pool.acquire() as conn:
        product = await conn.fetchrow(
            "SELECT quantity FROM products WHERE id=$1",
            product_id
        )

    if not product:
        await update.message.reply_text("Mahsulot topilmadi.")
        return ConversationHandler.END

    if quantity > product["quantity"]:
        await update.message.reply_text(
            f"❗ Omborda faqat {product['quantity']} dona bor."
        )
        return QUANTITY_SELECT

    context.user_data["selected_quantity"] = quantity

    await update.message.reply_text("👤 Ism familiyangizni kiriting:")
    return FULLNAME



# =========================
# FULLNAME
# =========================

async def get_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["fullname"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:")
    return PHONE


# =========================
# PHONE
# =========================

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("📍 Lokatsiyangizni yuboring:")
    return LOCATION


# =========================
# LOCATION
# =========================

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.location:
        await update.message.reply_text("❗ Lokatsiya yuboring.")
        return LOCATION

    context.user_data["latitude"] = str(update.message.location.latitude)
    context.user_data["longitude"] = str(update.message.location.longitude)

    # SUMMARY
    summary_text = await build_summary(context, update.effective_user.id)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Tasdiqlash", callback_data="confirm_order")],
        [InlineKeyboardButton("✏️ Ismni o‘zgartirish", callback_data="edit_fullname")],
        [InlineKeyboardButton("✏️ Telefonni o‘zgartirish", callback_data="edit_phone")],
        [InlineKeyboardButton("✏️ Lokatsiyani o‘zgartirish", callback_data="edit_location")],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_order")]
    ])


    await update.message.reply_text(summary_text, reply_markup=keyboard)
    return CONFIRM


# =========================
# BUILD SUMMARY
# =========================

async def build_summary(context, telegram_id):
    async with db.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id FROM users WHERE telegram_id=$1",
            telegram_id
        )
        user_id = user["id"]

        total = 0
        items_text = ""

        if context.user_data["checkout_type"] == "cart":
            items = await conn.fetch("""
                SELECT p.name, p.price, c.count
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id=$1
            """, user_id)

        else:
            product_id = context.user_data["product_id"]
            items = await conn.fetch("""
                SELECT name, price, 1 as count
                FROM products
                WHERE id=$1
            """, product_id)

        for item in items:
            subtotal = item["price"] * item["count"]
            total += subtotal
            items_text += f"{item['name']} x {item['count']} = {subtotal}\n"

        context.user_data["total"] = total

    return (
        f"📦 Buyurtma:\n{items_text}\n"
        f"👤 {context.user_data['fullname']}\n"
        f"📞 {context.user_data['phone']}\n\n"
        f"💰 Umumiy: {total}\n\n"
        f"Tasdiqlaysizmi?"
    )


# =========================
# CONFIRM CALLBACK
# =========================

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    telegram_id = query.from_user.id

    async with db.pool.acquire() as conn:

        user = await conn.fetchrow(
            "SELECT id FROM users WHERE telegram_id=$1",
            telegram_id
        )
        user_id = user["id"]

        order = await conn.fetchrow("""
            INSERT INTO orders (
                user_id, total_price, fullname, phone,
                latitude, longitude
            )
            VALUES ($1,$2,$3,$4,$5,$6)
            RETURNING id
        """,
            user_id,
            context.user_data["total"],
            context.user_data["fullname"],
            context.user_data["phone"],
            context.user_data["latitude"],
            context.user_data["longitude"]
        )

        order_id = order["id"]

        # order items
        if context.user_data["checkout_type"] == "cart":

            items = await conn.fetch("""
                SELECT product_id, count
                FROM cart
                WHERE user_id=$1
            """, user_id)

            for item in items:
                await conn.execute("""
                    INSERT INTO order_items (order_id, product_id, count)
                    VALUES ($1,$2,$3)
                """, order_id, item["product_id"], item["count"])

            await conn.execute("DELETE FROM cart WHERE user_id=$1", user_id)

        else:
            await conn.execute("""
                INSERT INTO order_items (order_id, product_id, count)
                VALUES ($1,$2,$3)
            """, order_id, context.user_data["product_id"], context.user_data["quantity"])

    await query.message.reply_text(
        f"💳 To‘lov qiling:\n\n"
        f"Karta: {CARD_NUMBER}\n"
        f"Ism: {CARD_OWNER}\n\n"
        f"Order ID: {order_id}\n\n"
        f"To‘lovdan keyin screenshot yuboring."
    )

    return ConversationHandler.END


# =========================
# EDIT CALLBACK
# =========================

async def edit_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("✏️ Ism familiyangizni qayta kiriting:")
    return FULLNAME


# =========================
# CANCEL CALLBACK
# =========================

async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    await query.message.reply_text("❌ Buyurtma bekor qilindi.")
    return ConversationHandler.END


# =========================
# EDIT FULLNAME
# =========================

async def edit_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✏️ Yangi ism familiyangizni kiriting:")
    return FULLNAME


# =========================
# EDIT PHONE
# =========================

async def edit_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✏️ Yangi telefon raqamingizni kiriting:")
    return PHONE


# =========================
# EDIT LOCATION
# =========================

async def edit_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✏️ Yangi lokatsiyani yuboring:")
    return LOCATION

