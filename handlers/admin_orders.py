from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import db
from config import ADMIN_ID


# =========================
# ORDERS MENU
# =========================

async def admin_orders_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Barcha", callback_data="orders_all")],
        [InlineKeyboardButton("⏳ Pending", callback_data="orders_pending")],
        [InlineKeyboardButton("✅ Tasdiqlangan", callback_data="orders_confirmed")],
        [InlineKeyboardButton("❌ Bekor qilingan", callback_data="orders_cancelled")],
        [InlineKeyboardButton("📅 Bugungi", callback_data="orders_today")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_back")]
    ])

    await query.message.edit_text(
        "📦 Buyurtmalar boshqaruvi",
        reply_markup=keyboard
    )

async def admin_orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filter_type = query.data.split("_")[1]

    sql = "SELECT id, total_price, status, created_at FROM orders"
    params = []

    if filter_type == "pending":
        sql += " WHERE payment_status='pending'"
    elif filter_type == "confirmed":
        sql += " WHERE status='confirmed'"
    elif filter_type == "cancelled":
        sql += " WHERE status='cancelled'"
    elif filter_type == "today":
        sql += " WHERE DATE(created_at) = CURRENT_DATE"

    sql += " ORDER BY id DESC LIMIT 20"

    async with db.pool.acquire() as conn:
        orders = await conn.fetch(sql, *params)

    if not orders:
        await query.message.edit_text("Buyurtma topilmadi.")
        return

    text = "📦 Buyurtmalar:\n\n"

    keyboard = []

    for order in orders:
        text += (
            f"🆔 {order['id']} | "
            f"{order['total_price']} | "
            f"{order['status']}\n"
        )

        keyboard.append([
            InlineKeyboardButton(
                f"Order {order['id']} batafsil",
                callback_data=f"order_detail_admin:{order['id']}"
            )
        ])

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="admin_orders")])

    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def admin_order_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split(":")[1])

    async with db.pool.acquire() as conn:

        order = await conn.fetchrow("""
            SELECT o.*, u.telegram_id
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id=$1
        """, order_id)

        items = await conn.fetch("""
            SELECT p.name, p.price, oi.count
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id=$1
        """, order_id)

    text = (
        f"🆔 Order ID: {order_id}\n"
        f"👤 User: {order['telegram_id']}\n"
        f"💰 Summa: {order['total_price']}\n"
        f"📌 Status: {order['status']}\n"
        f"💳 To‘lov: {order['payment_status']}\n"
        f"🕒 Sana: {order['created_at']}\n\n"
        f"📦 Mahsulotlar:\n"
    )

    for item in items:
        text += f"{item['name']} x {item['count']}\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Orqaga", callback_data="admin_orders")]
    ])

    await query.message.edit_text(text, reply_markup=keyboard)
