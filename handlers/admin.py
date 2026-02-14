from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)

from database import db
from config import ADMIN_ID
from states import NAME, DESCRIPTION, PRICE, QUANTITY, IMAGE


# 🔒 Admin tekshirish
def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Siz admin emassiz.")
            return ConversationHandler.END
        return await func(update, context)
    return wrapper


# 1️⃣ Start
@admin_only
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📦 Mahsulot nomini kiriting:")
    return NAME


# 2️⃣ Name
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📝 Description kiriting:")
    return DESCRIPTION


# 3️⃣ Description
async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["description"] = update.message.text
    await update.message.reply_text("💰 Narxini kiriting:")
    return PRICE


# 4️⃣ Price
async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["price"] = float(update.message.text)
    except:
        await update.message.reply_text("❗ Iltimos to‘g‘ri narx kiriting.")
        return PRICE

    await update.message.reply_text("📦 Soni (quantity) kiriting:")
    return QUANTITY


# 5️⃣ Quantity
async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["quantity"] = int(update.message.text)
    except:
        await update.message.reply_text("❗ Iltimos butun son kiriting.")
        return QUANTITY

    await update.message.reply_text("📸 Mahsulot rasmini yuboring:")
    return IMAGE


# 6️⃣ Image
async def get_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❗ Rasm yuboring.")
        return IMAGE

    photo_id = update.message.photo[-1].file_id

    async with db.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO products (name, description, price, quantity, image)
            VALUES ($1, $2, $3, $4, $5)
        """,
        context.user_data["name"],
        context.user_data["description"],
        context.user_data["price"],
        context.user_data["quantity"],
        photo_id
        )

    await update.message.reply_text("✅ Mahsulot muvaffaqiyatli qo‘shildi!")
    return ConversationHandler.END


# ❌ Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END
