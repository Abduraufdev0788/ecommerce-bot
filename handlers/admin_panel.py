from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from config import ADMIN_ID


# =========================
# ADMIN PANEL ENTRY
# =========================

from telegram import ReplyKeyboardRemove

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    # 🔥 Oldingi reply keyboardni o‘chiramiz
    await update.message.reply_text(
        "🧑‍💼 Admin Panel",
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton("📦 Buyurtmalar", callback_data="admin_orders")],
        [InlineKeyboardButton("🛍 Mahsulotlar", callback_data="admin_products")],
        [InlineKeyboardButton("➕ Mahsulot qo‘shish", callback_data="admin_add_product")]
    ])

    await update.message.reply_text(
        "Dashboard:",
        reply_markup=keyboard
    )



async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with db.pool.acquire() as conn:

        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_products = await conn.fetchval("SELECT COUNT(*) FROM products")
        total_orders = await conn.fetchval("SELECT COUNT(*) FROM orders")
        total_income = await conn.fetchval("""
            SELECT COALESCE(SUM(total_price),0)
            FROM orders
            WHERE payment_status='paid'
        """)

    text = (
        "📊 Statistika\n\n"
        f"👤 Foydalanuvchilar: {total_users}\n"
        f"🛍 Mahsulotlar: {total_products}\n"
        f"📦 Buyurtmalar: {total_orders}\n"
        f"💰 Daromad: {total_income}"
    )

    await query.message.edit_text(text)


async def admin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with db.pool.acquire() as conn:
        orders = await conn.fetch("""
            SELECT id, total_price, status
            FROM orders
            ORDER BY id DESC
            LIMIT 10
        """)

    if not orders:
        await query.message.edit_text("Buyurtmalar yo‘q.")
        return

    text = "📦 Oxirgi 10 buyurtma:\n\n"

    for order in orders:
        text += (
            f"🆔 {order['id']} | "
            f"{order['total_price']} | "
            f"{order['status']}\n"
        )

    await query.message.edit_text(text)

async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    async with db.pool.acquire() as conn:
        products = await conn.fetch("""
            SELECT id, name, quantity
            FROM products
        """)

    if not products:
        await query.message.edit_text("Mahsulot yo‘q.")
        return

    text = "🛍 Mahsulotlar:\n\n"

    for product in products:
        text += (
            f"🆔 {product['id']} | "
            f"{product['name']} | "
            f"Qoldiq: {product['quantity']}\n"
        )

    await query.message.edit_text(text)
